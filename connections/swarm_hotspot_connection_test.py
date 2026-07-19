"""
Exploration Robotics Internship - Hardware Swarm Choreography.

This script demonstrates multi-agent synchronization and asymmetric mission execution.
Utilizing a common mobile hotspot framework, it instantiates parallel network sockets via 
TelloSwarm, coordinating synchronized group movements alongside asymmetrical, independent 
asynchronous tasks (divergent motions and opposing direction flips).
"""

from djitellopy import TelloSwarm
import time


def main():
    # Local IP leases assigned to the respective drone hardware by your mobile hotspot
    SWARM_IPS = [
        "10.65.164.114",  # Drone Index 0
        "10.65.164.156"   # Drone Index 1
    ]

    print(f"[SWARM] Initializing network interface bindings for nodes: {SWARM_IPS}")
    swarm = TelloSwarm.fromIps(SWARM_IPS)
    
    # Concurrently ping and open control sockets on all designated nodes
    swarm.connect()

    # Pre-flight diagnostic verification sweep across the array cluster
    for drone in swarm:
        print(f"[SWARM DIAGNOSTICS] Node {drone.address} -> Charge Status: {drone.get_battery()}%")

    print("[SWARM] Transmitting global synchronized takeoff directive...")
    swarm.takeoff()
    time.sleep(2.5)  # Extended buffer to guarantee both drones lock hover altitude cleanly

    # =========================================================================
    # PHASE 1: Synchronized Group Geometry (Symmetrical Square Tracking)
    # =========================================================================
    print("[SWARM PHASE 1] Executing synchronized 40cm perimeter square matrix...")
    
    swarm.move_forward(40)
    time.sleep(1.0)
    
    swarm.move_right(40)
    time.sleep(1.0)
    
    swarm.move_back(40)
    time.sleep(1.0)
    
    swarm.move_left(40)
    time.sleep(2.0)  # Settlement window before breaking uniform formation symmetry

    # =========================================================================
    # PHASE 2: Formation Splitting (Asymmetrical Divergent Translation)
    # =========================================================================
    print("[SWARM PHASE 2] Initiating split execution. Diverging fleet positions...")
    
    # Spawns separate execution threads via lambda map:
    # Drone [0] translates Forward while Drone [1] translates Backward
    swarm.parallel(lambda i, drone: drone.move_forward(40) if i == 0 else drone.move_back(40))
    time.sleep(2.0)

    # =========================================================================
    # PHASE 3: Asymmetrical Aerobatics (Opposing Direction Flips)
    # =========================================================================
    print("[SWARM PHASE 3] Triggering independent opposing dynamic flips...")
    
    # Simultaneously executes independent flips to limit spatial aerodynamic conflict
    # Drone [0] executes a Forward Flip | Drone [1] executes a Backward Flip
    swarm.parallel(lambda i, drone: drone.flip("f") if i == 0 else drone.flip("b"))
    time.sleep(2.5)  # High buffer time allows clean dissipation of shared prop-wash vortexes

    # =========================================================================
    # PHASE 4: Fleet Convergence & Return to Origin Layout
    # =========================================================================
    print("[SWARM PHASE 4] Reversing split vectors to re-align fleet formation...")
    
    # Drone [0] shifts Backward, Drone [1] shifts Forward to re-occupy original takeoff planes
    swarm.parallel(lambda i, drone: drone.move_back(40) if i == 0 else drone.move_forward(40))
    time.sleep(2.0)

    # =========================================================================
    # PHASE 5: Ground Recovery Sequence
    # =========================================================================
    print("[SWARM PHASE 5] Broadcasting unified safe landing commands...")
    swarm.land()
    print("[SWARM] Mission protocol completed successfully. All threads terminated.")


if __name__ == "__main__":
    main()