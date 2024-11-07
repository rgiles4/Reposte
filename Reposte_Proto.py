import cv2
from PIL import Image
from customtkinter import CTkImage
import customtkinter as ctk
import os
import imageio


class VideoRecorderApp:
    def __init__(self, fps=30):
        self.width = 800
        self.height = 600
        self.cap = None
        self.is_recording = False
        self.fps = fps
        self.max_frames = 4 * fps
        self.buffer = []
        self.recording_num = 0
        self.video_feed = None
        self.window = None
        self.setup_gui()

    def setup_gui(self):
        ctk.set_appearance_mode("dark")
        self.window = ctk.CTk()
        self.window.geometry(f"{self.width}x{self.height}")
        self.window.title("Reposte (Prototype)")

        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure((1, 2, 3), weight=1)

        # Top Frame for save location
        self.top_frame = ctk.CTkFrame(
            self.window, height=(self.height / 16), width=(self.width)
        )
        self.top_frame.grid(
            row=0, column=1, columnspan=3, sticky="n", pady=(5, 10), padx=(10, 10)
        )

        # Video feed display area
        self.video_feed = ctk.CTkLabel(self.window, text="", fg_color="black")
        self.video_feed.grid(
            row=1,
            column=1,
            rowspan=2,
            columnspan=3,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

        # Side frame for buttons
        self.side_frame = ctk.CTkFrame(
            self.window, width=(self.width / 4), height=self.height, corner_radius=5
        )
        self.side_frame.grid(row=0, column=0, rowspan=3, sticky="ns", pady=5)

        # Control buttons
        play_button = ctk.CTkButton(
            self.side_frame,
            text="Play",
            text_color="black",
            font=("tahoma", 12, "bold"),
            width=120,
            height=40,
            command=self.play_video,
            fg_color="darkseagreen",
            hover_color="darkgreen",
        )
        stop_button = ctk.CTkButton(
            self.side_frame,
            text="Stop",
            text_color="black",
            font=("tahoma", 12, "bold"),
            width=120,
            height=40,
            command=self.stop_video,
            fg_color="indianred",
            hover_color="maroon",
        )
        replay_button = ctk.CTkButton(
            self.side_frame,
            text="Replay",
            text_color="black",
            font=("tahoma", 12, "bold"),
            width=120,
            height=40,
            command=self.save_replay,
            fg_color="coral",
            hover_color="orangered",
        )

        # Layout configuration for buttons
        play_button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        stop_button.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nw")
        replay_button.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="nw")

        self.window.mainloop()

    def update_frame(self):
        if self.is_recording:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Couldn't receive frame (stream end?). Exiting...")
                return

            # Convert frame to RGB and display in tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = CTkImage(dark_image=img, size=(self.width, self.height))
            self.video_feed.imgtk = imgtk
            self.video_feed.configure(image=imgtk)

            # Add frame to buffer
            self.buffer.append(frame_rgb)
            if len(self.buffer) > self.max_frames:
                self.buffer.pop(0)

            self.video_feed.after(int(1000 / self.fps), self.update_frame)

    def play_video(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        self.is_recording = True
        self.buffer.clear()
        print("Recording started.")
        self.update_frame()

    def stop_video(self):
        self.is_recording = False
        if self.cap:
            self.cap.release()
            self.cap = None

        self.video_feed.configure(image="")
        print("Recording stopped.")

    def save_replay(self):
        video_path = os.path.join(os.getcwd(), f"Video-Output{self.recording_num}.mp4")

        with imageio.get_writer(video_path, fps=self.fps) as writer:
            for frame in self.buffer:
                writer.append_data(frame)

        print("Replay saved at:", video_path)
        self.recording_num += 1
        self.play_replay(video_path)

    def play_replay(self, video_path):
        replay_window = ctk.CTkToplevel(self.window)
        replay_window.geometry(f"{self.width}x{self.height}")
        replay_window.title(f"Video Replay: {video_path}")
        replay_window.attributes("-topmost", True)

        replay_window.grid_rowconfigure(1, weight=1)
        replay_window.grid_columnconfigure(0, weight=1)

        video_feed_replay = ctk.CTkLabel(replay_window, text="", fg_color="black")
        video_feed_replay.grid(
            row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=(10, 20)
        )

        cap_replay = cv2.VideoCapture(video_path)

        def update_replay_frame():
            ret, frame = cap_replay.read()
            if not ret:
                print("Replay ended.")
                cap_replay.release()
                replay_window.destroy()
                return

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = CTkImage(dark_image=img, size=(self.width, self.height))

            video_feed_replay.imgtk = imgtk
            video_feed_replay.configure(image=imgtk)

            video_feed_replay.after(int(1000 / self.fps), update_replay_frame)

        update_replay_frame()


if __name__ == "__main__":
    app = VideoRecorderApp(fps=30)
