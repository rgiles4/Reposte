import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QFormLayout,
    QSizePolicy,
)


class Config_Generator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Generator")

        self.cam_combo_box = QComboBox()
        self.audio_combo_box = QComboBox()

        gui_layout = QFormLayout()

        self.cam_combo_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.audio_combo_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        gui_layout.addRow("Select camera", self.cam_combo_box)
        gui_layout.addRow("Select audio device", self.audio_combo_box)

        self.setLayout(gui_layout)
        self.adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
