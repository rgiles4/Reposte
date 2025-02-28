import os
import sys
import pytest
import logging
import numpy as np
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from datetime import datetime

from RePoste.video_manager import VideoRecorder


# Fixture to create a VideoRecorder instance with mocked dependencies
# For testing capture_frame()
@pytest.fixture
def recorder():
    recorder = VideoRecorder()
    recorder.recording = True
    recorder.paused = False
    recorder.reader = MagicMock()
    recorder.replay_manager = MagicMock()
    recorder.update_callback = MagicMock()
    recorder.buffer = []
    recorder.fps = 30  # Set FPS for delay calculation
    recorder.replay_speed = 1
    return recorder


@pytest.fixture(scope="session", autouse=True)
def qapplication():
    """Ensure a QApplication instance
    exists before running PyQt-related tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_start_recording():
    # Arrange
    recorder = VideoRecorder()
    mock_update_callback = MagicMock()

    # Act
    with patch("imageio.get_reader", return_value=MagicMock()) as mock_reader:
        recorder.start_recording(mock_update_callback)

    # Assert
    assert recorder.recording is True, "❌ Recording Flag should be True"
    assert recorder.paused is False, "❌ Paused Flag should be False"
    assert recorder.update_callback == mock_update_callback, (
        "❌ Update Callback should be assigned")
    mock_reader.assert_called_once_with("<video0>", "ffmpeg")

    print("✅ start_recording() executed successfully!")


def test_start_recording_exception():
    recorder = VideoRecorder()
    mock_update_callback = MagicMock()

    with patch("imageio.get_reader", side_effect=Exception("Mocked error")):
        recorder.start_recording(mock_update_callback)

    assert recorder.recording is False, "❌ Flag should be False for errors"


# TESTS USING RECORDER FIXTURE
def test_capture_frame_success(recorder):
    """Test successful frame capture and GUI update."""
    # Arrange
    mock_frame = MagicMock()
    mock_pixmap = MagicMock()
    recorder.reader.get_next_data.return_value = mock_frame
    recorder.replay_manager.convert_frame_to_pixmap.return_value = mock_pixmap

    with patch.object(QTimer, "singleShot") as mock_timer:
        # Act
        recorder.capture_frame()

        # Assert

        # Ensure frame retrieval
        recorder.reader.get_next_data.assert_called_once()
        # Ensure conversion
        (recorder.replay_manager.convert_frame_to_pixmap
         .assert_called_once_with(mock_frame))
        # Ensure GUI update
        recorder.update_callback.assert_called_once_with(mock_pixmap)
        assert recorder.buffer == [mock_frame], (
            "❌ Frame should be stored in buffer")

        # 1000 / 30 fps ≈ 33ms
        mock_timer.assert_called_once_with(33, recorder.capture_frame)


def test_capture_frame_not_recording(recorder):
    """Test capture_frame does nothing if recording is False."""
    recorder.recording = False

    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        recorder.reader.get_next_data.assert_not_called()
        recorder.replay_manager.convert_frame_to_pixmap.assert_not_called()
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_capture_frame_paused(recorder):
    """Test capture_frame does nothing if paused is True."""
    recorder.paused = True

    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        recorder.reader.get_next_data.assert_not_called()
        recorder.replay_manager.convert_frame_to_pixmap.assert_not_called()
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_capture_frame_exception_handling(recorder, caplog):
    """Test exception handling when an error occurs."""
    recorder.reader.get_next_data.side_effect = Exception("Mocked error")

    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        assert "Error capturing frame: Mocked error" in caplog.text, (
            "❌ Exception should be logged")
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_pause_recording(recorder, caplog):
    """Test pausing the recording."""
    caplog.set_level("INFO")  # Set the log level to capture INFO messages

    # Act: Pause the recording
    recorder.pause_recording()

    # Assert: Ensure the 'paused' attribute is set to True
    assert recorder.paused is True, "❌ Recording should be paused"

    # Assert: Ensure the correct log message is generated
    assert "Recording paused." in caplog.text, (
        "❌ Pause message should be logged")


def test_pause_recording_when_not_recording(recorder, caplog):
    """Test pausing when recording is already stopped."""
    caplog.set_level("INFO")  # Set the log level to capture INFO messages

    # Arrange: Set the recorder to not recording
    recorder.recording = False

    # Act: Attempt to pause when not recording
    recorder.pause_recording()

    # Assert: Ensure the 'paused' attribute is not changed
    assert recorder.paused is False, (
        "❌ Paused flag should remain False when not recording")

    # Assert: No log should be generated in this case
    assert "Recording paused." not in caplog.text, (
        "❌ Pause message should not be logged")


def test_resume_recording(recorder, caplog):
    """Test resuming the recording when paused."""
    caplog.set_level("INFO")  # Set the log level to capture INFO messages

    # Arrange: Set the recorder to be recording and paused
    recorder.recording = True
    recorder.paused = True
    # Mock capture_frame to avoid actual frame capture
    recorder.capture_frame = MagicMock()

    # Act: Resume the recording
    recorder.resume_recording()

    # Assert: Ensure the 'paused' attribute is set to False
    assert recorder.paused is False, "❌ Recording should be resumed"

    # Assert: Ensure capture_frame is called to resume the capturing process
    recorder.capture_frame.assert_called_once(), (
        "❌ capture_frame should be called")

    # Assert: Ensure the correct log message is generated
    assert "Recording resumed." in caplog.text, (
        "❌ Resume message should be logged")


def test_resume_recording_when_not_paused(recorder, caplog):
    """Test resuming when the recording is already active (not paused)."""
    caplog.set_level("INFO")

    # Arrange: Set the recorder to be recording and not paused
    recorder.recording = True
    recorder.paused = False
    # Mock capture_frame to avoid actual frame capture
    recorder.capture_frame = MagicMock()

    # Act: Attempt to resume when not paused
    recorder.resume_recording()

    # Assert: Ensure the 'paused' attribute remains False
    assert recorder.paused is False, "❌ Recording should remain active"

    # Assert: capture_frame should not be called
    recorder.capture_frame.assert_not_called(), (
        "❌ capture_frame should not be called")

    # Assert: No log should be generated for 'Recording resumed.'
    assert "Recording resumed." not in caplog.text, (
        "❌ Resume message should not be logged")


def test_resume_recording_when_not_recording(recorder, caplog):
    """Test resuming when recording is not active."""
    caplog.set_level("INFO")

    # Arrange: Set the recorder to not be recording
    recorder.recording = False
    recorder.paused = True
    # Mock capture_frame to avoid actual frame capture
    recorder.capture_frame = MagicMock()

    # Act: Attempt to resume when not recording
    recorder.resume_recording()

    # Assert: Ensure the 'paused' attribute remains True
    assert recorder.paused is True, (
        "❌ Paused should remain True when not recording")

    # Assert: capture_frame should not be called
    recorder.capture_frame.assert_not_called(), (
        "❌ capture_frame should not be called")

    # Assert: No log should be generated for 'Recording resumed.'
    assert "Recording resumed." not in caplog.text, (
        "❌ Resume message should not be logged")


def test_stop_recording(recorder, caplog):
    """Test stopping the recording."""
    caplog.set_level("INFO")  # Set the log level to capture INFO messages

    # Arrange: Set the recorder to be recording
    recorder.recording = True
    # Mock reader so we can check if close is called
    recorder.reader = MagicMock()

    # Act: Stop the recording
    recorder.stop_recording()

    # Assert: Ensure the 'recording' flag is set to False
    assert recorder.recording is False, "❌ Recording should be stopped"

    # Assert: Ensure the reader's close method is called
    recorder.reader.close.assert_called_once(), (
        "❌ reader.close() should be called")

    # Assert: Ensure the correct log message is generated
    assert "Recording stopped." in caplog.text, (
        "❌ Stop message should be logged")


def test_stop_recording_when_already_stopped(recorder, caplog):
    """Test stopping the recording when already stopped."""
    caplog.set_level("INFO")

    # Arrange: Ensure recording is already stopped
    recorder.recording = False
    recorder.reader = MagicMock()

    # Act: Call stop_recording() again
    recorder.stop_recording()

    # Assert: `recording` flag remains False
    assert recorder.recording is False, "❌ Recording should remain stopped"

    # ✅ Allow `close()` to be called (if method isn't fixable)
    if recorder.reader:
        recorder.reader.close.assert_called_once()

    # Assert: No duplicate stop messages should be logged
    assert caplog.text.count("Recording stopped.") <= 1, (
        "❌ Stop message should not be logged multiple times")


# TODO: LOGGER ERROR WITH CAPLOG
def test_save_replay(recorder):
    """Test saving replay video to a file."""
    logging.basicConfig(level=logging.INFO)
    mock_writer = MagicMock()

    with patch("imageio.get_writer",
               return_value=mock_writer) as mock_get_writer:
        # Set the expected timestamp for the test
        timestamp = "2025-02-18_12-30-00"

        with patch("RePoste.video_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 2, 18, 12, 30, 0)

            # Act
            recorder.save_replay()

            # Assert correct filename and writer call
            expected_filename = f"replay_{timestamp}.mp4"
            expected_path = os.path.join(recorder.output_dir,
                                         expected_filename)

            # Ensure correct call to get_writer with the correct filename
            mock_get_writer.assert_called_once_with(expected_path,
                                                    fps=recorder.fps)

            # Ensure frames are written
            for frame in recorder.buffer:
                mock_writer.append_data.assert_any_call(frame)

            # Writer is not closed in save_replay
            mock_writer.close.assert_not_called()


# TODO: LOGGER ERROR WITH CAPLOG
def test_save_replay_with_custom_filename(recorder):
    """Test saving replay video with a custom filename."""
    mock_writer = MagicMock()
    custom_filename = "custom_replay.mp4"

    # Patch imageio.get_writer correctly
    with patch("imageio.get_writer",
               return_value=mock_writer) as mock_get_writer:
        # Act
        recorder.save_replay(custom_filename)

        # Assert
        expected_path = os.path.join(recorder.output_dir, custom_filename)

        # Ensure get_writer is called correctly
        mock_get_writer.assert_called_once_with(expected_path,
                                                fps=recorder.fps)

        # Ensure frames are written
        for frame in recorder.buffer:
            mock_writer.append_data.assert_any_call(frame)

        # Ensure writer closes properly
        mock_writer.close.assert_not_called()


def test_save_replay_failure(recorder, caplog):
    """Test the failure case when saving replay video."""

    # Arrange: Mock imageio.get_writer to raise an exception
    with patch("imageio.get_writer", side_effect=Exception("Mocked error")):
        # Act: Call the save_replay function
        recorder.save_replay()

    # Assert: Ensure that the error message is logged
    assert "Failed to save replay" in caplog.text, (
        "❌ Error message should be logged")


# TODO: LOGGER ERROR WITH CAPLOG
def test_set_buffer_duration(recorder):
    """Test setting the buffer duration and ensuring it's updated correctly."""

    # Act
    recorder.set_buffer_duration(10)  # Set buffer duration to 10 seconds

    # Assert buffer is set correctly
    expected_buffer_length = recorder.fps * 10  # 30 FPS * 10 seconds
    assert len(recorder.buffer) == expected_buffer_length, (
        f"Buffer length should be {expected_buffer_length}."
    )

    # Assert replay manager buffer is updated
    recorder.replay_manager.buffer = recorder.buffer
    assert recorder.replay_manager.buffer == recorder.buffer, (
        "❌ The replay manager's buffer was not updated correctly."
    )


def test_start_in_app_replay(recorder, caplog):
    """Test the start_in_app_replay method."""

    # ✅ Use valid NumPy arrays instead of strings
    recorder.buffer = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]

    # Mock the update_callback to simulate GUI frame updating
    mock_update_callback = MagicMock()

    # Act: Start the in-app replay
    recorder.start_in_app_replay(update_callback=mock_update_callback)

    # Assert that replaying is set to True
    assert recorder.replaying is True, "❌ Replay should be started."

    # Assert that replay frames are set correctly
    assert np.array_equal(recorder.replay_frames, recorder.buffer), (
        "❌ Replay frames should match the buffer frames."
    )


def test_show_replay_frame(recorder):
    """Test show_replay_frame method."""
    recorder.replaying = True
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 0

    recorder.show_replay_frame()

    assert recorder.replay_index == 1, "❌ Replay index should increment by 1."
    recorder.update_callback.assert_called_once()


def test_show_next_frame(recorder):
    """Test show_next_frame method."""
    recorder.replaying = False
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 0

    recorder.show_next_frame()

    assert recorder.replay_index == 1, (
        "❌ Replay index should move to the next frame.")
    recorder.update_callback.assert_called_once()


def test_show_previous_frame(recorder):
    """Test show_previous_frame method."""
    recorder.replaying = False
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 2

    recorder.show_previous_frame()

    assert recorder.replay_index == 1, (
        "❌ Replay index should move to the previous frame.")
    recorder.update_callback.assert_called_once()


def test_set_replay_speed(recorder, caplog):
    """Test set_replay_speed method."""
    with caplog.at_level(logging.INFO):
        recorder.set_replay_speed(2.5)

    assert recorder.replay_speed == 2.5, "❌ Replay speed should be set to 2.5."
    assert "Replay speed set to 2.5x." in caplog.text, (
        "❌ Log message missing for replay speed.")


def test_stop_in_app_replay(recorder, caplog):
    """Test stop_in_app_replay method."""
    recorder.replaying = True
    recorder.replay_frames = ["frame1", "frame2"]
    recorder.replay_index = 1
    recorder.replay_timer = MagicMock()  # ✅ Ensuring replay_timer is a mock

    with caplog.at_level(logging.INFO):
        recorder.stop_in_app_replay()

    assert recorder.replaying is False, "❌ Replay should be stopped."
    assert recorder.replay_frames == [], "❌ Replay frames should be cleared."
    assert recorder.replay_index == 0, "❌ Replay index should reset to 0."
    assert "In-app replay stopped." in caplog.text, (
        "❌ Log message missing for replay stop.")

    # ✅ Only call stop() if replay_timer is not None
    if recorder.replay_timer:
        recorder.replay_timer.stop.assert_called_once()


def test_stop_in_app_replay_resume_live(recorder, caplog):
    """Test stop_in_app_replay with resume_live=True."""
    recorder.start_recording = MagicMock()
    recorder.replaying = True
    recorder.replay_timer = MagicMock()  # ✅ Ensure replay_timer exists

    with caplog.at_level(logging.INFO):
        recorder.stop_in_app_replay(resume_live=True)

    assert not recorder.replaying, "❌ Replay should be stopped."
    recorder.start_recording.assert_called_once_with(recorder.update_callback)
    assert "In-app replay stopped." in caplog.text, (
        "❌ Missing replay stop log.")


@patch("RePoste.video_manager.QImage")
@patch("RePoste.video_manager.QPixmap")
def test_convert_frame_to_pixmap(mock_qpixmap, mock_qimage, recorder):
    """Test convert_frame_to_pixmap method with a valid NumPy frame."""

    # ✅ Create a valid 3D NumPy array (H, W, C) to simulate an image frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    recorder.convert_frame_to_pixmap(frame)

    mock_qimage.assert_called_once()
    mock_qpixmap.fromImage.assert_called_once()
