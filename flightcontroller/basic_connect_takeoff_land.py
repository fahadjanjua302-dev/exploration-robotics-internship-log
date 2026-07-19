"""
Exploration Robotics Internship - Hardware Test: Single Baseline.

This script serves as the initial hardware validation milestone. It establishes 
a direct 1-to-1 Wi-Fi connection to a single Tello drone's default access point, 
verifying basic handshake, telemetry initialization, takeoff, and landing routines.
"""

from djitellopy import Tello
import time


def main():
    # Initialize the single drone controller interface
    drone = Tello()

    # Establish socket connection via the default Tello Wi-Fi network (192.168.10.1)
    print("[HW TEST] Attempting connection to Tello access point...")
    drone.connect()

    # Basic telemetry retrieval to confirm responsive bidirectional data flow
    print(f"[HW TEST] Connection verified. Current Battery: {drone.get_battery()}%")

    # Minimalist flight profile to test vertical stabilization and motor actuation
    print("[HW TEST] Executing automated takeoff...")
    drone.takeoff()
    
    # Static hover buffer to allow internal state estimation/IMU filters to settle
    time.sleep(2.0)

    print("[HW TEST] Initiating automated landing...")
    drone.land()
    print("[HW TEST] Baseline test complete. Motors disarmed.")


if __name__ == "__main__":
    main()