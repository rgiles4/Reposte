import os
<<<<<<< HEAD
import sys
=======
>>>>>>> origin/sgood-dev-new
from PyQt6.QtWidgets import (
    QApplication,
    QSizePolicy,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
<<<<<<< HEAD
    QHBoxLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
=======
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from video_manager import VideoRecorder
from settings import SettingsWindow
from scoreboard_manager import ScoreboardManager


class ScoreboardWidget(QWidget):
    def __init__(self, scoreboard_manager):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            "background-color: rgba(0, 0, 0, 180); border-radius: 12px; padding: 10px;"
        )

        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)

        self.left_flag = QLabel()
        self.left_flag.setFixedSize(35, 35)
        self.left_flag.setStyleSheet(
            "border-radius: 8px; background: transparent;"
        )

        self.right_flag = QLabel()
        self.right_flag.setFixedSize(35, 35)
        self.right_flag.setStyleSheet(
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
        self.timer_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #ffffff;")

        self.match_indicator = QLabel("1")
        self.match_indicator.setFont(font)
        self.match_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.match_indicator.setStyleSheet("color: #ffffff;")

        # Score row layout
        score_row = QHBoxLayout()
        score_row.addWidget(self.left_flag)
        score_row.addWidget(self.left_score_label)
        score_row.addStretch()
        score_row.addWidget(self.timer_label)
        score_row.addStretch()
        score_row.addWidget(self.right_score_label)
        score_row.addWidget(self.right_flag)

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
        lamp_bits = data.get("lamp_bits", {})
        penalty = data.get("penalty", {})

        self.left_score_label.setText(str(left_score))
        self.right_score_label.setText(str(right_score))
        self.timer_label.setText(f"{minutes}:{seconds:02}")
        self.match_indicator.setText(str(num_matches))

        if penalty.get("penalty_left_red", False):
            self.left_flag.setStyleSheet(
                "background: red; border-radius: 8px;"
            )
        elif penalty.get("penalty_left_yellow", False):
            self.left_flag.setStyleSheet(
                "background: yellow; border-radius: 8px;"
            )
        else:
            self.left_flag.setStyleSheet("background: transparent;")

        if penalty.get("penalty_right_red", False):
            self.right_flag.setStyleSheet(
                "background: red; border-radius: 8px;"
            )
        elif penalty.get("penalty_right_yellow", False):
            self.right_flag.setStyleSheet(
                "background: yellow; border-radius: 8px;"
            )
        else:
            self.right_flag.setStyleSheet("background: transparent;")

        self.repaint()
        # self.update()
>>>>>>> origin/sgood-dev-new

from video_manager import VideoRecorder
from settings import SettingsWindow
from scoreboard_manager import ScoreboardManager 

class ScoreboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 10px; padding: 5px;")

        score_font = QFont("Arial", 16, QFont.Weight.Bold)
        trigger_font = QFont("Arial", 14, QFont.Weight.Bold)

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
        self.trigger_label.setFixedSize(30, 30)
        self.trigger_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trigger_label.setStyleSheet("background-color: transparent; color: white; border-radius: 15px;")

        # Yellow & Red Card Overlays with smaller sizes
        self.red_card_overlay = QLabel("Red Card")
        self.red_card_overlay.setFixedSize(80, 40)
        self.red_card_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.red_card_overlay.setStyleSheet("background-color: red; color: white; border-radius: 10px; font-size: 14px;")
        self.red_card_overlay.setVisible(False)

        self.yellow_card_overlay = QLabel("Yellow Card")
        self.yellow_card_overlay.setFixedSize(80, 40)
        self.yellow_card_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.yellow_card_overlay.setStyleSheet("background-color: yellow; color: black; border-radius: 10px; font-size: 14px;")
        self.yellow_card_overlay.setVisible(False)

        # Touch Indicators (circle with color) next to each player
        self.left_touch_indicator = QLabel()
        self.left_touch_indicator.setFixedSize(25, 25)
        self.left_touch_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_touch_indicator.setStyleSheet("background-color: transparent; border-radius: 12px;")

        self.right_touch_indicator = QLabel()
        self.right_touch_indicator.setFixedSize(25, 25)
        self.right_touch_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_touch_indicator.setStyleSheet("background-color: transparent; border-radius: 12px;")

        # Layout for the score and timer
        score_layout = QHBoxLayout()
        score_layout.addWidget(self.left_score_label)
        score_layout.addWidget(self.timer_label)
        score_layout.addWidget(self.right_score_label)

        # Create a horizontal layout for the cards and touch indicators
        side_layout = QHBoxLayout()
        side_layout.addWidget(self.left_touch_indicator, alignment=Qt.AlignmentFlag.AlignLeft)
        side_layout.addWidget(self.red_card_overlay, alignment=Qt.AlignmentFlag.AlignLeft)
        side_layout.addStretch(1)  # Push the elements to the left side
        side_layout.addWidget(self.yellow_card_overlay, alignment=Qt.AlignmentFlag.AlignRight)
        side_layout.addWidget(self.right_touch_indicator, alignment=Qt.AlignmentFlag.AlignRight)

        # Create the main layout and add the score and timer
        main_layout = QVBoxLayout()
        main_layout.addLayout(score_layout)
        main_layout.addWidget(self.match_indicator, alignment=Qt.AlignmentFlag.AlignCenter)

        # Final layout: combining score, touch indicators, and cards
        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)  # Add main score layout
        final_layout.addLayout(side_layout)  # Add the side layout with the touch indicators and cards

        self.setLayout(final_layout)

    def update_from_data(self, data):
        if not data:
            return  # Prevent updating with empty data
        
        self.left_score_label.setText(str(data.get("left_score", 0)))
        self.right_score_label.setText(str(data.get("right_score", 0)))
        self.timer_label.setText(f"{data.get('minutes', 0)}:{data.get('seconds', 0):02}")
        self.match_indicator.setText(str(data.get("match_bits", {}).get("num_matches", 1)))

        lamp_bits = data.get("lamp_bits", {})
        if lamp_bits.get("left_white") or lamp_bits.get("right_white"):
            self.trigger_label.setText("W")
            self.trigger_label.setStyleSheet("background-color: white; color: black; border-radius: 15px;")
        elif lamp_bits.get("left_red") or lamp_bits.get("right_green"):
            self.trigger_label.setText("G")
            self.trigger_label.setStyleSheet("background-color: green; color: white; border-radius: 15px;")
        else:
            self.trigger_label.setText("")
            self.trigger_label.setStyleSheet("background-color: transparent;")

        # Correctly update red/yellow card visibility
        penalty = data.get("penalty", {})
        red_card_active = penalty.get("penalty_right_red", False) or penalty.get("penalty_left_red", False)
        yellow_card_active = penalty.get("penalty_right_yellow", False) or penalty.get("penalty_left_yellow", False)

        self.red_card_overlay.setVisible(red_card_active)
        self.yellow_card_overlay.setVisible(yellow_card_active)

        # Update touch indicators (circles)
        if lamp_bits.get("left_red"):
            self.left_touch_indicator.setStyleSheet("background-color: red; border-radius: 12px;")
        else:
            self.left_touch_indicator.setStyleSheet("background-color: transparent; border-radius: 12px;")

        if lamp_bits.get("right_green"):
            self.right_touch_indicator.setStyleSheet("background-color: green; border-radius: 12px;")
        else:
            self.right_touch_indicator.setStyleSheet("background-color: transparent; border-radius: 12px;")

        if lamp_bits.get("left_white"):
            self.left_touch_indicator.setStyleSheet("background-color: white; border-radius: 12px;")
        elif lamp_bits.get("right_white"):
            self.right_touch_indicator.setStyleSheet("background-color: white; border-radius: 12px;")

        # Ensure layout is updated properly
        self.repaint()
        self.update()

class MainWindow(QMainWindow):
    def update_scoreboard(self, data):
        if data:
            self.scoreboard.update_from_data(data)
<<<<<<< HEAD
    def update_frame(self, pixmap):
        if pixmap:
            self.video_feed.setPixmap(pixmap.scaled(self.video_feed.size(), Qt.AspectRatioMode.KeepAspectRatio))
    def open_settings_window(self):
        settings_window = SettingsWindow(self.recorder)
        settings_window.exec()
    def __init__(self):
=======

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

    def __init__(self, scoreboard_manager):
>>>>>>> origin/sgood-dev-new
        super().__init__()
        self.setWindowTitle("RePoste")
        self.showFullScreen()

        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.video_feed = QLabel()
        self.video_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
<<<<<<< HEAD
        self.video_feed.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_feed.setStyleSheet("background-color: black;")
        self.main_layout.addWidget(self.video_feed)

        self.scoreboard = ScoreboardWidget()
        self.scoreboard.setFixedHeight(125)
        self.main_layout.addWidget(self.scoreboard, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
=======
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
>>>>>>> origin/sgood-dev-new

        self.settings_button = QPushButton()
        self.settings_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        icon_path = os.path.abspath("../Reposte/images/cog-svgrepo-com.svg")
<<<<<<< HEAD

=======
>>>>>>> origin/sgood-dev-new
        if os.path.exists(icon_path):
            self.settings_button.setIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon not found at {icon_path}")
<<<<<<< HEAD

        self.settings_button.setIconSize(QSize(32, 32))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_window)
        self.main_layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
=======
        self.settings_button.setIconSize(QSize(40, 40))
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.clicked.connect(self.open_settings_window)
        self.main_layout.addWidget(
            self.settings_button,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
>>>>>>> origin/sgood-dev-new

        self.recorder = VideoRecorder()
        self.recorder.start_recording(self.update_frame)

<<<<<<< HEAD
        self.scoreboard_manager = ScoreboardManager()
        self.scoreboard_manager.scoreboard_updated.connect(self.update_scoreboard)
        self.scoreboard_manager.start()
    
=======
        self.scoreboard_manager = scoreboard_manager
        self.scoreboard_manager.scoreboard_updated.connect(
            self.update_scoreboard
        )
        self.scoreboard_manager.start()

>>>>>>> origin/sgood-dev-new
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
<<<<<<< HEAD
            self.recorder.set_replay_speed(round((key - Qt.Key.Key_0) * 0.1, 1)) 
=======
            self.recorder.set_replay_speed(
                round((key - Qt.Key.Key_0) * 0.1, 1)
            )
>>>>>>> origin/sgood-dev-new
        elif key == Qt.Key.Key_Left:
            self.recorder.show_previous_frame()
        elif key == Qt.Key.Key_Right:
            self.recorder.show_next_frame()
        elif key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
<<<<<<< HEAD
                self.showFullScreen()
=======
                self.showFullScreen()
>>>>>>> origin/sgood-dev-new
