import os
import imageio
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime
from typing import Callable, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

#4/23
class RingBuffer: 
    def __init__(self, size: int):
        self.size = size
        self.data = [None] * size
        self.head = 0
        self.full = False

    def append(self, item):
        self.data[self.head] = item
        self.head = (self.head + 1) % self.size
        if self.head == 0:
            self.full = True

    def get_all(self):
        if not self.full:
            return self.data[:self.head]
        return self.data[self.head:] + self.data[:self.head]

    def clear(self):
        self.data = [None] * self.size
        self.head = 0
        self.full = False

class VideoRecorder:
    def __init__(self, fps: int = 60, buffer_duration: int = 5, output_dir: str = "output"):
        self.fps = fps
        buf_size = fps * buffer_duration

        # two ring buffers (4/23)
        self.live_buffer   = RingBuffer(buf_size)
        self.replay_buffer = RingBuffer(buf_size)

        # recording state
        self.recording = False
        self.paused    = False
        self.reader    = None

        # callbacks
        self.live_update_callback: Optional[Callable[[QPixmap], None]] = None
        self.replay_update_callback: Optional[Callable[[QPixmap], None]] = None
        self.update_callback: Optional[Callable[[QPixmap], None]] = None

        # timers
        self.record_timer = QTimer()
        self.record_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.record_timer.timeout.connect(self.capture_frame)

        self.replay_timer = QTimer()
        self.replay_timer.setSingleShot(True)
        self.replay_timer.timeout.connect(self._auto_replay_step)

        # replay state
        self.replaying    = False
        self.replay_index = 0
        self.replay_speed = 1.0

        os.makedirs(output_dir, exist_ok=True)

    def start_recording(self, update_callback: Callable[[QPixmap], None]):
        self.recording = True
        self.paused    = False
        self.reader    = imageio.get_reader("<video0>", "ffmpeg")
        self.live_update_callback = update_callback
        self.update_callback      = update_callback
        # start capturing and timer
        self.capture_frame()
        self.record_timer.start(int(1000 / self.fps))
        logger.info("Recording started.")

    def capture_frame(self):
        if not self.recording or self.paused:
            return
        try:
            frame = self.reader.get_next_data()
            pix   = self._to_pixmap(frame)
            if self.update_callback:
                self.update_callback(pix)
            self.live_buffer.append(frame)
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            self.record_timer.stop()

    def pause_recording(self):
        if self.recording and not self.paused:
            self.paused = True
            self.record_timer.stop()
            logger.info("Recording paused.")

    def resume_recording(self):
        if self.recording and self.paused:
            self.paused = False
            self.record_timer.start(int(1000 / self.fps))
            logger.info("Recording resumed.")

    def stop_recording(self):
        self.recording = False
        self.record_timer.stop()
        if self.reader:
            self.reader.close()
        logger.info("Recording stopped.")

#NEED TO FIX THIS FUNCTION TO WORK AS INTENDED (4/23)
    # def save_replay(self, filename: Optional[str] = None):
    #     frames = self.live_buffer.get_all()
    #     if not filename:
    #         ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #         filename = f"replay_{ts}.mp4"
    #     out = os.path.join(self.output_dir, filename)
    #     try:
    #         with imageio.get_writer(out, fps=self.fps) as w:
    #             for f in frames:
    #                 w.append_data(f)
    #         logger.info(f"Replay saved to {out}")
    #     except Exception as e:
    #         logger.error(f"Failed to save replay: {e}")

    def start_in_app_replay(self, update_callback: Optional[Callable[[QPixmap], None]] = None):
        # Pause live capture before snapshotting
        if self.recording:
            self.pause_recording()

        # snapshot live_buffer into replay_buffer
        self.replay_buffer.clear()
        for frame in self.live_buffer.get_all():
            self.replay_buffer.append(frame)

        self.replay_update_callback = update_callback or self.live_update_callback
        self.update_callback        = self.replay_update_callback

        self.replaying    = True
        self.replay_index = 0
        self.replay_speed = 1.0

        if not self.replay_buffer.get_all():
            logger.warning("No frames to replay.")
            return

        logger.info("Starting in-app replay")
        self._auto_replay_step()

    def _auto_replay_step(self):
        frames = self.replay_buffer.get_all()
        if self.replay_index >= len(frames):
            self.stop_in_app_replay()
            return

        pix = self._to_pixmap(frames[self.replay_index])
        if self.update_callback:
            self.update_callback(pix)

        self.replay_index += 1
        interval = int(1000 / (self.fps * self.replay_speed))
        self.replay_timer.start(interval)

    def show_next_frame(self):
        if not self.replaying:
            return
        if self.replay_timer.isActive():
            self.replay_timer.stop()
        self.replay_index = min(self.replay_index + 1, len(self.replay_buffer.get_all()) - 1)
        self._display_replay_frame()

    def show_previous_frame(self):
        if not self.replaying:
            return
        if self.replay_timer.isActive():
            self.replay_timer.stop()
        self.replay_index = max(self.replay_index - 1, 0)
        self._display_replay_frame()

    def _display_replay_frame(self):
        frames = self.replay_buffer.get_all()
        pix    = self._to_pixmap(frames[self.replay_index])
        if self.update_callback:
            self.update_callback(pix)

    def set_replay_speed(self, speed: float):
        self.replay_speed = speed
        logger.info(f"Replay speed set to {speed}x")
        if self.replaying and self.replay_timer.isActive():
            self.replay_timer.stop()
            interval = int(1000 / (self.fps * self.replay_speed))
            self.replay_timer.start(interval)

    def stop_in_app_replay(self, resume_live: bool = False):
        # Stop the replay timer and exit replay mode
        self.replay_timer.stop()
        self.replaying = False
        logger.info("In-app replay stopped.")
        
        # Restore live‐view callback
        self.update_callback = self.live_update_callback
        
        if resume_live:
            # Clear out the old frames so the next replay only contains new footage
            self.live_buffer.clear()
            self.replay_buffer.clear()
            # Resume recording (reader already open)
            self.resume_recording()

    def _to_pixmap(self, frame) -> QPixmap:
        m = np.fliplr(frame)
        h, w, c = m.shape
        bpl = c * w
        qi = QImage(m.data.tobytes(), w, h, bpl, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qi)
