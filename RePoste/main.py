import sys
from PyQt6.QtWidgets import QApplication

# from RePoste.gui import MainWindow for tests
from gui import MainWindow
from scoreboard_manager import ScoreboardManager

#Lot of work needed: on_scoreboard_data.
# For example, to detect touches:
    # lamp_bits = data.get("lamp_bits", 0)
    # left_white_on = bool(lamp_bits & 0x01)
    # right_white_on = bool(lamp_bits & 0x02)
    # if left_white_on or right_white_on:
    #     print("Touch detected -- saving replay!")
    #     window.recorder.save_replay()
    #     window.recorder.start_in_app_replay()

def on_scoreboard_data(data):
    if not data:
        print("Scoreboard offline or no data detected.")
        return
    print("Scoreboard updated:", data)

if __name__ == "__main__":
    app = QApplication([])
    scoreboard_mgr = ScoreboardManager()
    scoreboard_mgr.start()

    window = MainWindow()
    window.show()

    # scoreboard_mgr.scoreboard_updated.connect(on_scoreboard_data)
    exit_code = app.exec()
    scoreboard_mgr.stop()
    sys.exit(exit_code)