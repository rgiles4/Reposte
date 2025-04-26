import os
import imageio
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
from collections import deque
from datetime import datetime
import logging
from typing import Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class VideoRecorder:
    def __init__(
        self,
        fps: int = 60,
        buffer_duration: int = 5,
        output_dir: str = "output",
    ):
        self.fps = fps
        self.buffer = deque(
            maxlen=fps * buffer_duration,
        )
        self.output_dir = output_dir
        self.recording = False
        self.paused = False
        self.reader = None
        self.update_callback = None
        self.replaying = False
        self.replay_frames = []
        self.replay_index = 0
        self.replay_timer = None
        self.replay_speed = 1.0

        os.makedirs(output_dir, exist_ok=True)

    def start_recording(self, update_callback: Callable[[QPixmap], None]):
        try:
            self.recording = True
            self.paused = False
            self.update_callback = update_callback

            # Try initializing with imageio first
            self.reader = imageio.get_reader("<video1>", "ffmpeg")
            logger.info("Successfully initialized video with imageio.")

            self.capture_frame()
            logger.info("Recording started.")
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.recording = False

    def capture_frame(self):
        if not self.recording or self.paused:
            return
        try:
            frame = self.reader.get_next_data()
            pixmap = self.convert_frame_to_pixmap(frame)
            self.update_callback(pixmap)
            self.buffer.append(frame)
            QTimer.singleShot(int(1000 / self.fps), self.capture_frame)
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")

    def pause_recording(self):
        if self.recording:
            self.paused = True
            logger.info("Recording paused.")

    def resume_recording(self):
        if self.recording and self.paused:
            self.paused = False
            self.capture_frame()
            logger.info("Recording resumed.")

    def stop_recording(self):
        self.recording = False
        if self.reader:
            self.reader.close()
            self.reader.close()
        logger.info("Recording stopped.")

    def save_replay(self, filename: Optional[str] = None):
        if not filename:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"replay_{timestamp}.mp4"

        output_path = os.path.join(self.output_dir, filename)
        try:
            with imageio.get_writer(output_path, fps=self.fps) as writer:
                for frame in self.buffer:
                    writer.append_data(frame)
            logger.info(f"Replay saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save replay: {e}")

    def set_buffer_duration(self, duration: int):
        self.buffer = deque(maxlen=self.fps * duration)
        logger.info(f"Buffer duration set to {duration} seconds.")

    def start_in_app_replay(
        self, update_callback: Optional[Callable[[QPixmap], None]] = None
    ):
        if self.recording:
            self.stop_recording()

        self.replaying = True
        self.replay_speed = 1.0
        self.replay_index = 0
        self.replay_frames = list(self.buffer)
        self.update_callback = update_callback or self.update_callback

        if not self.replay_frames:
            logger.warning("No frames in buffer to replay.")
            return

        logger.info(
            f"Starting in-app replay of {len(self.replay_frames)} frames."
        )
        self.show_replay_frame()

    def show_replay_frame(self):
        if not self.replaying and (
            self.replay_index < 0
            or self.replay_index >= len(self.replay_frames)
        ):
            return

        frame = self.replay_frames[self.replay_index]
        pixmap = self.convert_frame_to_pixmap(frame)
        if self.update_callback:
            self.update_callback(pixmap)

        if self.replaying:
            self.replay_index += 1
        if self.replay_index >= len(self.replay_frames):
            self.stop_in_app_replay()
        else:
            self.replay_timer = QTimer()
            self.replay_timer.setSingleShot(True)
            self.replay_timer.timeout.connect(self.show_replay_frame)
            self.replay_timer.start(
                int(1000 / (self.fps * self.replay_speed))
            )

    def show_next_frame(self):
        if self.replaying:
            self.replaying = False
            if self.replay_timer:
                self.replay_timer.stop()

        if self.replay_index < len(self.replay_frames) - 1:
            self.replay_index += 1
            self.show_replay_frame()
        else:
            logger.info("At the last frame of the replay.")

    def show_previous_frame(self):
        if self.replaying:
            self.replaying = False
            if self.replay_timer:
                self.replay_timer.stop()

        if self.replay_index > 0:
            self.replay_index -= 1
            self.show_replay_frame()
        else:
            logger.info("At the first frame of the replay.")

    def set_replay_speed(self, speed: float):
        self.replay_speed = speed
        logger.info(f"Replay speed set to {speed}x.")

    def stop_in_app_replay(self, resume_live: bool = False):
        if self.replay_timer is not None:
            self.replay_timer.stop()
            self.replay_timer = None
        self.replaying = False
        self.replay_frames = []
        self.replay_index = 0
        logger.info("In-app replay stopped.")
        if resume_live:
            self.start_recording(self.update_callback)

    def convert_frame_to_pixmap(self, frame) -> QPixmap:
        mirrored_frame = np.fliplr(frame)

        height, width, channel = mirrored_frame.shape
        bytes_per_line = channel * width
        qt_image = QImage(
            mirrored_frame.data.tobytes(),
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(qt_image)
