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

        self.side_frame_width = 100
        self.top_frame_height = 50

        self.sf_button_width = 80
        self.tf_button_width = 80

        self.SetupGUI()

    def SetupGUI(self):
        self.setWindowTitle("RePoste Prototype (PyQt6)")
        self.setGeometry(100, 100, 800, 600)

        # app window
        self.app_window_widget = QWidget()
        self.app_window_layout = QHBoxLayout()

        # Side frame
        self.side_frame = QFrame()
        self.side_frame.setFixedWidth(self.side_frame_width)
        self.side_frame_layout = QVBoxLayout(self.side_frame)

        # Add buttons to side frame
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.replay_button = QPushButton("Replay")

        self.play_button.setFixedWidth(self.sf_button_width)
        self.stop_button.setFixedWidth(self.sf_button_width)
        self.replay_button.setFixedWidth(self.sf_button_width)

        self.side_frame_layout.addWidget(self.play_button)
        self.side_frame_layout.addWidget(self.stop_button)
        self.side_frame_layout.addWidget(self.replay_button)

        # Align layout to the top of the side frame
        self.side_frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.app_window_layout.addWidget(self.side_frame)

        # Top and video frame independent of side frame
        self.main_window_widget = QWidget()
        self.main_window_layout = QVBoxLayout(self.main_window_widget)

        # Top Frame
        self.top_frame = QFrame()
        self.top_frame.setFixedHeight(self.top_frame_height)
        self.top_frame_layout = QVBoxLayout(self.top_frame)

        # Add buttons to top frame
        self.save_file_button = QPushButton("Save")
        self.save_file_button.setFixedWidth(self.tf_button_width)
        self.top_frame_layout.addWidget(
            self.save_file_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Video Frame
        self.video_frame = QLabel("Video Feed")
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_window_layout.addWidget(self.top_frame)
        self.main_window_layout.addWidget(self.video_frame)

        # Apply and format widgets to the app
        self.app_window_layout.addWidget(self.main_window_widget)
        self.app_window_widget.setLayout(self.app_window_layout)

        self.StylingGUI()

        # renders widgets to screen
        self.setCentralWidget(self.app_window_widget)

    def StylingGUI(self):

        self.app_window_widget.setStyleSheet("""background-color: gray;""")

        # Side frame
        self.side_frame.setStyleSheet(
            """ QFrame { background-color: darkgray;
            border: 1px solid black;
            border-radius: 10px;}"""
        )

        # Top frame
        self.top_frame.setStyleSheet(
            """ QFrame { background-color: darkgray;
            border: 1px solid black;
            border-radius: 10px;}"""
        )

        # Video frame
        self.video_frame.setStyleSheet(
            """ QLabel { background-color: darkgray;
            border-radius: 10px;}"""
        )

        # Button Styling
        self.play_button.setStyleSheet(
            """ QPushButton { background-color: green;}"""
        )

        self.stop_button.setStyleSheet(
            """ QPushButton { background-color: red;}"""
        )

        self.replay_button.setStyleSheet(
            """ QPushButton { background-color: orange;}"""
        )

        self.save_file_button.setStyleSheet(
            """ QPushButton { background-color: slategray;}"""
        )


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("fusion")

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
