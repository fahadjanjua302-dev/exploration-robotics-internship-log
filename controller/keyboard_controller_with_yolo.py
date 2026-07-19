"""
Exploration Robotics Internship - Intelligent RC Flight Engine (YOLO11n Integration).

This system merges real-time continuous manual flight control (via Pygame keyboard I/O)
with airborne computer vision. It captures live video from the Tello EDU drone, decodes
the frames, runs neural network inference via YOLO11n, plots the tracking boxes, and
simultaneously handles continuous velocity commands via send_rc_control().
"""

import cv2
from djitellopy import Tello
import pygame
import sys
import time
from ultralytics import YOLO

# 1. Initialize Pygame modules and build an explicit window to capture keystrokes
pygame.init()
window = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Tello Control Console")

# 2. Initialize the YOLO11 Nano neural network model instance
model = YOLO("yolo11n.pt")

# 3. Initialize and establish network control and telemetry sockets with the drone
drone = Tello()
drone.connect()
print(f"[BOOT] Connected. System Battery: {drone.get_battery()}%")

# Activate live H.264 video decoding background stream threads
drone.streamon()
frame_reader = drone.get_frame_read()

# --- Flight Parameters Configuration ---
# Velocity scalar modes (Max range bounds: 0 to 100)
SPEED_SLOW = 35
SPEED_FAST = 75
current_speed = SPEED_SLOW  # System defaults to safe slow-speed mode

# Track application operational loop state
is_running = True

print("\n=======================================================")
print("  INTELLIGENT RC CONTROLLER + YOLO11n ACTIVE           ")
print("=======================================================")
print("  Focus the small blank Pygame window to control:     ")
print("  W / S      : Continuous Forward / Backward           ")
print("  A / D      : Continuous Left / Right Roll            ")
print("  UP / DOWN  : Continuous Throttle Up / Down           ")
print("  LEFT/RIGHT : Continuous Yaw Turn Left / Right        ")
print("  SHIFT / CAPSLOCK : Toggle Speed (SHIFT=Fast, CAPS=Slow)")
print("  T / L      : Takeoff / Land                          ")
print("  ESCAPE     : Emergency Cut & Stop                    ")
print("=======================================================\n")


def get_keyboard_input():
    """Polls the active Pygame OS events stack, mapping pressed arrays to explicit

    linear and angular velocity components.
    """
    global current_speed, is_running

    # Core vector initializations (Velocity parameters range: -100 to 100)
    lr, fb, ud, yaw = 0, 0, 0, 0

    # Process pending events queue to prevent OS window freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    keys = pygame.key.get_pressed()

    # --- Mode Shifts: Speed Regulation ---
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        current_speed = SPEED_FAST
    elif keys[pygame.K_CAPSLOCK]:
        current_speed = SPEED_SLOW

    # --- Structural Commands: Takeoff / Landing / Emergency ---
    if keys[pygame.K_ESCAPE]:
        print("[EMERGENCY] Halting engine threads immediately.")
        is_running = False
        return 0, 0, 0, 0
    elif keys[pygame.K_t]:
        print("[ACTION] Sending global takeoff frame...")
        drone.takeoff()
    elif keys[pygame.K_l]:
        print("[ACTION] Sending global landing frame...")
        drone.land()

    # --- Flight Vector Mapping (Horizontal Planar Axis) ---
    if keys[pygame.K_w]:
        fb = current_speed
    elif keys[pygame.K_s]:
        fb = -current_speed

    if keys[pygame.K_a]:
        lr = -current_speed
    elif keys[pygame.K_d]:
        lr = current_speed

    # --- Flight Vector Mapping (Vertical and Rotational Axis) ---
    if keys[pygame.K_UP]:
        ud = current_speed
    elif keys[pygame.K_DOWN]:
        ud = -current_speed

    if keys[pygame.K_LEFT]:
        yaw = -current_speed
    elif keys[pygame.K_RIGHT]:
        yaw = current_speed

    return lr, fb, ud, yaw


# Main High-Frequency Asynchronous Execution Loop
while is_running:

    # 1. Capture spatial velocity parameters based on current key-states
    lr_v, fb_v, ud_v, yaw_v = get_keyboard_input()

    # Dispatch non-blocking RC velocity vectors to the Tello controller
    drone.send_rc_control(lr_v, fb_v, ud_v, yaw_v)

    # 2. Extract raw frame array from the PyAV network thread buffer
    raw_frame = frame_reader.frame

    # [COLOR FIX] Convert native raw video array out of RGB into OpenCV's native BGR layout
    corrected_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

    # 3. Compute neural inference tracking maps over the color-corrected matrix frame
    # stream=True optimizes frame caching vectors; verbose=False prevents console lag
    results = model(corrected_frame, stream=True, verbose=False)

    # Extract target annotations and draw bounding boxes on the frame matrix
    for result in results:
        annotated_frame = result.plot()

    # 4. Flush the compiled image matrix arrays to the desktop view screen
    cv2.imshow("Tello Drone Live Vision Tracker - YOLO11n", annotated_frame)

    # Force a microscopic OpenCV draw update event loop (1ms) to paint graphic pixels
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # 5. Microsecond timing loop throttle to match Tello command packet intervals (~20-50Hz)
    time.sleep(0.02)

# =========================================================================
# Resource Reclamation and Shutdown Sequence
# =========================================================================
print("\n[SHUTDOWN] Exiting main loop. Safe landing sequence engaged...")
drone.send_rc_control(0, 0, 0, 0)  # Zero out all velocity registers to prevent drift
drone.land()

# Terminate socket stream pipes safely
drone.streamoff()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()