import cv2
from tkinter import *
from PIL import ImageTk, Image
import os

# Global variables handling state and webcam playback
cap = None
is_recording = False
fps = 30
max_frames = 4 * fps  
buffer = []

def update_frame():
    global cap, is_recording, buffer, video_feed  

    #Update at each frame for video feed at 30 fps
    if is_recording:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't receive frame (stream end?). Exiting...")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        video_feed.imgtk = imgtk 
        video_feed.configure(image=imgtk) 

        buffer.append(frame)
        if len(buffer) > max_frames:
            buffer.pop(0)

        video_feed.after(int(1000 / fps), update_frame)

def play_video():
    global cap, is_recording, buffer

    #Play the video when the play button is hit
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

    #set is_recording to false when stop button is hit
    is_recording = False
    if cap:
        cap.release()

    video_feed.configure(image="")
    print("Recording stopped.")


def replay_video():
    global buffer

    # Create a video path for saving a reaply
    video_path = os.path.join(os.getcwd(), "Video-Output")
    height, width, layers = buffer[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Match video with fps for saving replays
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # Take each frame from the buffer and make a 4 sec replay
    for frame in buffer:
        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    out.release()
    print("Replay saved at: ", video_path)

def main():
    global video_feed  

    #Creating a tkinter window for app
    window = Tk()
    window_width = 800
    window_height = 600
    window.geometry(f"{window_width}x{window_height}")
    window.title("Reposte (Prototype)")

    video_feed = Label(window, bg="black")
    play_button = Button(window, text="Play", width=10, height=2, command=play_video)
    stop_button = Button(window, text="Stop", width=10, height=2, command=stop_video)  
    replay_button = Button(window, text="Replay", width=10, height=2, command=replay_video)

    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(3, weight=1)
    video_feed.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    play_button.grid(row=2, column=0, padx=10, pady=10, sticky="sw")
    stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="sw")
    replay_button.grid(row=2, column=2, padx=10, pady=10, sticky="sw") 

    window.mainloop()

main()
