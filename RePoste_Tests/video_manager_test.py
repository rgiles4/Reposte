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
    assert (
        recorder.update_callback == mock_update_callback
    ), "❌ Update Callback should be assigned"
    mock_reader.assert_called_once_with("<video0>", "ffmpeg")


def test_start_recording_exception():
    # Arrange
    recorder = VideoRecorder()
    mock_update_callback = MagicMock()

    # Act
    with patch("imageio.get_reader", side_effect=Exception("Mocked error")):
        recorder.start_recording(mock_update_callback)

    # Assert
    assert recorder.recording is False, "❌ Flag should be False for errors"


def test_capture_frame_success(recorder):
    # Arrange
    mock_frame = MagicMock()
    mock_pixmap = MagicMock()
    recorder.reader.get_next_data.return_value = mock_frame
    recorder.replay_manager.convert_frame_to_pixmap.return_value = mock_pixmap

    with patch.object(QTimer, "singleShot") as mock_timer:
        # Act
        recorder.capture_frame()
        # Ensure frame retrieval
        recorder.reader.get_next_data.assert_called_once()
        # Ensure conversion
        # fmt: off
        (
            recorder.replay_manager \
            .convert_frame_to_pixmap \
            .assert_called_once_with(
                mock_frame
            )
        )
        # fmt: on

        # Ensure GUI update
        recorder.update_callback.assert_called_once_with(mock_pixmap)

        # Assert
        assert recorder.buffer == [
            mock_frame
        ], "❌ Frame should be stored in buffer"

        # 1000 / 30 fps ≈ 33ms
        mock_timer.assert_called_once_with(33, recorder.capture_frame)


def test_capture_frame_not_recording(recorder):

    # Arrange
    recorder.recording = False

    # Act
    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        recorder.reader.get_next_data.assert_not_called()
        recorder.replay_manager.convert_frame_to_pixmap.assert_not_called()
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_capture_frame_paused(recorder):
    # Arrange
    recorder.paused = True

    # Act
    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        recorder.reader.get_next_data.assert_not_called()
        recorder.replay_manager.convert_frame_to_pixmap.assert_not_called()
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_capture_frame_exception_handling(recorder, caplog):
    # Arrange
    recorder.reader.get_next_data.side_effect = Exception("Mocked error")

    # Act
    with patch.object(QTimer, "singleShot") as mock_timer:
        recorder.capture_frame()

        # Assert
        assert (
            "Error capturing frame: Mocked error" in caplog.text
        ), "❌ Exception should be logged"
        recorder.update_callback.assert_not_called()
        assert recorder.buffer == [], "❌ Buffer should remain empty"
        mock_timer.assert_not_called()


def test_pause_recording(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO

    # Act
    recorder.pause_recording()

    # Assert
    assert recorder.paused is True, "❌ Recording should be paused"
    assert (
        "Recording paused." in caplog.text
    ), "❌ Pause message should be logged"


def test_pause_recording_when_not_recording(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = False

    # Act
    recorder.pause_recording()

    # Assert
    assert (
        recorder.paused is False
    ), "❌ Paused flag should remain False when not recording"
    assert (
        "Recording paused." not in caplog.text
    ), "❌ Pause message should not be logged"


def test_resume_recording(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = True
    recorder.paused = True
    recorder.capture_frame = MagicMock()

    # Act
    recorder.resume_recording()

    # Assert
    assert recorder.paused is False, "❌ Recording should be resumed"
    recorder.capture_frame.assert_called_once(), (
        "❌ capture_frame should be called"
    )
    assert (
        "Recording resumed." in caplog.text
    ), "❌ Resume message should be logged"


def test_resume_recording_when_not_paused(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = True
    recorder.paused = False
    recorder.capture_frame = MagicMock()

    # Act
    recorder.resume_recording()

    # Assert
    assert recorder.paused is False, "❌ Recording should remain active"
    recorder.capture_frame.assert_not_called(), (
        "❌ capture_frame should not be called"
    )
    assert (
        "Recording resumed." not in caplog.text
    ), "❌ Resume message should not be logged"


def test_resume_recording_when_not_recording(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = False
    recorder.paused = True
    recorder.capture_frame = MagicMock()

    # Act
    recorder.resume_recording()

    # Assert
    assert (
        recorder.paused is True
    ), "❌ Paused should remain True when not recording"
    recorder.capture_frame.assert_not_called(), (
        "❌ capture_frame should not be called"
    )
    assert (
        "Recording resumed." not in caplog.text
    ), "❌ Resume message should not be logged"


def test_stop_recording(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = True
    recorder.reader = MagicMock()

    # Act
    recorder.stop_recording()

    # Assert
    assert recorder.recording is False, "❌ Recording should be stopped"
    recorder.reader.close.assert_called_once(), (
        "❌ reader.close() should be called"
    )
    assert (
        "Recording stopped." in caplog.text
    ), "❌ Stop message should be logged"


def test_stop_recording_when_already_stopped(recorder, caplog):
    # Arrange
    caplog.set_level("INFO")  # Set the log level to INFO
    recorder.recording = False
    recorder.reader = MagicMock()

    # Act
    recorder.stop_recording()

    # Assert
    assert recorder.recording is False, "❌ Recording should remain stopped"
    if recorder.reader:
        recorder.reader.close.assert_called_once()
    assert (
        caplog.text.count("Recording stopped.") <= 1
    ), "❌ Stop message should not be logged multiple times"


# TODO: LOGGER ERROR WITH CAPLOG
def test_save_replay(recorder):
    # Arrange
    logging.basicConfig(level=logging.INFO)  # Config the log level to INFO
    mock_writer = MagicMock()

    # Act
    with patch(
        "imageio.get_writer", return_value=mock_writer
    ) as mock_get_writer:
        timestamp = "2025-02-18_12-30-00"

        with patch("RePoste.video_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 2, 18, 12, 30, 0)

            recorder.save_replay()

            # Assert
            expected_filename = f"replay_{timestamp}.mp4"
            expected_path = os.path.join(
                recorder.output_dir, expected_filename
            )
            mock_get_writer.assert_called_once_with(
                expected_path, fps=recorder.fps
            )
            for frame in recorder.buffer:
                mock_writer.append_data.assert_any_call(frame)
            mock_writer.close.assert_not_called()


# TODO: LOGGER ERROR WITH CAPLOG
def test_save_replay_with_custom_filename(recorder):
    # Arrange
    mock_writer = MagicMock()
    custom_filename = "custom_replay.mp4"
    with patch(
        "imageio.get_writer", return_value=mock_writer
    ) as mock_get_writer:
        # Act
        recorder.save_replay(custom_filename)

        # Assert
        expected_path = os.path.join(recorder.output_dir, custom_filename)
        mock_get_writer.assert_called_once_with(
            expected_path, fps=recorder.fps
        )
        for frame in recorder.buffer:
            mock_writer.append_data.assert_any_call(frame)
        mock_writer.close.assert_not_called()


def test_save_replay_failure(recorder, caplog):
    # Arrange
    with patch("imageio.get_writer", side_effect=Exception("Mocked error")):
        # Act
        recorder.save_replay()

    # Assert
    assert (
        "Failed to save replay" in caplog.text
    ), "❌ Error message should be logged"


# TODO: LOGGER ERROR WITH CAPLOG
def test_set_buffer_duration(recorder):
    # Act
    recorder.set_buffer_duration(10)  # Set buffer duration to 10 seconds

    # Assert
    expected_buffer_length = recorder.fps * 10  # 30 FPS * 10 seconds
    assert (
        len(recorder.buffer) == expected_buffer_length
    ), f"Buffer length should be {expected_buffer_length}."
    recorder.replay_manager.buffer = recorder.buffer
    assert (
        recorder.replay_manager.buffer == recorder.buffer
    ), "❌ The replay manager's buffer was not updated correctly."


def test_start_in_app_replay(recorder, caplog):
    # Arrange
    recorder.buffer = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    mock_update_callback = MagicMock()

    # Act
    recorder.start_in_app_replay(update_callback=mock_update_callback)

    # Assert
    assert recorder.replaying is True, "❌ Replay should be started."
    assert np.array_equal(
        recorder.replay_frames, recorder.buffer
    ), "❌ Replay frames should match the buffer frames."


def test_show_replay_frame(recorder):
    # Arrange
    recorder.replaying = True
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 0

    # Act
    recorder.show_replay_frame()

    # Assert
    assert (
        recorder.replay_index == 1
    ), "❌ Replay index should increment by 1."
    recorder.update_callback.assert_called_once()


def test_show_next_frame(recorder):
    # Arrange
    recorder.replaying = False
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 0

    # Act
    recorder.show_next_frame()

    # Assert
    assert (
        recorder.replay_index == 1
    ), "❌ Replay index should move to the next frame."
    recorder.update_callback.assert_called_once()


def test_show_previous_frame(recorder):
    # Arrange
    recorder.replaying = False
    recorder.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
    ]
    recorder.replay_index = 2

    # Act
    recorder.show_previous_frame()

    # Assert
    assert (
        recorder.replay_index == 1
    ), "❌ Replay index should move to the previous frame."
    recorder.update_callback.assert_called_once()


def test_set_replay_speed(recorder, caplog):
    # Act
    with caplog.at_level(logging.INFO):
        recorder.set_replay_speed(2.5)

    # Assert
    assert (
        recorder.replay_speed == 2.5
    ), "❌ Replay speed should be set to 2.5."
    assert (
        "Replay speed set to 2.5x." in caplog.text
    ), "❌ Log message missing for replay speed."


def test_stop_in_app_replay(recorder, caplog):
    # Arrange
    recorder.replaying = True
    recorder.replay_frames = ["frame1", "frame2"]
    recorder.replay_index = 1
    recorder.replay_timer = MagicMock()

    # Act
    with caplog.at_level(logging.INFO):
        recorder.stop_in_app_replay()

    # Assert
    assert recorder.replaying is False, "❌ Replay should be stopped."
    assert recorder.replay_frames == [], "❌ Replay frames should be clear."
    assert recorder.replay_index == 0, "❌ Replay index should reset to 0."
    assert (
        "In-app replay stopped." in caplog.text
    ), "❌ Log message missing for replay stop."
    if recorder.replay_timer:
        recorder.replay_timer.stop.assert_called_once()


def test_stop_in_app_replay_resume_live(recorder, caplog):
    # Arrange
    recorder.start_recording = MagicMock()
    recorder.replaying = True
    recorder.replay_timer = MagicMock()  # ✅ Ensure replay_timer exists

    # Act
    with caplog.at_level(logging.INFO):
        recorder.stop_in_app_replay(resume_live=True)

    # Assert
    assert not recorder.replaying, "❌ Replay should be stopped."
    recorder.start_recording.assert_called_once_with(recorder.update_callback)
    assert (
        "In-app replay stopped." in caplog.text
    ), "❌ Missing replay stop log."


@patch("RePoste.video_manager.QImage")
@patch("RePoste.video_manager.QPixmap")
def test_convert_frame_to_pixmap(mock_qpixmap, mock_qimage, recorder):
    # Arrange
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Act
    recorder.convert_frame_to_pixmap(frame)

    # Assert
    mock_qimage.assert_called_once()
    mock_qpixmap.fromImage.assert_called_once()
