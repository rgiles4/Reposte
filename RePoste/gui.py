import os
from PyQt6.QtWidgets import (
    QSizePolicy,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

# Use RePoste.video_manager for running tests

from video_manager import VideoRecorder
from RePoste.settings import SettingsWindow

class MainWindow(QMainWindow):
    """
    MainWindow is the primary GUI class for the video recorder application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RePoste")
        self.showFullScreen()

        # Set up central widget and layout
        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Video feed QLabel
        self.video_feed = QLabel()
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_feed.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.layout.addWidget(self.video_feed)

        # Settings button overlay
        self.settings_button = QPushButton()
        self.settings_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Prevent Space from triggering it
        icon_path = os.path.abspath("../Reposte/images/cog-svgrepo-com.svg")

        # Find image from image path
        if os.path.exists(icon_path):
            self.settings_button.setIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon not found at {icon_path}")

        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_window)
        
        # Add button
        self.layout.addWidget(self.settings_button)

        # Initialize VideoRecorder
        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

    def open_settings_window(self):
        """Open the settings window and pass video recorder settings."""
        settings_window = SettingsWindow(self.recorder)  # Pass the video_recorder instance
        settings_window.exec()

    def update_frame(self, pixmap):
        """Update video feed to fill the label proportionally."""
        label_size = self.video_feed.size()
        scaled_pixmap = pixmap.scaled(
            label_size.width(),
            label_size.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.video_feed.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        """Handle key presses for video control and fullscreen toggling."""
        key = event.key()

        if key == Qt.Key.Key_Escape:
            self.recorder.stop_recording()
            self.close()
        elif key == Qt.Key.Key_Space:
            self.recorder.save_replay()
        elif key == Qt.Key.Key_P:
            self.recorder.pause_recording()
        elif key == Qt.Key.Key_R:
            self.recorder.resume_recording()
        elif key == Qt.Key.Key_Up:
            self.recorder.start_in_app_replay(self.update_frame)
        elif key == Qt.Key.Key_Down:
            self.recorder.stop_in_app_replay(resume_live=True)
        elif key == Qt.Key.Key_0:
            self.recorder.set_replay_speed(1.0)
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            self.recorder.set_replay_speed(round((key - Qt.Key.Key_0) * 0.1, 1)) 
        elif key == Qt.Key.Key_Left:
            self.recorder.show_previous_frame()
        elif key == Qt.Key.Key_Right:
            self.recorder.show_next_frame()
        elif key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
