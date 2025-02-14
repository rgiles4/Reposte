import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QFormLayout,
    QSizePolicy,
    QPushButton,
    QHBoxLayout,
)


class Config_Generator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Generator")
        self.setFixedSize(400, 150)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #808080;
            }
            QComboBox {
                background-color: #636363;
            }
            QPushButton {
                min-width: 100px;
                min-height: 30px;
                background-color: #636363;
                margin-top: 30px;
            }
            """
        )

        self.cam_combo_box = QComboBox()
        self.audio_combo_box = QComboBox()

        gui_layout = QFormLayout()

        self.cam_combo_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.audio_combo_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        self.generate_button = QPushButton("Generate Config")

        gui_layout.addRow("Select camera", self.cam_combo_box)
        gui_layout.addRow("Select audio device", self.audio_combo_box)
        gui_layout.addWidget(self.generate_button)

        self.setLayout(gui_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
