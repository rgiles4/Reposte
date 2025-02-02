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
from video_manager import VideoRecorder

class SettingsWindow(QDialog):
    """
    Placeholder settings window
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)

        layout = QFormLayout()
        self.setLayout(layout)

        # Placeholder
        layout.addRow(QLabel("Settings Placeholder"))

        # Exit button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
class MainWindow(QMainWindow):
    """
    MainWindow is the primary GUI class for the video recorder application.

    Handles the layout and display of the video feed, initializes the
    VideoRecorder, and processes user input for controlling video recording.

    things it do:
    - Displays video feed using a QLabel within a QVBoxLayout.
    - Listens for key events to control video recording
        (pause, resume, save replay).
    - Provides an interface for interacting with the video recorder.

    things it need to-do:
    - Add more key events for managing the replay functionality.
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
        # NOTE: setSizePolicy is making the label size the size of the
        # window if elements want to be added around the label, this will
        # have to be adjusted
        self.video_feed.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.layout.addWidget(self.video_feed)

        # Settings button overlay
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("../../Reposte/cog-svgrepo-com.svg"))
        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_window)
        self.settings_button.move(10, 10)
        self.settings_button.setParent(self.video_feed)
        self.settings_button.raise_()

        # Initialize VideoRecorder
        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

    def open_settings_window(self):
            """Open the settings window"""
            settings_window = SettingsWindow()
            settings_window.exec()

    def update_frame(self, pixmap):
        """Update video feed to fill the label to the closest
        aspect ratio.

        TODO: webcam doesn't fit exactly to the label.  White bars
        on the sides are larger than the top and bottom.  Fix
        video feed to fill all of the label (screen).
        """

        # Get label dimensions
        label_size = self.video_feed.size()
        label_width = label_size.width()
        label_height = label_size.height()

        # Scale the pixmap to the calculated dimensions
        scaled_pixmap = pixmap.scaled(
            label_width,
            label_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Center the scaled pixmap in the label
        self.video_feed.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        """Handle key presses for pausing, resuming, and saving replay."""
        if event.key() == Qt.Key.Key_Escape:
            self.recorder.stop_recording()
            self.close()
        elif (
            event.key() == Qt.Key.Key_Space
        ):  # Stop recording and save with 'SPACE'
            self.recorder.save_replay()
        elif event.key() == Qt.Key.Key_P:
            # Pause recording with 'P'
            self.recorder.pause_recording()
        elif event.key() == Qt.Key.Key_R:
            # Resume recording with 'R'
            self.recorder.resume_recording()
        elif (
            event.key() == Qt.Key.Key_Up
        ):  # Start in-app replay with 'Up Key'
            self.recorder.start_in_app_replay(self.update_frame)
        elif (
            event.key() == Qt.Key.Key_Down
        ):  # Stop in-app replay and resume live recording with 'Down Key'
            self.recorder.stop_in_app_replay(resume_live=True)
        elif event.key() == Qt.Key.Key_0:
            # In-app replay: 100% speed
            self.recorder.set_replay_speed(1.0)
        elif event.key() == Qt.Key.Key_1:
            # In-app replay: 10% speed
            self.recorder.set_replay_speed(0.1)
        elif event.key() == Qt.Key.Key_2:
            # In-app replay: 20% speed
            self.recorder.set_replay_speed(0.2)
        elif event.key() == Qt.Key.Key_3:
            # In-app replay:30% speed
            self.recorder.set_replay_speed(0.3)
        elif event.key() == Qt.Key.Key_4:
            # In-app replay: 40% speed
            self.recorder.set_replay_speed(0.4)
        elif event.key() == Qt.Key.Key_5:
            # In-app replay: 50% speed
            self.recorder.set_replay_speed(0.5)
        elif event.key() == Qt.Key.Key_6:
            # In-app replay: 60% speed
            self.recorder.set_replay_speed(0.6)
        elif event.key() == Qt.Key.Key_7:
            # In-app replay: 70% speed
            self.recorder.set_replay_speed(0.7)
        elif event.key() == Qt.Key.Key_8:
            # In-app replay: 80% speed
            self.recorder.set_replay_speed(0.8)
        elif event.key() == Qt.Key.Key_9:
            # In-app replay: 90% speed
            self.recorder.set_replay_speed(0.9)
        elif event.key() == Qt.Key.Key_Left:
            # In-app replay: go to previous frame
            self.recorder.show_previous_frame()
        elif event.key() == Qt.Key.Key_Right:
            # In-app replay: go to next frame
            self.recorder.show_next_frame()
            # Fullscreen application
        elif event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
