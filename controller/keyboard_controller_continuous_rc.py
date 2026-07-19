"""
Exploration Robotics Internship - Asynchronous Continuous RC Flight Controller.

This engine utilizes Pygame for high-frequency keyboard I/O polling (detecting hold 
and release states) and routes non-blocking velocity vectors to the Tello drone via 
send_rc_control(). Simultaneously, OpenCV displays a real-time, color-corrected video feed.
"""

import cv2
from djitellopy import Tello
import pygame
import sys
import time

# Initialize Pygame modules and build an explicit window to capture keystrokes
pygame.init()
window = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Tello Control Console")

# Initialize and establish network sockets with the drone
drone = Tello()
drone.connect()
print(f"[BOOT] Connected. System Battery: {drone.get_battery()}%")

# Active H.264 video decoding background threads
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
print("  REAL-TIME CONTINUOUS RC CONTROLLER ACTIVATED         ")
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

    # [LOGIC] Dispatch non-blocking RC velocity vectors to the Tello controller.
    # The drone will execute these speeds continuously until a clean zero vector is received.
    drone.send_rc_control(lr_v, fb_v, ud_v, yaw_v)

    # 2. Extract frame buffer array from the PyAV network thread
    raw_frame = frame_reader.frame

    # [COLOR FIX] Convert native raw video array out of RGB into OpenCV's native BGR layout
    corrected_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

    # Render frame inside visual UI monitor window
    cv2.imshow("Tello Live BGR Video Stream", corrected_frame)

    # Force a microscopic OpenCV draw update event loop (1ms) to paint graphic pixels
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # 3. Microsecond timing loop throttle to match Tello command packet intervals (~20-50Hz)
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