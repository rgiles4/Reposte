import pytest
import numpy as np
import os
from collections import deque
from PyQt6.QtGui import QPixmap
from unittest.mock import MagicMock
from RePoste.replay_manager import ReplayManager


@pytest.fixture(scope="session")
def qapp():
    """Provides a QApplication instance for tests."""
    from PyQt6.QtWidgets import QApplication

    return QApplication([])


@pytest.fixture
def sample_buffer():
    return deque(
        [
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            for _ in range(5)
        ]
    )


@pytest.fixture
def output_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def replay_manager(sample_buffer, output_dir):
    return ReplayManager(fps=30, buffer=sample_buffer, output_dir=output_dir)


def test_initialization(replay_manager, sample_buffer, output_dir):
    assert replay_manager.fps == 30
    assert replay_manager.buffer == sample_buffer
    assert replay_manager.output_dir == output_dir
    assert not replay_manager.replaying


def test_start_in_app_replay(qtbot, replay_manager):
    replay_manager.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for _ in range(5)
    ]
    replay_manager.buffer = replay_manager.replay_frames.copy()

    mock_callback = MagicMock()
    replay_manager.start_in_app_replay(update_callback=mock_callback)

    qtbot.wait(100)  # Short delay to allow execution

    assert replay_manager.replaying
    assert replay_manager.replay_index == 3
    assert len(replay_manager.replay_frames) == len(replay_manager.buffer)
    mock_callback.assert_called()  # Ensure the callback was triggered


def test_stop_in_app_replay(replay_manager):
    # Arrange
    replay_manager.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for _ in range(3)
    ]
    replay_manager.buffer = replay_manager.replay_frames.copy()

    # Act
    # Start Replay
    try:
        replay_manager.start_in_app_replay()
    except Exception as e:
        pytest.fail(
            f"start_in_app_replay() raised an unexpected exception: {e}"
        )

    # Stop Replay
    try:
        replay_manager.stop_in_app_replay()
    except Exception as e:
        pytest.fail(
            f"stop_in_app_replay() raised an unexpected exception: {e}"
        )

    # Assert
    assert replay_manager.replaying is False, "Replaying flag should be False"
    assert isinstance(
        replay_manager.replay_frames, list
    ), "replay_frames should be a list"
    assert (
        replay_manager.replay_frames == []
    ), "replay_frames should be empty after stopping"
    assert (
        replay_manager.replay_index == 0
    ), "replay_index should be reset to 0"


def test_set_replay_speed(replay_manager):
    # Act
    replay_manager.set_replay_speed(2.0)

    # Assert
    assert replay_manager.replay_speed == 2.0


def test_show_next_frame(replay_manager):
    # Arrange
    replay_manager.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for _ in range(5)
    ]
    replay_manager.buffer = replay_manager.replay_frames.copy()
    replay_manager.start_in_app_replay()
    initial_index = replay_manager.replay_index

    # Act
    replay_manager.show_next_frame()

    # Assert
    assert replay_manager.replay_index == min(
        initial_index + 1, len(replay_manager.replay_frames) - 1
    )


def test_show_previous_frame(replay_manager):
    # Arrange
    replay_manager.replay_frames = [
        np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for _ in range(3)
    ]
    replay_manager.buffer = replay_manager.replay_frames.copy()
    replay_manager.start_in_app_replay()
    replay_manager.replay_index = 2

    # Act
    replay_manager.show_previous_frame()

    # Assert
    assert replay_manager.replay_index == 1


def test_save_replay(replay_manager):
    # Arrange
    filename = "test_replay.mp4"

    # Act
    replay_manager.save_replay(filename)
    output_path = os.path.join(replay_manager.output_dir, filename)

    # Assert
    assert os.path.exists(output_path)


def test_convert_frame_to_pixmap(qapp, replay_manager, sample_buffer):
    # Act
    frame = sample_buffer[0]
    pixmap = replay_manager.convert_frame_to_pixmap(frame)

    # Assert
    assert isinstance(pixmap, QPixmap)
