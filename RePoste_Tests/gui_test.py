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
    mock_pixmap.width.return_value = 1920  # Mock width return value
    mock_pixmap.height.return_value = 1080  # Mock height return value

    # Mock the scaled method to return the mock_pixmap itself
    scaled_pixmap = MagicMock(spec=QPixmap)
    scaled_pixmap.width.return_value = 1920
    scaled_pixmap.height.return_value = 1080

    # Mock the scaled method of QPixmap to return the scaled_pixmap
    mock_pixmap.scaled.return_value = scaled_pixmap

    window.video_feed.setPixmap = MagicMock()

    # Act
    window.update_frame(mock_pixmap)

    # Assert
    window.video_feed.setPixmap.assert_called_once()
    scaled_pixmap_passed = window.video_feed.setPixmap.call_args[0][0]

    # Assert that scaled_pixmap is actually a MagicMock and that the
    # return values are correct
    assert isinstance(
        scaled_pixmap_passed, MagicMock
    ), "scaled_pixmap is not a MagicMock"

    # Check that the width and height methods return the correct values
    assert (
        scaled_pixmap_passed.width() == 1920
    ), f"❌ Expected width to be 1920: {scaled_pixmap_passed.width()}"
    assert (
        scaled_pixmap_passed.height() == 1080
    ), f"❌ Expected height to be 1080: {scaled_pixmap_passed.height()}"

    # Check the values are integers
    assert isinstance(
        scaled_pixmap_passed.width(), int
    ), f"❌ Expected an integer for width: {scaled_pixmap_passed.width()}"
    assert isinstance(
        scaled_pixmap_passed.height(), int
    ), f"❌ Expected an integer for height: {scaled_pixmap_passed.height()}"

    # Ensure the pixmap has positive dimensions
    assert (
        scaled_pixmap_passed.width() > 0
    ), f"❌ Scaled pixmap has invalid width: {scaled_pixmap_passed.width()}"
    assert (
        scaled_pixmap_passed.height() > 0
    ), f"❌ Scaled pixmap has invalid height: {scaled_pixmap_passed.height()}"

    print("✅ update_frame() successfully updated the video feed!")


def test_open_settings_window(mocker):
    # Arrange
    window = MainWindow()
    
    # Mock the instantiation of SettingsWindow
    mock_settings_window = mocker.patch("RePoste.gui.SettingsWindow",
                                        autospec=True)
    instance = mock_settings_window.return_value  # Mocked instance

    # Act
    window.open_settings_window()

    # Assert
    # Ensure SettingsWindow was instantiated
    mock_settings_window.assert_called_once()
    instance.exec.assert_called_once()  # Ensure exec() was called

    print("✅ open_settings_window() successfully opened the settings menu!")


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
    event = QKeyEvent(
        QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier
    )

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
    event = QKeyEvent(
        QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier
    )
    window.keyPressEvent(event)

    # Assert ???
    window.recorder.set_replay_speed.assert_called_once_with(expected_speed)

    print("✅ keyPressEvent() successfully adjusted replay speed!")
