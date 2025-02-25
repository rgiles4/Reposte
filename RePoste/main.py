import sys
from PyQt6.QtWidgets import QApplication

# from RePoste.gui import MainWindow for tests
from RePoste.gui import MainWindow


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
