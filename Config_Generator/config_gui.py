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
        self.setFixedSize(500, 160)

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
        gui_layout.addRow("Select microphone", self.audio_combo_box)
        gui_layout.addWidget(self.generate_button)

        self.setLayout(gui_layout)

        self.setStyleSheet(
            """
        QWidget {
            background-color: #ffffff;
            font-family: 'Poppins', Arial, sans-serif;
            font-size: 14px;
            color: #333;
        }

        QComboBox {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 5px;
        }
        
        QComboBox:hover {
            background-color: #e0e0e0;
        }

        QComboBox::drop-down {
            border: none;
            background: transparent;
        }

        QComboBox::down-arrow {
            image: url(images/caret-down-solid.svg);
            width: 18px;
            height: 18px;
        }

        QPushButton {
            min-width: 120px;
            min-height: 35px;
            background-color: #0078D4;
            color: #fff;
            margin-top: 25px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #005fa3;
        }

        QPushButton:pressed {
            background-color: #004a82;
        }
        """
        )

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
            # print(output)

            for line in output.split("/n"):
                line = line.strip()
                print(line)
                # cameras.append(line)

            # if sys.platform == "win32":

        except Exception as e:
            print(f"AYYY YO We Failed:\n {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
