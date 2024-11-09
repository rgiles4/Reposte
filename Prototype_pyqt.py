import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RePoste Prototype (PyQt6)")
        self.setGeometry(100, 100, 800, 600)

        # Main window variables
        self.main_window_widget = QWidget()
        self.main_window_layout = QVBoxLayout()

        # Top frame
        self.top_frame = QFrame()
        self.top_frame_layout = QHBoxLayout()

        self.placehold_button = QPushButton("Placeholder")
        self.top_frame_layout.addWidget(self.placehold_button)

        self.top_frame.setLayout(self.top_frame_layout)
        self.top_frame.setFixedHeight(50)

        # Horizontal area for video frame
        self.video_frame = QHBoxLayout()

        # Side Frame
        self.side_frame = QFrame()
        self.side_frame_layout = QVBoxLayout()

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.replay_button = QPushButton("Replay")

        self.side_frame_layout.addWidget(self.start_button)
        self.side_frame_layout.addWidget(self.stop_button)
        self.side_frame_layout.addWidget(self.replay_button)

        self.side_frame.setLayout(self.side_frame_layout)
        self.side_frame.setFixedWidth(150)

        # Video Frame
        self.video_feed = QLabel("Video Feed")
        self.video_feed.setStyleSheet("background-color: lightgray;")
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.video_frame.addWidget(self.side_frame)
        self.video_frame.addWidget(self.video_feed)

        self.main_window_layout.addWidget(self.top_frame)
        self.main_window_layout.addLayout(self.video_frame)

        self.main_window_widget.setLayout(self.main_window_layout)
        self.setCentralWidget(self.main_window_widget)


if __name__ == "__main__":
    app = QApplication([])

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
