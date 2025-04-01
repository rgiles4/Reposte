import sys
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
from scoreboard_manager import ScoreboardManager
        
        
if __name__ == "__main__":
    # Initialize the QApplication
    app = QApplication([])

    # Create an instance of ScoreboardManager and start it
    scoreboard_mgr = ScoreboardManager()
    scoreboard_mgr.start()

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the Qt event loop
    try:
        exit_code = app.exec()
    finally:
        # Stop the ScoreboardManager when the application exits
        scoreboard_mgr.stop()
        sys.exit(exit_code)