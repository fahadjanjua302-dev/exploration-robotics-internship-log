"""
Exploration Robotics Internship - Tello Drone YOLO11n Real-Time Object Detection.

This script hooks into the Tello drone's live H.264 video stream, pulls decoded frames 
directly from the background memory buffer, feeds them into a local YOLO11n computer 
vision model, and presents the annotated results inside a native OpenCV GUI frame window.
"""

import cv2
from djitellopy import Tello
from ultralytics import YOLO

# 1. Initialize the YOLO11 Nano neural network model instance
model = YOLO("yolo11n.pt")

# 2. Establish connection sockets with the Tello drone hardware
drone = Tello()
drone.connect()
print(f"[BOOT] Connected. Battery Capacity: {drone.get_battery()}%")

# 3. Fire up the onboard camera video transmission stream
drone.streamon()

# Initialize the background PyAV decoding stream listener thread 
frame_reader = drone.get_frame_read()

print("\n=======================================================")
print("  TELLO AIRBORNE YOLO11n DETECTION PIPELINE ONLINE     ")
print("=======================================================")
print("  Press 'q' in the video viewport window to exit...    ")
print("=======================================================\n")

while True:
    # 4. Fetch the raw frame matrix array out of the network stream buffer
    raw_frame = frame_reader.frame

    # [COLOR CORRECTION] Tello decodes to RGB, but OpenCV maps pixels in BGR layout.
    # We convert the color space layout before sending the array to the network layer.
    bgr_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

    # 5. Compute neural inference tracking maps over the live drone matrix frame
    # stream=True optimizes internal GPU/CPU caching for streaming sequences.
    # verbose=False suppresses logging clutter to save CPU cycles.
    results = model(bgr_frame, stream=True, verbose=False)

    # Extract target annotations from the output collection object generator
    for result in results:
        # Instantly render standard bounding boxes and category text tags
        annotated_frame = result.plot()

    # 6. Flush the compiled image matrix arrays to the desktop view screen
    cv2.imshow("Tello Drone Live Vision Tracker - YOLO11n", annotated_frame)

    # Break loop safely if user presses the 'q' key in focus
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[EXIT] Disarming detection framework loops...")
        break

# =========================================================================
# Resource Cleanup Protocol
# =========================================================================
cv2.destroyAllWindows()
drone.streamoff()
print("[SHUTDOWN] Video capture streams disconnected. Safe teardown completed.")