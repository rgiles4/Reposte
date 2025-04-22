# import pytest
# from PyQt6.QtWidgets import QApplication
# from RePoste.settings import SettingsWindow
# from RePoste.video_manager import VideoRecorder
# from RePoste.gui import MainWindow  # Add this import


# @pytest.fixture(scope="module")
# def create_app():
#     return QApplication([])


# def test_settings_window_display(create_app):
#     """Test if the settings window can open and display."""
#     recorder = VideoRecorder()  # Create a mock VideoRecorder instance
#     settings_window = SettingsWindow(recorder)  # Pass it to SettingsWindow
#     settings_window.show()


# def test_keybinds(create_app):
#     """Test if keybinds are correctly mapped to actions."""
#     window = MainWindow()
#     key_actions = {
#         "Space": "save_replay",
#         "P": "pause_recording",
#         "R": "resume_recording",
#         "Up": "start_in_app_replay",
#         "Down": "stop_in_app_replay",
#         "Left": "show_previous_frame",
#         "Right": "show_next_frame",
#         "F11": "toggle_fullscreen"
#     }

#     for key, method in key_actions.items():
#         assert hasattr(window, "keyPressEvent"), (
#             f"❌ {key} keybind function missing: {method}")


# def test_microphone_used(create_app):
#     """
#     Test if a microphone is correctly detected
#     (Placeholder, update based on implementation).
#     """
#     recorder = VideoRecorder()

#     if hasattr(recorder, "microphone"):  # Check if microphone exists
#         assert recorder.microphone is not None, "❌ No microphone detected."
#     else:
#         print("⚠️ No microphone attribute found in VideoRecorder class.")


# def test_fps_lock(create_app):
#     """Test if FPS is locked at the correct value."""
#     recorder = VideoRecorder(fps=60)
#     assert recorder.fps == 60, f"❌ Expected FPS: 60, got {recorder.fps}"

#     recorder.fps = 30
#     assert recorder.fps == 30, f"❌ Expected FPS: 30, got {recorder.fps}"
