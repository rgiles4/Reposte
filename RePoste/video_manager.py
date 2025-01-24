import os
import imageio
import numpy as np 
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt
from collections import deque
from datetime import datetime
import logging
from typing import Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

class VideoRecorder:
    def __init__(self, fps: int = 60, buffer_duration: int = 5, output_dir: str = "output"):
        """
        Initializes the VideoRecorder.
        Args:
            fps (int): Frames per second for video capture.
            buffer_duration (int): Duration (in seconds) of the buffer.
            output_dir (str): Directory to save replays.
        """
        self.fps = fps
        self.buffer = deque(maxlen=fps * buffer_duration)
        self.output_dir = output_dir
        self.recording = False
        self.paused = False
        self.reader = None

        # For in-app replay
        self.replaying = False
        self.replay_frames = []
        self.replay_index = 0
        self.replay_timer = None

        # Callback used both for live and replay display
        self.update_callback = None

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def start_recording(self, update_callback: Callable[[QPixmap], None]):
        """
        Starts capturing video and updating the GUI.
        Args:
            update_callback (Callable[[QPixmap], None]): Function to update the video feed in the GUI.
        """
        try:
            self.recording = True
            self.paused = False
            self.reader = imageio.get_reader("<video0>", "ffmpeg")
            self.update_callback = update_callback
            self._capture_frame()
            logger.info("Recording started.")
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.recording = False

    def _capture_frame(self):
        """Captures a single frame and updates the GUI."""
        if not self.recording or self.paused:
            return
        try:
            frame = self.reader.get_next_data()
            pixmap = self._convert_frame_to_pixmap(frame)
            self.update_callback(pixmap)
            self.buffer.append(frame)
            QTimer.singleShot(int(1000 / self.fps), self._capture_frame)
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")

    def pause_recording(self):
        """Pauses the recording."""
        if self.recording:
            self.paused = True
            logger.info("Recording paused.")

    def resume_recording(self):
        """Resumes the recording."""
        if self.recording and self.paused:
            self.paused = False
            self._capture_frame()
            logger.info("Recording resumed.")

    def stop_recording(self):
        """Stops the recording."""
        self.recording = False
        if self.reader:
            self.reader.close()
        logger.info("Recording stopped.")

    def save_replay(self, filename: Optional[str] = None):
        """
        Saves the buffered frames as a video file.
        Args:
            filename (str): The name of the saved replay file. If None, generates a timestamp-based name.
        """
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
        """
        Adjusts the buffer duration and resets the buffer.
        Args:
            duration (int): The new buffer duration in seconds.
        """
        self.buffer = deque(maxlen=self.fps * duration)
        logger.info(f"Buffer duration set to {duration} seconds.")

    def start_in_app_replay(self, update_callback: Optional[Callable[[QPixmap], None]] = None):
        """
        Plays back the frames currently in 'self.buffer' in the same GUI widget.
        Args:
            update_callback (callable): A function to display frames (QPixmap) in the GUI.
                                        If None, uses self.update_callback from live capture.
        """
        if self.recording:
            self.stop_recording()

        self.replaying = True
        self.replay_index = 0
        self.replay_frames = list(self.buffer)
        self.update_callback = update_callback or self.update_callback

        if not self.replay_frames:
            logger.warning("No frames in buffer to replay.")
            return

        logger.info(f"Starting in-app replay of {len(self.replay_frames)} frames.")
        self._show_replay_frame()

    def _show_replay_frame(self):
        """Displays a single frame from self.replay_frames by index."""
        if not self.replaying:
            return

        if self.replay_index >= len(self.replay_frames):
            self.stop_in_app_replay()
            return

        frame = self.replay_frames[self.replay_index]
        self.replay_index += 1

        pixmap = self._convert_frame_to_pixmap(frame)
        if self.update_callback:
            self.update_callback(pixmap)

        self.replay_timer = QTimer()
        self.replay_timer.setSingleShot(True)
        self.replay_timer.timeout.connect(self._show_replay_frame)
        self.replay_timer.start(int(1000 / self.fps))

    def stop_in_app_replay(self, resume_live: bool = False):
        """Stops the in-app replay and clears replay variables."""
        if self.replay_timer is not None:
            self.replay_timer.stop()
            self.replay_timer = None
        self.replaying = False
        self.replay_frames = []
        self.replay_index = 0
        logger.info("In-app replay stopped.")
        if resume_live:
            self.start_recording(self.update_callback)

    def _convert_frame_to_pixmap(self, frame) -> QPixmap:
        """Converts a frame to QPixmap and mirrors it horizontally."""
        # Mirror the frame horizontally using NumPy
        mirrored_frame = np.fliplr(frame)

        h, w, ch = mirrored_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(mirrored_frame.data.tobytes(), w, h, bytes_per_line, QImage.Format.Format_RGB888)
        scaled_width = int(w * 2)
        scaled_height = int(h * 2)
        scaled_image = qt_image.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(scaled_image)
