from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from video_manager import VideoRecorder

class MainWindow(QMainWindow):
    """
    MainWindow is the primary GUI class for the video recorder application.

    Handles the layout and display of the video feed, initializes the
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
        elif event.key() == Qt.Key.Key_Up:  # Start in-app replay with 'Up Key'
            self.recorder.start_in_app_replay(self.update_frame)
        elif event.key() == Qt.Key.Key_Down:  # Stop in-app replay and resume live recording with 'Down Key'
            self.recorder.stop_in_app_replay(resume_live=True)
        elif event.key() == Qt.Key.Key_0:
            self.recorder.set_replay_speed(1.0)  #In-app replay: 100% speed
        elif event.key() == Qt.Key.Key_1:
            self.recorder.set_replay_speed(0.1)  #In-app replay: 10% speed
        elif event.key() == Qt.Key.Key_2:
            self.recorder.set_replay_speed(0.2)  #In-app replay: 20% speed
        elif event.key() == Qt.Key.Key_3:
            self.recorder.set_replay_speed(0.3)  # In-app replay:30% speed
        elif event.key() == Qt.Key.Key_4:
            self.recorder.set_replay_speed(0.4)  #In-app replay: 40% speed
        elif event.key() == Qt.Key.Key_5:
            self.recorder.set_replay_speed(0.5)  #In-app replay: 50% speed
        elif event.key() == Qt.Key.Key_6:
            self.recorder.set_replay_speed(0.6)  #In-app replay: 60% speed
        elif event.key() == Qt.Key.Key_7:
            self.recorder.set_replay_speed(0.7)  #In-app replay: 70% speed
        elif event.key() == Qt.Key.Key_8:
            self.recorder.set_replay_speed(0.8)  #In-app replay: 80% speed
        elif event.key() == Qt.Key.Key_9:
            self.recorder.set_replay_speed(0.9)  #In-app replay: 90% speed
        elif event.key() == Qt.Key.Key_Left:
            self.recorder.show_previous_frame() # In-app replay: go to previous frame
        elif event.key() == Qt.Key.Key_Right:
            self.recorder.show_next_frame() # In-app replay: go to next frame

