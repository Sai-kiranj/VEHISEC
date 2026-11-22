import can
import threading
import json
import time
import os
from pathlib import Path

from crypto_security import verify_authenticated_payload

CAN_INTERFACE = "vcan0"
TARGET_CAN_ID = 0x100

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = str(BASE_DIR / "dashboard" / "vehicle_state.json")

vehicle_state = {
    "rpm": 0,
    "speed": 0,
    "temperature": 0,
    "authentication": "WAITING",
"status": "WAITING",
    "reason": "Waiting for authenticated CAN data",
    "security_event": "NONE",
    "event_time": 0
}

bus = can.interface.Bus(
    channel=CAN_INTERFACE,
    interface="socketcan"
)


def save_state():

    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w") as file:

        json.dump(
            vehicle_state,
file
        )

    os.replace(
        temp_file,
        STATE_FILE
    )


def monitor_can():

    while True:

        message = bus.recv()

        if message is None:
            continue

        if message.arbitration_id != TARGET_CAN_ID:

vehicle_state["authentication"] = "BLOCKED"
            vehicle_state["status"] = "BLOCKED"
            vehicle_state["reason"] = "UNKNOWN CAN ID"
            vehicle_state["security_event"] = "UNKNOWN CAN ID"
            vehicle_state["event_time"] = time.time()

            save_state()

            continue

        authenticated, reason = verify_authenticated_payload(
            message.arbitration_id,
            message.data
        )

        if not authenticated:

            vehicle_state["authentication"] = "FAILED"
vehicle_state["status"] = "BLOCKED"
            vehicle_state["reason"] = reason
            vehicle_state["security_event"] = reason
            vehicle_state["event_time"] = time.time()

            save_state()

            continue

        data = message.data[:4]

        rpm = (data[0] << 8) | data[1]
        speed = data[2]
        temperature = data[3]

        vehicle_state["rpm"] = rpm
        vehicle_state["speed"] = speed
        vehicle_state["temperature"] = temperature
        vehicle_state["authentication"] = "VALID"
vehicle_state["status"] = "NORMAL"
        vehicle_state["reason"] = "Authenticated CAN data"

        save_state()


def start_monitor():

    thread = threading.Thread(
        target=monitor_can,
        daemon=True
    )

    thread.start()


if __name__ == "__main__":

    print("========================================")
 print("       LIVE VEHICLE CAN MONITOR")
    print("========================================")
    print(f"Interface : {CAN_INTERFACE}")
    print(f"CAN ID    : {hex(TARGET_CAN_ID)}")
    print("Publishing live state to:")
    print(f"  {STATE_FILE}")
    print("Press Ctrl+C to stop.\n")

    save_state()

    start_monitor()

    try:

        while True:
 print(
                f"RPM: {vehicle_state['rpm']:5d} | "
                f"Speed: {vehicle_state['speed']:3d} km/h | "
                f"Temp: {vehicle_state['temperature']:3d} C | "
                f"Auth: {vehicle_state['authentication']} | "
                f"Status: {vehicle_state['status']}"
            )

            time.sleep(2)

    except KeyboardInterrupt:

        print("\nVehicle monitor stopped.")

    finally:

        bus.shutdown()
