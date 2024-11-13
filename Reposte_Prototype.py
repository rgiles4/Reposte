import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSlider,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

import imageio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.side_frame_width = 100
        self.top_frame_height = 50

        self.sf_button_width = 80
        self.tf_button_width = 80

        self.width = 800
        self.height = 600
        self.fps = 60
        self.buffer = []
        self.max_frames = 4 * self.fps
        self.recording_num = 0
        self.playback_duration = 4

        self.Setup_GUI()

        self.is_recording = False
        self.cap = None

    def Setup_GUI(self):
        self.setWindowTitle("RePoste Prototype (PyQt6)")
        self.setGeometry(100, 100, self.width, self.height)

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

        # Align button layout to the top of the side frame
        self.side_frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # apply side frame to app window
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
        self.video_feed = QLabel("Video Feed")
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_window_layout.setContentsMargins(0, 0, 0, 0)
        self.main_window_layout.addWidget(self.top_frame)
        self.main_window_layout.addWidget(self.video_feed)

        # Slider for playback length (1-10 seconds)
        slider_layout = QHBoxLayout()
        self.playback_frame = QFrame()

        self.playback_label = QLabel(
            f"Playback Duration: {self.playback_duration} Seconds"
        )
        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(1, 10)
        self.playback_slider.setValue(self.playback_duration)
        self.playback_slider.setToolTip("Set playback duration (seconds)")
        self.playback_slider.valueChanged.connect(self.Set_Playback_Duration)
        self.playback_frame_layout = QVBoxLayout(self.playback_frame)
        self.playback_frame_layout.addWidget(self.playback_label)
        slider_layout.addWidget(self.playback_frame)
        slider_layout.addWidget(self.playback_slider)

        self.main_window_layout.addLayout(slider_layout)

        # Apply and format widgets to the app
        self.app_window_layout.addWidget(self.main_window_widget)
        self.app_window_widget.setLayout(self.app_window_layout)

        self.Styling_GUI()

        # renders widgets to screen
        self.setCentralWidget(self.app_window_widget)

        self.play_button.clicked.connect(self.Play_Video)
        self.stop_button.clicked.connect(self.Stop_Video)
        self.replay_button.clicked.connect(self.Save_Replay)

    def Styling_GUI(self):
        self.app_window_widget.setStyleSheet("""background-color: #222222;""")

        # Side frame
        self.side_frame.setStyleSheet(
            """ QFrame { background-color: #636363;
            border: 1px solid black;
            border-radius: 10px;}"""
        )

        # Top frame
        self.top_frame.setStyleSheet(
            """ QFrame { background-color: #636363;
            border: 1px solid black;
            border-radius: 10px;}"""
        )

        # Video frame
        self.video_feed.setStyleSheet(
            """ QLabel { background-color: #636363;
            border-radius: 10px;}"""
        )

        # Playback slider frame
        self.playback_frame.setStyleSheet(
            """ QFrame { background-color: #636363;
            border: 1px solid black;
            border-radius: 5px;
            padding: 5px;}"""
        )

        # Button Styling
        self.play_button.setStyleSheet(
            """ QPushButton { background-color: #2e6f40;}"""
            )

        self.stop_button.setStyleSheet(
            """ QPushButton { background-color: #942222;}"""
            )

        self.replay_button.setStyleSheet(
            """ QPushButton { background-color: #be5103;}"""
        )

        self.save_file_button.setStyleSheet(
            """ QPushButton { background-color: #6d8196;}"""
        )

    # Updates max_frames to set playback duration
    def Set_Playback_Duration(self, value):
        self.playback_duration = value
        self.max_frames = self.playback_duration * self.fps
        self.playback_label.setText(
            f"Playback Duration: {self.playback_duration} Seconds"
        )

    def Update_Frame(self):
        try:
            if self.is_recording:
                frame = self.cap.get_next_data()

                # Convert frame to QImage to update inside the QLabel
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_frame = QImage(
                    frame.data,
                    w,
                    h,
                    bytes_per_line,
                    QImage.Format.Format_RGB888,
                )

                # scaled QImage frames
                scaled_qt_frame = qt_frame.scaled(
                    self.video_feed.size(), Qt.AspectRatioMode.KeepAspectRatio
                )

                # Set the scaled qt frame to the label
                self.video_feed.setPixmap(QPixmap.fromImage(scaled_qt_frame))

                # Add frame to buffer
                self.buffer.append(frame)
                if len(self.buffer) > self.max_frames:
                    self.buffer.pop(0)

                # Update frame every 1000/fps milliseconds
                QTimer.singleShot(int(1000 / self.fps), self.Update_Frame)
        except (IndexError, RuntimeError, StopIteration) as e:
            print(f"Error: {e}")

    def Play_Video(self):
        self.cap = imageio.get_reader("<video0>", "ffmpeg")
        self.is_recording = True
        self.buffer.clear()
        print("Recording started.")
        self.Update_Frame()

    def Stop_Video(self):
        self.is_recording = False
        if self.cap:
            self.cap.close()
            self.cap = None

        self.video_feed.clear()
        print("Recording stopped.")

    def Save_Replay(self):
        video_path = os.path.join(
            os.getcwd(), f"Video-Output{self.recording_num}.mp4"
            )

        with imageio.get_writer(video_path, fps=self.fps) as writer:
            for frame in self.buffer:
                writer.append_data(frame)

        print("Replay saved at:", video_path)
        self.recording_num += 1
        self.Play_Replay(video_path)

    def Play_Replay(self, video_path):
        # Create the replay window GUI
        # TODO: make replay window pretty
        replay_window = QWidget()
        replay_window.setWindowTitle(f"Video Replay: {video_path}")
        replay_window.setGeometry(1000, 100, self.width, self.height)
        replay_window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # Layout for the replay window
        replay_layout = QVBoxLayout(replay_window)

        # Create QLabel to render video frame
        video_feed_replay = QLabel("Video Feed")
        video_feed_replay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        replay_layout.addWidget(video_feed_replay)

        # Create a bottom frame
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(self.height // 2)
        replay_layout.addWidget(bottom_frame)

        cap_replay = imageio.get_reader(video_path).iter_data()

        def Update_Replay_Frame():
            try:
                frame = next(cap_replay)
            except (IndexError, RuntimeError, StopIteration):
                print("Replay ended.")
                cap_replay.close()
                replay_window.close()
                return

            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_frame = QImage(
                frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )

            # Scale the QImage to fit the window w/ specific aspect ratios
            scaled_qt_frame = qt_frame.scaled(
                self.width, self.height, Qt.AspectRatioMode.KeepAspectRatio
            )

            # Set the scaled image to the QLabel
            video_feed_replay.setPixmap(QPixmap.fromImage(scaled_qt_frame))

            # Update every frame 1000/fps milliseconds
            QTimer.singleShot(int(1000 / self.fps), Update_Replay_Frame)

        # Update frames
        Update_Replay_Frame()

        # render replay window
        replay_window.show()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("fusion")

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
