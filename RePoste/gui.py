from PyQt6.QtWidgets import (
    QSizePolicy,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

# Use RePoste.video_manager for running tests
from video_manager import VideoRecorder


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
        self.setWindowState(Qt.WindowState.WindowMaximized)

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

        # Initialize VideoRecorder
        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

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

        # Get webcam (pixmap) dimensions
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # Calculate aspect ratio of the pixmap
        pixmap_aspect_ratio = pixmap_width / pixmap_height

        if label_width / label_height > pixmap_aspect_ratio:
            # Scale to fit height of gui window
            target_height = label_height
            target_width = int(target_height * pixmap_aspect_ratio)
        else:
            # Scake to fit width of gui window
            target_width = label_width
            target_height = int(target_width / pixmap_aspect_ratio)

        # Scale the pixmap to the calculated dimensions
        scaled_pixmap = pixmap.scaled(
            target_width,
            target_height,
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
