import sys
import os
import subprocess
import imageio_ffmpeg
import json
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

        # Get all cameras on device
        self.all_cameras = self.Get_Cameras()

        # Add cameras to dropdown
        for camera in self.all_cameras:
            self.cam_combo_box.addItem(camera["name"])

        # NOTE: Add back if window size is not fixed. Will expand dropdowns to
        # fill the window
        # self.cam_combo_box.setSizePolicy(
        #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        # )
        # self.audio_combo_box.setSizePolicy(
        #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        # )

        self.generate_button = QPushButton("Generate Config")
        self.generate_button.clicked.connect(self.Generate_Config)

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
        cameras_list = []
        # TODO: Add Mac command later
        try:
            video_devices_found = False
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            # print(f"FFmpeg path: {ffmpeg_path}")

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

            # Go through each line and extract camera info
            lines = output.split("\n")
            for i, line in enumerate(lines):
                # Check for DirectShow video devices section in ffmpeg
                if "DirectShow video devices" in line:
                    video_devices_found = True
                    continue

                if video_devices_found:
                    # Find lines with camera names by ('"')
                    # (may not be robust)
                    if '"' in line:
                        camera_name = line.split('"')[1]

                        # Check the next line for the camera path
                        if i + 1 < len(lines) and '"' in lines[i + 1]:
                            camera_path = lines[i + 1].split('"')[1]

                            # Append the camera info to the list
                            cameras_list.append(
                                {
                                    "name": camera_name,
                                    "camera_path": camera_path,
                                }
                            )

                    # When at "DirectShow audio devices", stop processing
                    if "DirectShow audio devices" in line:
                        break
            # print(cameras_list)

        except Exception as e:
            print(f"Failed to get cameras:\n {e}")
        return cameras_list

    def Generate_Config(self):
        # Get the selected camera
        selected_camera_name = self.cam_combo_box.currentText()

        # Find the camera data in the list
        selected_camera = next(
            (
                camera
                for camera in self.all_cameras
                if camera["name"] == selected_camera_name
            ),
            None,
        )

        if selected_camera:
            # Get the camera path
            camera_data = {
                "name": selected_camera["name"],
                "camera_path": selected_camera["camera_path"],
            }

            # Create a config file and write the camera data to it
            config_file_path = os.path.join(os.getcwd(), "camera_config.json")
            with open(config_file_path, "w") as config_file:
                json.dump(camera_data, config_file, indent=4)

            print(f"Config file saved at: {config_file_path}")
        else:
            print("Selected camera not found.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Config_Generator()
    window.show()
    sys.exit(app.exec())
