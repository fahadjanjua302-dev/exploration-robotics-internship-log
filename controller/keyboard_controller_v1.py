import cv2
from djitellopy import Tello
import time

# Initialize drone and connect
drone = Tello()
drone.connect()
print(f"Connected. Battery: {drone.get_battery()}%")

# Turn on video streaming and initialize the frame reader thread
drone.streamon()
frame_reader = drone.get_frame_read()

# Define translational step distance (in cm) for each keypress
MOVE_STEP = 30 

print("\n=== KEYBOARD CONTROLLER ACTIVATED ===")
print("Click on the video window to focus it, then use controls:")
print("  W / S : Move Forward / Backward")
print("  A / D : Move Left / Right")
print("  T / L : Takeoff / Land")
print("  Q     : Quit Application\n")

while True:
    # 1. Fetch and process the video frame
    frame = frame_reader.frame
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("Tello Keyboard Control", frame)

    # 2. Capture keyboard inputs via the OpenCV GUI thread (awaits input for 1ms)
    key = cv2.waitKey(1) & 0xFF

    # 3. Flight Commands Logic Mapping
    if key == ord('t'):
        print("[CONTROL] Takeoff initiated")
        drone.takeoff()
    elif key == ord('l'):
        print("[CONTROL] Landing initiated")
        drone.land()
    elif key == ord('w'):
        print(f"[CONTROL] Moving Forward {MOVE_STEP}cm")
        drone.move_forward(MOVE_STEP)
    elif key == ord('s'):
        print(f"[CONTROL] Moving Backward {MOVE_STEP}cm")
        drone.move_back(MOVE_STEP)
    elif key == ord('a'):
        print(f"[CONTROL] Moving Left {MOVE_STEP}cm")
        drone.move_left(MOVE_STEP)
    elif key == ord('d'):
        print(f"[CONTROL] Moving Right {MOVE_STEP}cm")
        drone.move_right(MOVE_STEP)
    
    # 4. Exit Condition
    elif key == ord('q'):
        print("[EXIT] Closing controller application...")
        break

# Resource cleanup
cv2.destroyAllWindows()
drone.streamoff()