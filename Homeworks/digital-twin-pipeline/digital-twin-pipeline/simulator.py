import time
import cv2
import psutil
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Updated InfluxDB Configuration
URL = "http://localhost:8086"
TOKEN = "my-super-secret-token"
ORG = "digitaltwin"
BUCKET = "twin_data"

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize Webcam
cap = cv2.VideoCapture(0)

print("Starting Laptop Surrounding Digital Twin Simulator... Press Ctrl+C to stop.")

try:
    while True:
        # 1. Capture Environmental Ambient Light
        ret, frame = cap.read()
        brightness = 0.0
        if ret:
            # Convert frame to grayscale and calculate average pixel intensity
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = float(np.mean(gray))
        
        # 2. Capture Laptop Internal Hardware State
        cpu_load = psutil.cpu_percent(interval=None)
        battery = psutil.sensors_battery()
        battery_level = float(battery.percent) if battery else 100.0

        # 3. Create spatial twin movement variables mapped to your surroundings
        # Example: Brightness drives X/Y shifting, CPU load drives Z rotation speed
        x_pos = (brightness / 255.0) * 10.0 - 5.0  # Scale brightness 0-255 to a -5 to 5 coordinate range
        y_pos = (cpu_load / 100.0) * 5.0
        z_rot = time.time() % 360 * (cpu_load / 100.0) 

        # 4. Write Telemetry/Sensor Stream to InfluxDB
        sensor_point = Point("sensor_data") \
            .field("room_brightness", brightness) \
            .field("cpu_load", cpu_load) \
            .field("battery", battery_level)
        
        # 5. Write Digital Twin State (Spatial properties for Omniverse)
        twin_point = Point("twin_state") \
            .field("x", x_pos) \
            .field("y", y_pos) \
            .field("z", 0.0) \
            .field("rx", z_rot) \
            .field("ry", 0.0) \
            .field("rz", 0.0)

        write_api.write(bucket=BUCKET, org=ORG, record=[sensor_point, twin_point])
        
        print(f"Logged -> Room Brightness: {brightness:.2f} | CPU: {cpu_load}% | Mapped X: {x_pos:.2f}")
        
        # Periodic update rate (e.g., every 1 second)
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nStopping Simulator...")
finally:
    cap.release()
    client.close()
