
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

        # Convert to RGB for displaying in tkinter and for consistent saving
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        video_feed.imgtk = imgtk 
        video_feed.configure(image=imgtk) 

        # Append the RGB frame for consistency with imageio
        buffer.append(frame_rgb)
        if len(buffer) > max_frames:
            buffer.pop(0)

        video_feed.after(int(1000 / fps), update_frame)

def play_video():
    global cap, is_recording, buffer

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

    is_recording = False
    if cap:
        cap.release()

    video_feed.configure(image="")
    print("Recording stopped.")

def replay_video():
    global buffer

    # Ensure the video path is writable and create an output file
    video_path = os.path.join(os.getcwd(), "Video-Output.mp4")
    
    # Save video with specified FPS and color adjustment
    with imageio.get_writer(video_path, fps=fps) as writer:
        for frame in buffer:
            writer.append_data(frame)  # buffer is already in RGB format

    print("Replay saved at:", video_path)

def main():
    global video_feed  

    ctk.set_appearance_mode("dark")
    window = ctk.CTk()
    window.geometry("800x600")
    window.title("Reposte (Prototype)")

    video_feed = ctk.CTkLabel(window, text="", fg_color="black")
    play_button = ctk.CTkButton(window, text="Play", width=10, height=2, command=play_video)
    stop_button = ctk.CTkButton(window, text="Stop", width=10, height=2, command=stop_video)
    replay_button = ctk.CTkButton(window, text="Replay", width=10, height=2, command=replay_video)

    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure((0, 1, 2), weight=1)
    video_feed.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

    play_button.grid(row=2, column=0, padx=10, pady=10, sticky="sw")
    stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="sw")
    replay_button.grid(row=2, column=2, padx=10, pady=10, sticky="sw")

    window.mainloop()

main()

