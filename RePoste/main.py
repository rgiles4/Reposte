import sys
from PyQt6.QtWidgets import QApplication

# from RePoste.gui import MainWindow for tests
from gui import MainWindow
from scoreboard_manager import ScoreboardManager
        
<<<<<<< HEAD
        
=======
>>>>>>> origin/sgood-dev-new
if __name__ == "__main__":
    # Initialize the QApplication
    app = QApplication([])
<<<<<<< HEAD

    # Create an instance of ScoreboardManager and start it
    scoreboard_mgr = ScoreboardManager()
    scoreboard_mgr.start()

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Connect the scoreboard_updated signal to the on_scoreboard_data function
    # scoreboard_mgr.scoreboard_updated.connect(on_scoreboard_data)

    # Start the Qt event loop
    exit_code = app.exec()

    # Stop the ScoreboardManager when the application exits
    scoreboard_mgr.stop()
    sys.exit(exit_code)
=======
    
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
>>>>>>> origin/sgood-dev-new
