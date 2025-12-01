import paho.mqtt.client as mqtt
import json
import random
import time
import sys
import signal
from datetime import datetime

BROKER = "localhost"
PORT = 1883

def main():
    device_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    topic = f"sensors/device{device_id}"
    client = mqtt.Client()
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        return

    print(f"[Device {device_id}] Publishing to topic: {topic}")
    running = True

    def handle_sig(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    while running:
        payload = {
            "device": device_id,
            "temperature": round(random.uniform(25.0, 35.0), 2),
            "humidity": round(random.uniform(35.0, 55.0), 2)
        }

        try:
            client.publish(topic, json.dumps(payload))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"[{timestamp}] [Device {device_id}] Published: {payload}")
        except Exception as e:
            print(f"[Device {device_id}] Publish error: {e}")

        time.sleep(20)

if __name__ == "__main__":
    main()