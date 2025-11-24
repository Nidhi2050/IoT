import threading
import subprocess
import sys
import os
import time
import signal

PY = sys.executable
processes = []

def start_device(device_id):
    script = os.path.join(os.path.dirname(__file__), "SensorPublisher.py")
    p = subprocess.Popen([PY, script, str(device_id)])
    processes.append(p)
    return p

def stop_all(signum, frame):
    print("Stopping all publishers...")
    for p in processes:
        try: p.terminate()
        except: pass
    time.sleep(1)
    for p in processes:
        if p.poll() is None:
            try: p.kill()
            except: pass
    print("All publishers stopped.")
    raise SystemExit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_all)
    signal.signal(signal.SIGTERM, stop_all)

    print("Starting 3 device publishers...")
    for i in [1,2,3]:
        start_device(i)
        time.sleep(20)

    print("Publishers started. Press Ctrl-C to stop.")
    while True:
        time.sleep(20)