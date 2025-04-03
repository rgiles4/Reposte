import os
from PyQt6.QtWidgets import (
    QSizePolicy,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from video_manager import VideoRecorder
from settings import SettingsWindow
from scoreboard_manager import ScoreboardManager


class ScoreboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); border-radius: 10px; padding: 5px;"
        )

        score_font = QFont("Arial", 20, QFont.Weight.Bold)
        trigger_font = QFont("Arial", 18, QFont.Weight.Bold)

        self.left_score_label = QLabel("0")
        self.left_score_label.setFont(score_font)
        self.left_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_score_label.setStyleSheet("color: white;")

        self.right_score_label = QLabel("0")
        self.right_score_label.setFont(score_font)
        self.right_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_score_label.setStyleSheet("color: white;")

        self.timer_label = QLabel("3:00")
        self.timer_label.setFont(score_font)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: white;")

        self.match_indicator = QLabel("1")
        self.match_indicator.setFont(score_font)
        self.match_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_indicator.setStyleSheet("color: white;")

        self.trigger_label = QLabel("")
        self.trigger_label.setFont(trigger_font)
        self.trigger_label.setFixedSize(40, 40)
        self.trigger_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trigger_label.setStyleSheet(
            "background-color: transparent; color: white; border-radius: 20px;"
        )

        self.red_card_overlay = QLabel()
        self.red_card_overlay.setFixedSize(80, 80)
        self.red_card_overlay.setStyleSheet(
            "background-color: transparent; border-radius: 10px;"
        )
        self.red_card_overlay.setVisible(False)

        self.yellow_card_overlay = QLabel()
        self.yellow_card_overlay.setFixedSize(80, 80)
        self.yellow_card_overlay.setStyleSheet(
            "background-color: transparent; border-radius: 10px;"
        )
        self.yellow_card_overlay.setVisible(False)

        score_layout = QHBoxLayout()
        score_layout.addWidget(self.left_score_label)
        score_layout.addWidget(self.timer_label)
        score_layout.addWidget(self.right_score_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(score_layout)
        main_layout.addWidget(
            self.match_indicator, alignment=Qt.AlignmentFlag.AlignCenter
        )

        final_layout = QVBoxLayout()
        final_layout.addWidget(
            self.red_card_overlay, alignment=Qt.AlignmentFlag.AlignCenter
        )
        final_layout.addWidget(
            self.yellow_card_overlay, alignment=Qt.AlignmentFlag.AlignCenter
        )
        final_layout.addLayout(main_layout)

        self.setLayout(final_layout)

    def update_from_data(self, data):
        if not data:
            return  # Prevent updating with empty data
        print(f"Updating scoreboard UI with data: {data}")

        self.left_score_label.setText(str(data.get("left_score", 0)))
        self.right_score_label.setText(str(data.get("right_score", 0)))
        self.timer_label.setText(
            f"{data.get('minutes', 0)}:{data.get('seconds', 0):02}"
        )
        self.match_indicator.setText(
            str(data.get("match_bits", {}).get("num_matches", 1))
        )

        lamp_bits = data.get("lamp_bits", {})
        if lamp_bits.get("left_white") or lamp_bits.get("right_white"):
            self.trigger_label.setText("W")
            self.trigger_label.setStyleSheet(
                "background-color: white; color: black; border-radius: 20px;"
            )
        elif lamp_bits.get("left_red") or lamp_bits.get("right_green"):
            self.trigger_label.setText("G")
            self.trigger_label.setStyleSheet(
                "background-color: green; color: white; border-radius: 20px;"
            )
        else:
            self.trigger_label.setText("")
            self.trigger_label.setStyleSheet("background-color: transparent;")

        penalty = data.get("penalty", {})
        red_card_active = penalty.get(
            "penalty_right_red", False
        ) or penalty.get("penalty_left_red", False)
        yellow_card_active = penalty.get(
            "penalty_right_yellow", False
        ) or penalty.get("penalty_left_yellow", False)

        self.red_card_overlay.setVisible(red_card_active)
        self.yellow_card_overlay.setVisible(yellow_card_active)

        self.repaint()
        self.update()


class MainWindow(QMainWindow):
    def update_scoreboard(self, data):
        if data:
            self.scoreboard.update_from_data(data)

    def update_frame(self, pixmap):
        if pixmap:
            self.video_feed.setPixmap(
                pixmap.scaled(
                    self.video_feed.size(), Qt.AspectRatioMode.KeepAspectRatio
                )
            )

    def open_settings_window(self):
        settings_window = SettingsWindow(self.recorder)
        settings_window.exec()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RePoste")
        self.showFullScreen()

        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.video_feed = QLabel()
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_feed.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.video_feed.setStyleSheet("background-color: black;")
        self.main_layout.addWidget(self.video_feed)

        self.scoreboard = ScoreboardWidget()
        self.scoreboard.setFixedHeight(80)
        self.main_layout.addWidget(
            self.scoreboard,
            alignment=Qt.AlignmentFlag.AlignBottom
            | Qt.AlignmentFlag.AlignHCenter,
        )

        self.settings_button = QPushButton()
        self.settings_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon_path = os.path.abspath("../Reposte/images/cog-svgrepo-com.svg")

        if os.path.exists(icon_path):
            self.settings_button.setIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon not found at {icon_path}")

        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_window)
        self.main_layout.addWidget(
            self.settings_button,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )

        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

        self.scoreboard_manager = ScoreboardManager()
        self.scoreboard_manager.scoreboard_updated.connect(
            self.update_scoreboard
        )
        self.scoreboard_manager.start()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.recorder.stop_recording()
            self.scoreboard_manager.stop()
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
            self.recorder.set_replay_speed(
                round((key - Qt.Key.Key_0) * 0.1, 1)
            )
        elif key == Qt.Key.Key_Left:
            self.recorder.show_previous_frame()
        elif key == Qt.Key.Key_Right:
            self.recorder.show_next_frame()
        elif key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
