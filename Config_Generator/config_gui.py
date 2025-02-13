import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QVBoxLayout,
)


class Config_Generator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Generator")
        self.resize(600, 300)

        self.camera_label = QLabel("Select Camera")
        self.cam_combo_box = QComboBox(self)

        self.audio_label = QLabel("Select audio device")
        self.audio_combo_box = QComboBox(self)

        gui_layout = QVBoxLayout()
        gui_layout.addWidget(self.camera_label)
        gui_layout.addWidget(self.cam_combo_box)
        gui_layout.addWidget(self.audio_label)
        gui_layout.addWidget(self.audio_combo_box)

        self.setLayout(gui_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
