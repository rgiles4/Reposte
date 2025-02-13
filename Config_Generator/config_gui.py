import sys
from PyQt6.QtWidgets import QApplication, QWidget


class Config_Generator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Generator")
        self.resize(1280, 720)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Config_Generator()
    sys.exit(app.exec())
