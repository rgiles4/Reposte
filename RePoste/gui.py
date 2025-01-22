from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from video_manager import VideoRecorder

class MainWindow(QMainWindow):
    """
    MainWindow is the primary GUI class for the video recorder application.

    It handles the layout and display of the video feed, initializes the
    VideoRecorder, and processes user input for controlling video recording.

    things it do:
    - Displays video feed using a QLabel within a QVBoxLayout.
    - Listens for key events to control video recording (pause, resume, save replay).
    - Provides an interface for interacting with the video recorder.

    things it need to-do:
    - Add more key events for managing the replay functionality.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fullscreen Video Recorder")

        # Set up central widget and layout
        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Video feed QLabel
        self.video_feed = QLabel()
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_feed)

        # Initialize VideoRecorder
        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

    def update_frame(self, pixmap):
        """Update the video feed with the provided pixmap."""
        self.video_feed.setPixmap(pixmap)

    def keyPressEvent(self, event):
        """Handle key presses for pausing, resuming, and saving replay."""
        if event.key() == Qt.Key.Key_Escape:
            self.recorder.stop_recording()
            self.close()
        elif event.key() == Qt.Key.Key_Space:  # Stop recording and save with 'SPACE'
            self.recorder.save_replay()
        elif event.key() == Qt.Key.Key_P:  # Pause recording with 'P'
            self.recorder.pause_recording()
        elif event.key() == Qt.Key.Key_R:  # Resume recording with 'R'
            self.recorder.resume_recording()
        elif event.key() == Qt.Key.Key_A:  # Start in-app replay with 'A'
            self.recorder.start_in_app_replay(self.update_frame)
        elif event.key() == Qt.Key.Key_X:  # Stop in-app replay and resume live recording with 'X'
            self.recorder.stop_in_app_replay(resume_live=True)
