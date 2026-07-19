"""
Exploration Robotics Internship - Real-Time YOLO11n Object Detection Engine.

This script opens the laptop's primary video device, passes the frame data to a local 
YOLO11n neural network instance, and displays the annotated inference on an OpenCV GUI.
"""

import cv2
from ultralytics import YOLO

# 1. Initialize the YOLO11 Nano model structure
# The ultralytics library handles automatic model download on first execution.
model = YOLO("yolo11n.pt")

# 2. Bind to the local laptop camera pipeline
# Index 0 targets the primary internal hardware webcam device.
cap = cv2.VideoCapture(0)

# Verify camera interface initialization status
if not cap.isOpened():
    print("[CRITICAL] Could not open or read from webcam device index 0.")
    exit()

print("\n=======================================================")
print("  YOLO11n WEBCAM INFERENCE PIPELINE RUNNING           ")
print("=======================================================")
print("  Press 'q' inside the video display window to exit... ")
print("=======================================================\n")

while True:
    # Capture sequential frames from the camera device buffer
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Blank frame intercepted. Dropping connection link.")
        break

    # 3. Compute inference maps over the frame array matrix
    # stream=True optimizes internal GPU/CPU caching vectors for video sequences.
    # verbose=False minimizes terminal logging overhead to sustain target frame rates.
    results = model(frame, stream=True, verbose=False)

    # Iterate through the single-element frame output generator
    for result in results:
        # Utilize internal plotting routines to draw pixel-perfect 
        # bounding boxes, confidence tags, and class identifiers directly on the frame array.
        annotated_frame = result.plot()

    # 4. Flush the completed inference matrix onto the OpenCV viewport monitor
    cv2.imshow("Ultralytics YOLO11n Real-Time Detector", annotated_frame)

    # Await keypress escape event for 1 millisecond; check for quit command
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("[EXIT] Stopping detection engine...")
        break

# =========================================================================
# System Teardown Sequence
# =========================================================================
cap.release()
cv2.destroyAllWindows()
print("[SHUTDOWN] Hardware disarmed. Local resources reclaimed.")