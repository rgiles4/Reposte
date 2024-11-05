import cv2
from PIL import Image, ImageTk
import customtkinter as ctk
import os
import imageio

# Global variables for webcam playback and state
cap = None
is_recording = False
fps = 30
max_frames = 4 * fps
buffer = []


def update_frame():
    global cap, is_recording, buffer, video_feed

    if is_recording:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't receive frame (stream end?). Exiting...")
            return

        # Convert to RGB for displaying in tkinter and render frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        video_feed.imgtk = imgtk
        video_feed.configure(image=imgtk)

        # Append the RGB frame to the buffer
        buffer.append(frame_rgb)
        if len(buffer) > max_frames:
            buffer.pop(0)

        video_feed.after(int(1000 / fps), update_frame)


def play_video():
    global cap, is_recording, buffer

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    is_recording = True
    buffer.clear()
    print("Recording started.")
    update_frame()


def stop_video():
    global is_recording, cap

    # Clear cap when stop is hit
    is_recording = False
    if cap:
        cap.release()
        cap = None

    video_feed.configure(image="")
    print("Recording stopped.")


def replay_video():
    global buffer

    # Ensure the video path is writable and create an output file
    video_path = os.path.join(os.getcwd(), "Video-Output.mp4")

    # Save video with specified FPS and color adjustment
    with imageio.get_writer(video_path, fps=fps) as writer:
        for frame in buffer:
            writer.append_data(frame)

    print("Replay saved at:", video_path)


def main():
    global video_feed, window

    # Set up GUI
    ctk.set_appearance_mode("dark")
    window = ctk.CTk()
    window.geometry("800x600")
    window.title("Reposte (Prototype)")

    video_feed = ctk.CTkLabel(window, text="", fg_color="black")
    play_button = ctk.CTkButton(
        window,
        text="Play",
        text_color="black",
        font=("tahoma", 12, "bold"),
        width=120,
        height=40,
        command=play_video,
        fg_color="darkseagreen",
        hover_color="darkgreen",
    )
    stop_button = ctk.CTkButton(
        window,
        text="Stop",
        text_color="black",
        font=("tahoma", 12, "bold"),
        width=120,
        height=40,
        command=stop_video,
        fg_color="indianred",
        hover_color="maroon",
    )

    replay_button = ctk.CTkButton(
        window,
        text="Replay",
        text_color="black",
        font=("tahoma", 12, "bold"),
        width=120,
        height=40,
        command=replay_video,
        fg_color="coral",
        hover_color="orangered",
    )

    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure((0, 1, 2), weight=1)

    video_feed.grid(
        row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=(10, 20)
    )

    play_button.grid(row=2, column=0, padx=10, pady=(5, 20), sticky="s")
    stop_button.grid(row=2, column=1, padx=10, pady=(5, 20), sticky="s")
    replay_button.grid(row=2, column=2, padx=10, pady=(5, 20), sticky="s")

    window.mainloop()


main()
