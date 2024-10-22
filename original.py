# # Open webcam
# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("Error: Could not open webcam.")
#     exit()

# # Set FPS and resolution (optional, change as per need)
# fps = 60
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# # Create a list to store frames (with a fixed length to store the last 4 seconds of footage)
# buffer = []
# max_frames = 4 * fps  # 4 seconds of footage

# print("Recording started. Press SPACE to stop and replay last 4 seconds...")

# while cap.isOpened():
#     ret, frame = cap.read()

#     if not ret:
#         print("Error: Couldn't receive frame (stream end?). Exiting...")
#         break

#     # Display the live feed
#     cv2.imshow('Live Video', frame)

#     # Store frame in buffer (keep only the last 4 seconds)
#     buffer.append(frame)
#     if len(buffer) > max_frames:
#         buffer.pop(0)

#     # Check for spacebar press to stop recording
#     if cv2.waitKey(1) & 0xFF == ord(' '):
#         print("Spacebar pressed. Stopping recording...")
#         break

# # Release the webcam
# cap.release()
# cv2.destroyAllWindows()

# # Replay the last 4 seconds of recorded footage
# print("Replaying the last 4 seconds...")
# for frame in buffer:
#     cv2.imshow('Playback', frame)
#     if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
#         break

# # Close all OpenCV windows
# cv2.destroyAllWindows()