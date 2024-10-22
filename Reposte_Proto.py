import cv2
from tkinter import *
from PIL import ImageTk, Image

# Global variables handling state and webcam playback
cap = None
is_recording = False
fps = 60
max_frames = 4 * fps  
buffer = []

def update_frame():
    # Get global state variables to handle webcam and frames
    global cap, is_recording, buffer, video_feed  

    # When recording is true, continue to update frames
    if is_recording:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't receive frame (stream end?). Exiting...")
            return

        # Show color in webcam
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Format for tkinter
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        # Display the current frame in the label
        video_feed.imgtk = imgtk 
        video_feed.configure(image=imgtk) 

        # Store frames in buffer (For last 4 seconds playback when implemented)
        buffer.append(frame)
        # if len(buffer) > max_frames:
        #     buffer.pop(0)

        # Start the next frame
        video_feed.after(int(1000 / fps), update_frame)

def play_video():
    #Get global variables to handle state
    global cap, is_recording, buffer

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # When the start button is hit, clear buffer and start recording
    is_recording = True
    buffer.clear()
    print("Recording started.")

    # Start updating frames
    update_frame()

def main():

    #Find global variables to handle state (Best option I could find for now)
    global cap, is_recording, buffer, video_feed  

    window = Tk()

    window_width = 800
    window_height = 600
    window.geometry(f"{window_width}x{window_height}")

    window.title("Reposte (Prototype)")

    # GUI for buttons and video playback
    video_feed = Label(window, bg="black")
    play_button = Button(window, text="Play", width=10, height=2, command=play_video)
    stop_button = Button(window, text="Stop", width=10, height=2)
    replay_button = Button(window, text="Replay", width=10, height=2)

    # Elements laid out on screen in grid format, easy to adjust if needed
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(3, weight=1)
    video_feed.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

    play_button.grid(row=2, column=0, padx=10, pady=10, sticky="sw")
    stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="sw")
    replay_button.grid(row=2, column=2, padx=10, pady=10, sticky="sw") 

    window.mainloop()

main()


