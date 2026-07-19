"""
Exploration Robotics Internship - Hardware Test: Single Translation & Aerobatics.

This script extends the baseline single-drone test by implementing explicit
spatial movements (a 30cm planar translation box matrix) followed by high-current 
dynamic maneuvers (aerobatic inversion flip) to evaluate motor tracking.
"""

from djitellopy import Tello
import time


def main():
    drone = Tello()
    drone.connect()

    # Pre-flight battery check (Flips require >20% capacity due to high current draw)
    battery = drone.get_battery()
    print(f"[MOTION TEST] System Initialized. Battery: {battery}%")
    if battery < 30:
        print("[WARNING] Battery low. Dynamic flips may fail or force landing.")

    print("[MOTION TEST] Taking off...")
    drone.takeoff()
    time.sleep(1.5)

    # --- Step 1: Localized Horizontal Tracking (30cm Square Path) ---
    print("[MOTION TEST] Translating Forward 30cm...")
    drone.move_forward(30)
    time.sleep(1.0)

    print("[MOTION TEST] Translating Right 30cm...")
    drone.move_right(30)
    time.sleep(1.0)

    print("[MOTION TEST] Translating Backward 30cm...")
    drone.move_back(30)
    time.sleep(1.0)

    print("[MOTION TEST] Translating Left 30cm (Returning to origin)...")
    drone.move_left(30)
    time.sleep(1.5)  # Extended settle time to clear residual translational inertia

    # --- Step 2: High-Velocity Dynamic Maneuver ---
    # Executive command triggers a rapid motor pitch variation for a full 360 loop
    print("[MOTION TEST] Commanding Forward Inversion Flip ('f')...")
    drone.flip("f")
    time.sleep(2.0)  # Safe recovery window allowing the drone to regain pressure altitude

    # --- Step 3: Secure Recovery ---
    print("[MOTION TEST] Completing mission profile...")
    drone.land()


if __name__ == "__main__":
    main()