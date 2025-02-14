import sys
import subprocess
import imageio_ffmpeg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QFormLayout,
    QPushButton,
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

        all_cameras = self.Get_Cameras()

        # NOTE: Add back if window size is not fixed. Will expand dropdowns to
        # fill the window
        # self.cam_combo_box.setSizePolicy(
        #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        # )
        # self.audio_combo_box.setSizePolicy(
        #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        # )

        self.generate_button = QPushButton("Generate Config")

        gui_layout.addRow("Select camera", self.cam_combo_box)
        gui_layout.addRow("Select audio device", self.audio_combo_box)
        gui_layout.addWidget(self.generate_button)

        self.setLayout(gui_layout)

    def Get_Cameras(self):
        cameras = []
        # TODO: Add Mac command later
        try:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            print(f"FFmpeg path: {ffmpeg_path}")

            if sys.platform == "win32":
                command = [
                    ffmpeg_path,
                    "-list_devices",
                    "true",
                    "-f",
                    "dshow",
                    "-i",
                    "dummy",
                ]

            command_result = subprocess.run(
                command, capture_output=True, text=True
            )
            output = command_result.stderr
            print(output)

            # if sys.platform == "win32":

        except Exception as e:
            print(f"AYYY YO Command failed:\n {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
