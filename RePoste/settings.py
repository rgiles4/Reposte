import os
import json
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QDialogButtonBox,
)


class SettingsWindow(QDialog):
    """
    Displays settings information, including camera, microphone,
    keybinds, FPS, and buffer duration, by reading from a config file.
    """

    CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
    CONFIG_FILE = os.path.join(
        CONFIG_DIR, "camera_config.json"
    )  # Adjust path
    CONFIG_FILE = os.path.join(
        CONFIG_DIR, "camera_config.json"
    )  # Adjust path

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
        camera_name = self.config.get("name", "Unknown Camera")
        camera_path = self.config.get("camera_path", "Unknown Path")
        self.camera_label = QLabel(f"{camera_name} ({camera_path})")
        form_layout.addRow("Camera Source:", self.camera_label)

        # Microphone Source (If added to config)
        self.microphone_label = QLabel(
            self.config.get("microphone", "Unknown Microphone")
        )
        self.microphone_label = QLabel(
            self.config.get("microphone", "Unknown Microphone")
        )
        form_layout.addRow("Microphone Source:", self.microphone_label)

        # Keybinds
        self.keybinds_label = QLabel(self.load_keybinds())
        self.keybinds_label.setWordWrap(True)
        form_layout.addRow("Keybinds:", self.keybinds_label)

        # FPS Lock
        self.fps_label = QLabel(str(self.video_recorder.fps))
        form_layout.addRow("FPS Lock:", self.fps_label)

        # Buffer Duration
        buffer_duration = (
            len(self.video_recorder.buffer) // self.video_recorder.fps
        )
        buffer_duration = (
            len(self.video_recorder.buffer) // self.video_recorder.fps
        )
        self.buffer_label = QLabel(str(buffer_duration))
        form_layout.addRow("Buffer Duration (sec):", self.buffer_label)

        layout.addLayout(form_layout)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_config(self):
        """Load configuration from JSON file if it exists."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as file:
                return json.load(file)
        return {}  # Return empty config if file doesn't exist

    def load_keybinds(self):
        """Load keybinds from the config file (or defaults if missing)."""
        keybinds = self.config.get(
            "keybinds",
            {
                "ESC": "Close Program",
                "Space": "Save Replay",
                "P": "Pause Recording",
                "R": "Resume Recording",
                "Up": "Start In-App Replay",
                "Down": "Stop In-App Replay",
                "Left": "Previous Frame",
                "Right": "Next Frame",
                "F11(Fn+F11)": "Toggle Fullscreen",
            },
        )

        return "\n".join(
            [f"{key}: {action}" for key, action in keybinds.items()]
        )
