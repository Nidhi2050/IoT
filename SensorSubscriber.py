import json
import time
import requests
import paho.mqtt.client as mqtt
import threading

CONFIG = {"broker_host": "localhost", "broker_port": 1883}

THINGSPEAK_WRITE_KEY = "OH6BIO14QCCIP1EY"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

TOPIC_PREFIX = "sensors/device"
DEVICES = ["1", "2", "3"]

latest_temp = {d: None for d in DEVICES}
latest_hum = {d: None for d in DEVICES}

latest_lock = threading.Lock()
THRESHOLD_C = 30.0


def send_to_thingspeak(v1, v2, v3, h1, h2, h3, fan_status):
    params = {
        "api_key": THINGSPEAK_WRITE_KEY,
        "field1": v1,
        "field2": v2,
        "field3": v3,
        "field4": h1,
        "field5": h2,
        "field6": h3,
        "field7": int(fan_status)
    }

    try:
        r = requests.get(THINGSPEAK_URL, params=params, timeout=10)
        print("[ThingSpeak] Update:", params)
    except Exception as e:
        print("[ThingSpeak] Error:", e)


def maybe_publish():
    with latest_lock:
        t1, t2, t3 = latest_temp["1"], latest_temp["2"], latest_temp["3"]
        h1, h2, h3 = latest_hum["1"], latest_hum["2"], latest_hum["3"]

    fan_on = any((t and float(t) > THRESHOLD_C) for t in [t1, t2, t3])

    send_to_thingspeak(
        t1 if t1 else "",
        t2 if t2 else "",
        t3 if t3 else "",
        h1 if h1 else "",
        h2 if h2 else "",
        h3 if h3 else "",
        fan_on
    )


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        for d in DEVICES:
            topic = f"{TOPIC_PREFIX}{d}"
            client.subscribe(topic)
            print("Subscribed:", topic)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
    except:
        print("Invalid JSON")
        return

    device = payload.get("device")

    temp = payload.get("temperature")
    hum = payload.get("humidity")

    if device not in DEVICES:
        try:
            device = msg.topic.split("device")[-1]
        except:
            return

    if temp is None:
        print("No temperature in payload")
        return

    if hum is None:
        print("No humidity in payload")
        return

    with latest_lock:
        latest_temp[device] = float(temp)
        latest_hum[device] = float(hum)

    print(f"Device {device} -> {temp}°C, {hum}% RH")
    maybe_publish()


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(CONFIG["broker_host"], CONFIG["broker_port"], 60)
    client.loop_forever()


if __name__ == "__main__":
    main()