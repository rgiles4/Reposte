import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from scoreboard_manager import ScoreboardManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create one instance of ScoreboardManager
    scoreboard_mgr = ScoreboardManager()
    
    # Pass the instance to MainWindow (modify MainWindow to accept it)
    window = MainWindow(scoreboard_manager=scoreboard_mgr)
    window.show()
    
    try:
        exit_code = app.exec()
    finally:
        scoreboard_mgr.stop()
        sys.exit(exit_code)
