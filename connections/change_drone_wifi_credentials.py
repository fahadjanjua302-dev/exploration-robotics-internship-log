from djitellopy import Tello

drone = Tello()
drone.connect()

#make sure the sdk mode of drone is enabled 
drone.send_control_command("command")

# SDK command: wifi [ssid] [password]
# Note: Firmware prefixes the SSID with "TELLO-". Password must be >= 8 chars.
response = drone.send_control_command("wifi Fahad01 fahad1234")

print(f"Response: {response}")