"""
Exploration Robotics Internship - Network Provisioning: Access Point Migration.

This utility script reconfigures a standalone Tello drone's Wi-Fi module from 
Access Point mode to Station Mode. It instructs the drone to join an external 
local network infrastructure (e.g., mobile hotspot), facilitating swarm networking.
"""

from djitellopy import Tello


def main():
    drone = Tello()
    
    # Establish direct connection via the drone's individual factory Wi-Fi SSID
    drone.connect()
    print(f"[PROVISION] Connected to target drone. MAC Address: {drone.get_mac_address()}")

    # Network SSID and WPA2 Passphrase configuration targets
    TARGET_SSID = "abc"
    TARGET_PASS = "fahad1234"

    print(f"[PROVISION] Reconfiguring Wi-Fi module to Station Mode...")
    print(f"[PROVISION] Target Network SSID: '{TARGET_SSID}'")
    
    # Send the raw SDK control frame telling the Wi-Fi chip to shift modes and seek AP
    # Format: ap [ssid] [password]
    drone.send_control_command(f"ap {TARGET_SSID} {TARGET_PASS}")

    print("[PROVISION] Mode shift command dispatched successfully.")
    print("[PROVISION] ACTION REQUIRED: The drone will now reboot and attempt connection.")
    print("[PROVISION] Check your mobile hotspot/router client lease table for assigned IPs.")


if __name__ == "__main__":
    main()