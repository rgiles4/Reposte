import pytest

# Import required library classes
from unittest.mock import MagicMock
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Import gui.py class
from RePoste.gui import MainWindow


# Create QApplication
@pytest.fixture(scope="module")
def create_app():
    return QApplication([])


def test_frame_update(create_app):
    # Arrange
    window = MainWindow()

    # Mock QPixmap
    mock_pixmap = MagicMock(spec=QPixmap)
    mock_pixmap.width.return_value = 1920
    mock_pixmap.height.return_value = 1080

    window.video_feed.setPixmap = MagicMock()

    # Act
    window.update_frame(mock_pixmap)

    # Assert
    window.video_feed.setPixmap.assert_called_once()
    scaled_pixmap = window.video_feed.setPixmap.call_args[0][0]

    assert scaled_pixmap.width() > 0, (
        f"❌ Scaled pixmap has invalid width: {scaled_pixmap.width()}")
    assert scaled_pixmap.height() > 0 (
        f"❌ Scaled pixmap has invalid height: {scaled_pixmap.height()}")

    print("✅ update_frame() successfully updated the video feed!")


# Parameters for test_keyPressEvent
@pytest.mark.parametrize(
    "key, method",
    [
        (Qt.Key.Key_Escape, "stop_recording"),
        (Qt.Key.Key_Space, "save_replay"),
        (Qt.Key.Key_P, "pause_recording"),
        (Qt.Key.Key_R, "resume_recording"),
        (Qt.Key.Key_Up, "start_in_app_replay"),
        (Qt.Key.Key_Down, "stop_in_app_replay"),
        (Qt.Key.Key_Left, "show_previous_frame"),
        (Qt.Key.Key_Right, "show_next_frame"),
    ],
)
def test_keyPressEvent(key, method):
    # Arrange
    window = MainWindow()
    window.recorder = MagicMock()

    # QKeyEvent for Key Press
    event = QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier)

    # Act
    window.keyPressEvent(event)

    # Assert
    getattr(window.recorder, method).assert_called_once()

    print("✅ keyPressEvent() successfully called all methods!")


# Parameters for set_replay_speed
@pytest.mark.parametrize(
    "key, expected_speed",
    [
        (Qt.Key.Key_0, 1.0),
        (Qt.Key.Key_1, 0.1),
        (Qt.Key.Key_2, 0.2),
        (Qt.Key.Key_3, 0.3),
        (Qt.Key.Key_4, 0.4),
        (Qt.Key.Key_5, 0.5),
        (Qt.Key.Key_6, 0.6),
        (Qt.Key.Key_7, 0.7),
        (Qt.Key.Key_8, 0.8),
        (Qt.Key.Key_9, 0.9),
    ],
)
def test_keyPressEvent_setReplaySpeed(key, expected_speed):
    # Arrange
    window = MainWindow()
    window.recorder = MagicMock()

    # Act
    event = QKeyEvent(QKeyEvent.Type.KeyPress, key,
                      Qt.KeyboardModifier.NoModifier)
    window.keyPressEvent(event)

    # Assert ???
    window.recorder.set_replay_speed.assert_called_once_with(expected_speed)

    print("✅ keyPressEvent() successfully adjusted replay speed!")
