import can
import csv
import os
import time
from datetime import datetime

from defence.risk_engine import RiskCorrelator

CAN_INTERFACE = "vcan0"

# Expected CAN ID
ALLOWED_CAN_IDS = {0x100}
TARGET_ID = 0x100

# Security limits
MAX_RPM = 7000
MAX_SPEED = 200
MAX_TEMP = 120

# Frequency threshold
MAX_MESSAGES_PER_SECOND = 20

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "can_log.csv")

os.makedirs(LOG_DIR, exist_ok=True)

# Create CSV log if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp",
            "CAN_ID",
            "RPM",
            "Speed_kmh",
            "Temperature_C",
            "Status",
            "Reason"
        ])

# Connect to Virtual CAN
bus = can.interface.Bus(
    channel=CAN_INTERFACE,
    interface="socketcan"
)

# Risk correlation engine
correlator = RiskCorrelator(window_seconds=3)

# Maintain separate frequency windows for each CAN ID
frequency_windows = {}

print("========================================")
print("       CAN SECURITY DETECTOR")
print("========================================")
print(f"Interface       : {CAN_INTERFACE}")
print(f"Allowed CAN IDs : {[hex(x) for x in ALLOWED_CAN_IDS]}")
print(f"Target CAN ID   : {hex(TARGET_ID)}")
print(f"Frequency limit : {MAX_MESSAGES_PER_SECOND} messages/sec")
print("Risk correlation: 3 seconds")
print("Press Ctrl+C to stop.\n")

try:
    while True:

        # Flush incidents even when no CAN messages arrive
        correlator.flush_expired()

        message = bus.recv(timeout=0.2)

        if message is None:
            continue

        can_id = message.arbitration_id
        current_time = time.monotonic()

        if can_id not in frequency_windows:
            frequency_windows[can_id] = {
                "start": current_time,
                "count": 0
            }

        frequency_windows[can_id]["count"] += 1

        elapsed = current_time - frequency_windows[can_id]["start"]

        if elapsed >= 1.0:

            frequency = frequency_windows[can_id]["count"] / elapsed

            if frequency > MAX_MESSAGES_PER_SECOND:

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                reason = "HIGH CAN MESSAGE FREQUENCY"

                print(
                    f"{timestamp} | ANOMALY | "
                    f"CAN ID: {hex(can_id)} | "
                    f"{reason} | {frequency:.1f} msg/s"
                )

                with open(LOG_FILE, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        timestamp,
                        hex(can_id),
                        "",
                        "",
                        "",
                        "ANOMALY",
                        reason
                    ])

                correlator.add_evidence(can_id, [reason])

            frequency_windows[can_id] = {
                "start": current_time,
                "count": 0
            }


        if can_id not in ALLOWED_CAN_IDS:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            reason = "UNKNOWN CAN ID"

            print(
                f"{timestamp} | CAN ID: {hex(can_id)} | "
                f"ANOMALY | {reason}"
            )

            with open(LOG_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    hex(can_id),
                    "",
                    "",
                    "",
                    "ANOMALY",
                    reason
                ])

            correlator.add_evidence(can_id, [reason])
            continue


        if can_id != TARGET_ID:
            continue

        data = message.data

        if len(data) < 4:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            reason = "INVALID DATA LENGTH"

            print(
                f"{timestamp} | ANOMALY | {reason}"
            )

            with open(LOG_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    hex(can_id),
                    "",
                    "",
                    "",
                    "ANOMALY",
                    reason
                ])

            correlator.add_evidence(can_id, [reason])
            continue


        rpm = (data[0] << 8) | data[1]
        speed = data[2]
        temperature = data[3]


        reasons = []

        if rpm > MAX_RPM:
            reasons.append("RPM LIMIT EXCEEDED")

        if speed > MAX_SPEED:
            reasons.append("SPEED LIMIT EXCEEDED")

        if temperature > MAX_TEMP:
            reasons.append("TEMPERATURE LIMIT EXCEEDED")

        status = "ANOMALY" if reasons else "NORMAL"

        reason = ", ".join(reasons) if reasons else "Within limits"

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        print(
            f"{timestamp} | "
            f"CAN ID: {hex(can_id)} | "
            f"RPM: {rpm:5d} | "
            f"Speed: {speed:3d} km/h | "
            f"Temp: {temperature:3d} C | "
            f"{status} | {reason}"
        )

        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                hex(can_id),
                rpm,
                speed,
                temperature,
                status,
                reason
            ])

        if reasons:
            correlator.add_evidence(can_id, reasons)

except KeyboardInterrupt:
    print("\nCAN detector stopped.")

finally:
    correlator.flush_all()
    bus.shutdown()
