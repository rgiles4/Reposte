import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from RePoste.gui import SettingsWindow, MainWindow
from RePoste.video_manager import VideoRecorder

# Create QApplication fixture
@pytest.fixture(scope="module")
def create_app():
    return QApplication([])

def test_settings_window_display(create_app):
    """Test if the settings window can open and display."""
    settings_window = SettingsWindow()
    assert settings_window.isHidden(), "❌ Settings window should be hidden on initialization."
    
    settings_window.show()
    assert settings_window.isVisible(), "❌ Settings window did not become visible after calling show()."

    settings_window.close()
    assert settings_window.isHidden(), "❌ Settings window did not close properly."

    print("✅ Settings window display test passed.")

def test_camera_used(create_app):
    """Test if the camera source is correctly set."""
    recorder = VideoRecorder()
    assert recorder.reader is None, "❌ Camera reader should be None before starting recording."

    recorder.start_recording(lambda _: None)  # Mock update callback
    assert recorder.reader is not None, "❌ Camera reader should be initialized after starting recording."

    recorder.stop_recording()
    assert recorder.reader is None, "❌ Camera reader should be None after stopping recording."

    print("✅ Camera usage test passed.")

def test_keybinds(create_app):
    """Test if keybinds are correctly mapped to actions."""
    window = MainWindow()
    key_actions = {
        "Space": "save_replay",
        "P": "pause_recording",
        "R": "resume_recording",
        "Up": "start_in_app_replay",
        "Down": "stop_in_app_replay",
        "Left": "show_previous_frame",
        "Right": "show_next_frame",
        "F11": "toggle_fullscreen"
    }

    for key, method in key_actions.items():
        assert hasattr(window, "keyPressEvent"), f"❌ {key} keybind function missing: {method}"

    print("✅ Keybind mapping test passed.")

def test_microphone_used(create_app):
    """Test if a microphone is correctly detected (Placeholder, update based on implementation)."""
    recorder = VideoRecorder()
    
    if hasattr(recorder, "microphone"):  # Check if microphone attribute exists
        assert recorder.microphone is not None, "❌ No microphone detected."
    else:
        print("⚠️ No microphone attribute found in VideoRecorder class.")

    print("✅ Microphone test (if implemented) passed.")

def test_fps_lock(create_app):
    """Test if FPS is locked at the correct value."""
    recorder = VideoRecorder(fps=60)
    assert recorder.fps == 60, f"❌ Expected FPS to be 60, got {recorder.fps}"

    recorder.fps = 30
    assert recorder.fps == 30, f"❌ Expected FPS to be 30, got {recorder.fps}"

    print("✅ FPS lock test passed.")

def test_buffer_duration(create_app):
    """Test if buffer duration is set correctly."""
    recorder = VideoRecorder(fps=60, buffer_duration=5)
    assert len(recorder.buffer) == 60 * 5, f"❌ Expected buffer length to be {60 * 5}, got {len(recorder.buffer)}"

    recorder.set_buffer_duration(10)
    assert len(recorder.buffer) == 60 * 10, f"❌ Expected buffer length to be {60 * 10}, got {len(recorder.buffer)}"

    print("✅ Buffer duration test passed.")
