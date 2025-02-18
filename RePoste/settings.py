import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFormLayout, QDialogButtonBox
)


class SettingsWindow(QDialog):
    """
    Displays settings information, including camera, microphone,
    keybinds, FPS, and buffer duration, by reading from a config file.
    """

    CONFIG_FILE = "config.json"  # Path to config if config is named this

    def __init__(self, video_recorder):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        self.video_recorder = video_recorder

        # Load config settings
        self.config = self.load_config()

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Camera Source
        self.camera_label = QLabel(self.config.get("camera_source", 
                                                   "Unknown Camera"))
        form_layout.addRow("Camera Source:", self.camera_label)

        # Microphone Source
        self.microphone_label = QLabel(self.config.get("microphone_source", 
                                                       "Unknown Microphone"))
        form_layout.addRow("Microphone Source:", self.microphone_label)

        # Keybinds
        self.keybinds_label = QLabel(self.load_keybinds())
        self.keybinds_label.setWordWrap(True)
        form_layout.addRow("Keybinds:", self.keybinds_label)

        # FPS Lock
        self.fps_label = QLabel(str(self.video_recorder.fps))
        form_layout.addRow("FPS Lock:", self.fps_label)

        # Buffer Duration
        self.buffer_label = QLabel(str(len(self.video_recorder.buffer) //
                                       self.video_recorder.fps))
        form_layout.addRow("Buffer Duration (sec):", self.buffer_label)

        layout.addLayout(form_layout)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_config(self):
        """Load configuration from a JSON file."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as file:
                return json.load(file)
        return {}  # Return empty config if file doesn't exist

    def load_keybinds(self):
        """
        Load keybinds from the config file
        (Currently using our discussed binds until I work with config file)
        """
        keybinds = self.config.get("keybinds", {
            "Space": "Save Replay",
            "P": "Pause Recording",
            "R": "Resume Recording",
            "Up": "Start In-App Replay",
            "Down": "Stop In-App Replay",
            "Left": "Previous Frame",
            "Right": "Next Frame",
            "F11": "Toggle Fullscreen",
        })

        return "\n".join([f"{key}: {action}"
                          for key, action in keybinds.items()])
