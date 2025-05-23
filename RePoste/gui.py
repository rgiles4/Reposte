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


class ScoreboardWidget(QWidget):
    def __init__(self, scoreboard_manager):
        super().__init__()
        self.scoreboard_manager = scoreboard_manager
        self.init_ui()

    # (keep the rest of init_ui and update_from_data)

    def get_hit_style(self, color):
        if color == "green":
            return "background: green; border-radius: 15px;"
        elif color == "red":
            return "background: red; border-radius: 15px;"
        elif color == "white":
            return "background: white; border-radius: 15px;"
        else:
            return "background: transparent; border-radius: 15px;"

    def init_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color: rgba(128, 128, 128, 200);"
            "border-radius: 12px; padding: 10px;"
        )

        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)

        # --- Left side ---
        self.left_red_flag = QLabel()
        self.left_red_flag.setFixedSize(30, 30)
        self.left_red_flag.setStyleSheet(
            "border-radius: 8px; background: transparent;"
        )

        self.left_yellow_flag = QLabel()
        self.left_yellow_flag.setFixedSize(30, 30)
        self.left_yellow_flag.setStyleSheet(
            "border-radius: 8px; background: transparent;"
        )

        # --- Right side ---
        self.right_red_flag = QLabel()
        self.right_red_flag.setFixedSize(30, 30)
        self.right_red_flag.setStyleSheet(
            "border-radius: 8px; background: transparent;"
        )

        self.right_yellow_flag = QLabel()
        self.right_yellow_flag.setFixedSize(30, 30)
        self.right_yellow_flag.setStyleSheet(
            "border-radius: 8px; background: transparent;"
        )

        self.left_score_label = QLabel("0")
        self.left_score_label.setFont(font)
        self.left_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_score_label.setStyleSheet("color: #ffffff;")

        self.right_score_label = QLabel("0")
        self.right_score_label.setFont(font)
        self.right_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_score_label.setStyleSheet("color: #ffffff;")

        self.timer_label = QLabel("3:00")
        self.timer_label.setFont(font)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #ffffff;")

        self.match_indicator = QLabel("1")
        self.match_indicator.setFont(font)
        self.match_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_indicator.setStyleSheet("color: #ffffff;")

        # Left flag area
        left_flag_layout = QVBoxLayout()
        left_flag_layout.addWidget(self.left_red_flag)
        left_flag_layout.addWidget(self.left_yellow_flag)

        # Right flag area
        right_flag_layout = QVBoxLayout()
        right_flag_layout.addWidget(self.right_red_flag)
        right_flag_layout.addWidget(self.right_yellow_flag)

        # --- Left hit indicator ---
        self.left_hit_indicator = QLabel()
        self.left_hit_indicator.setFixedSize(30, 30)
        self.left_hit_indicator.setStyleSheet(
            "border-radius: 15px; background: transparent;"
        )

        # --- Right hit indicator ---
        self.right_hit_indicator = QLabel()
        self.right_hit_indicator.setFixedSize(30, 30)
        self.right_hit_indicator.setStyleSheet(
            "border-radius: 15px; background: transparent;"
        )

        # --- Left flag area (add hit indicator here) ---
        left_flag_layout = QVBoxLayout()
        left_flag_layout.addWidget(self.left_hit_indicator)
        left_flag_layout.addWidget(self.left_red_flag)
        left_flag_layout.addWidget(self.left_yellow_flag)
        left_flag_layout.setSpacing(35)

        # --- Right flag area (add hit indicator here) ---
        right_flag_layout = QVBoxLayout()
        right_flag_layout.addWidget(self.right_hit_indicator)
        right_flag_layout.addWidget(self.right_red_flag)
        right_flag_layout.addWidget(self.right_yellow_flag)
        right_flag_layout.setSpacing(35)

        # Score row layout
        score_row = QHBoxLayout()
        score_row.addLayout(left_flag_layout)
        score_row.addWidget(self.left_score_label)
        score_row.addStretch()
        score_row.addWidget(self.timer_label)
        score_row.addStretch()
        score_row.addWidget(self.right_score_label)
        score_row.addLayout(right_flag_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(score_row)
        main_layout.addWidget(
            self.match_indicator, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.setLayout(main_layout)

    def update_from_data(self, data):
        if not data:
            return

        print(f"Updating scoreboard UI with data: {data}")

        left_score = data.get("left_score", 0)
        right_score = data.get("right_score", 0)
        minutes = data.get("minutes", 0)
        seconds = data.get("seconds", 0)
        match_bits = data.get("match_bits", {})
        num_matches = match_bits.get("num_matches", 1)
        penalty = data.get("penalty", {})

        self.left_score_label.setText(str(left_score))
        self.right_score_label.setText(str(right_score))
        self.match_indicator.setText(str(num_matches))

        try:
            current_displayed_time = self.timer_label.text()
            current_minutes, current_seconds = map(
                int, current_displayed_time.split(":")
            )
        except ValueError:
            current_minutes, current_seconds = 3, 0

        # Always trust parsed seconds
        parsed_minutes = int(minutes)
        parsed_seconds = int(seconds)

        # Only override minutes if bad
        if parsed_minutes > 10:
            print(
                f"[WARNING] Minutes too high ({parsed_minutes})"
                f"keeping {current_minutes}"
            )
            minutes = current_minutes
            seconds = current_seconds
        else:
            minutes = parsed_minutes
            seconds = parsed_seconds

        # seconds = parsed_seconds no matter what
        self.timer_label.setText(f"{minutes}:{parsed_seconds:02}")

        # Update cards
        self.left_red_flag.setStyleSheet(
            "background: red; border-radius: 8px;"
            if penalty.get("penalty_left_red")
            else "background: transparent; border-radius: 8px;"
        )
        self.left_yellow_flag.setStyleSheet(
            "background: yellow; border-radius: 8px;"
            if penalty.get("penalty_left_yellow")
            else "background: transparent; border-radius: 8px;"
        )
        self.right_red_flag.setStyleSheet(
            "background: red; border-radius: 8px;"
            if penalty.get("penalty_right_red")
            else "background: transparent; border-radius: 8px;"
        )
        self.right_yellow_flag.setStyleSheet(
            "background: yellow; border-radius: 8px;"
            if penalty.get("penalty_right_yellow")
            else "background: transparent; border-radius: 8px;"
        )

        lamp_bits = data.get("lamp_bits", {})

        # Determine hit color priority: green > red > white > none
        def determine_hit_color(side):
            if lamp_bits.get(f"{side}_green"):
                return "green"
            elif lamp_bits.get(f"{side}_red"):
                return "red"
            elif lamp_bits.get(f"{side}_white"):
                return "white"
            else:
                return None

        left_hit = determine_hit_color("left")
        right_hit = determine_hit_color("right")

        self.left_hit_indicator.setStyleSheet(self.get_hit_style(left_hit))
        self.right_hit_indicator.setStyleSheet(self.get_hit_style(right_hit))

        self.repaint()


class MainWindow(QMainWindow):
    def update_scoreboard(self, data):
        if data:
            self.scoreboard.update_from_data(data)

    def update_frame(self, pixmap):
        if pixmap:
            # fmt: off
            self.video_feed.setPixmap(
                pixmap.scaled(
                    self.video_feed.size(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
                # fmt: on
            )

    def open_settings_window(self):
        settings_window = SettingsWindow(self.recorder)
        settings_window.exec()

    def __init__(self, scoreboard_manager):
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

        self.scoreboard = ScoreboardWidget(scoreboard_manager)
        self.scoreboard.setFixedHeight(120)
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
        self.settings_button.setIconSize(QSize(40, 40))
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.clicked.connect(self.open_settings_window)
        # fmt: off
        self.main_layout.addWidget(
            self.settings_button,
            alignment=Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignRight,
        )
        # fmt: on

        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

        self.scoreboard_manager = scoreboard_manager
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
