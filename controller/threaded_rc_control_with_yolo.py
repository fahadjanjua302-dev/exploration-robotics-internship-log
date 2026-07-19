"""
Exploration Robotics Internship - Thread-Decoupled Drone Engine.

Implements a multi-threaded architecture separating heavy YOLO11n inference from 
the Pygame input loop to eliminate command unresponsiveness and lag.
"""

import cv2
from djitellopy import Tello
import pygame
import queue
import sys
import threading
import time
from ultralytics import YOLO

# Initialize Pygame explicitly on the main process thread
pygame.init()
window = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Tello RC Command Input Console")

# Thread-safe pipeline queue to safely route processed frames to the UI thread
video_queue = queue.Queue(maxsize=1)

# Central structural flag tracking engine loop states across threads
is_running = True

# --- Establish Network Telemetry Sockets ---
drone = Tello()
drone.connect()
print(f"[BOOT] Connected. Battery Status: {drone.get_battery()}%")

# Initialize and fire deep network streaming buffers
drone.streamon()
frame_reader = drone.get_frame_read()

# --- Flight Parameters Configuration ---
SPEED_SLOW = 35
SPEED_FAST = 75
current_speed = SPEED_SLOW


def rc_control_loop():
    """Thread 1: Dedicated solely to continuous manual flight calculations.

    Runs independently to maintain highly responsive piloting control.
    """
    global current_speed, is_running

    print("[SYSTEM] Decoupled RC Command Thread Active.")
    while is_running:
        lr, fb, ud, yaw = 0, 0, 0, 0

        # Poll the live keyboard scan arrays directly
        keys = pygame.key.get_pressed()

        # Dynamic Speed Scalars
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_speed = SPEED_FAST
        elif keys[pygame.K_CAPSLOCK]:
            current_speed = SPEED_SLOW

        # Structurals: Escape, Takeoff, Landing
        if keys[pygame.K_ESCAPE]:
            print("[EMERGENCY] Terminating thread contexts.")
            is_running = False
            break
        elif keys[pygame.K_t]:
            drone.takeoff()
        elif keys[pygame.K_l]:
            drone.land()

        # Directional Maps
        if keys[pygame.K_w]:
            fb = current_speed
        elif keys[pygame.K_s]:
            fb = -current_speed

        if keys[pygame.K_a]:
            lr = -current_speed
        elif keys[pygame.K_d]:
            lr = current_speed

        if keys[pygame.K_UP]:
            ud = current_speed
        elif keys[pygame.K_DOWN]:
            ud = -current_speed

        if keys[pygame.K_LEFT]:
            yaw = -current_speed
        elif keys[pygame.K_RIGHT]:
            yaw = current_speed

        # Dispatch immediate velocity vectors via UDP
        drone.send_rc_control(lr, fb, ud, yaw)

        # Maintained at ~33Hz to conform with Tello stack tolerances without dropping packets
        time.sleep(0.03)


def vision_processing_loop():
    """Thread 2: Dedicated heavy lifting loop for YOLO11 object detection.

    Runs as fast as your processor allows without blocking your keystrokes.
    """
    global is_running
    print("[SYSTEM] Decoupled Vision / YOLO Inference Thread Active.")

    # Initialize neural network locally inside its working thread space
    model = YOLO("yolo11n.pt")

    while is_running:
        try:
            # Non-blocking access to the PyAV thread buffer cache
            raw_frame = frame_reader.frame
            if raw_frame is None:
                continue

            # [COLOR CORRECTION] Transform RGB data arrays into native OpenCV BGR format
            corrected_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)

            # Compute deep network inference models
            results = model(corrected_frame, stream=True, verbose=False)

            # Paint target identifiers and tracking lines over array elements
            for result in results:
                annotated_frame = result.plot()

            # Push the completed visual frame to the pipeline queue.
            # If the queue is full, drop the old frame to keep tracking real-time.
            if video_queue.full():
                try:
                    video_queue.get_nowait()
                except queue.Empty:
                    pass

            video_queue.put(annotated_frame, block=False)

        except Exception as err:
            print(f"[VISION ERROR] Pipeline Exception: {err}")
            time.sleep(0.01)


# --- Thread Spawning Sequence ---
rc_thread = threading.Thread(target=rc_control_loop, daemon=True)
vision_thread = threading.Thread(target=vision_processing_loop, daemon=True)

rc_thread.start()
vision_thread.start()


# --- Main Thread (Window Lifecycle & Display Render Output) ---
print("[SYSTEM] Host Management Thread Handling Windows and Outputs.")
try:
    while is_running:
        # Crucial: Pump Pygame event loop directly on Main Thread to prevent window freezing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Read the latest available fully-inferred frame from the vision thread
        if not video_queue.empty():
            display_frame = video_queue.get()
            cv2.imshow(
                "Tello Drone Live Vision Tracker - Thread Decoupled", display_frame
            )

        # Trigger quick render pulse event updates to clear frame screens
        if cv2.waitKey(1) & 0xFF == ord("q"):
            is_running = False
            break

        # Gentle throttle on the main thread loop to keep CPU usage efficient
        time.sleep(0.01)

finally:
    # --- Structural Reclamation Clean-up ---
    print("\n[SHUTDOWN] Terminating multi-threaded loops. Landing safely...")
    is_running = False

    # Force immediate hover to eliminate inertia drift
    drone.send_rc_control(0, 0, 0, 0)
    time.sleep(0.2)
    drone.land()

    # Close network pipes and drop resources safely
    drone.streamoff()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()