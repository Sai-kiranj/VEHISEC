import can
import time

from crypto_security import create_authenticated_payload

CAN_INTERFACE = "vcan0"
CAN_ID = 0x100

bus = can.interface.Bus(
    channel=CAN_INTERFACE,
    interface="socketcan"
)

print("========================================")
print("       AUTHENTICATED ENGINE ECU")
print("========================================")
print(f"CAN Interface : {CAN_INTERFACE}")
print(f"CAN ID        : {hex(CAN_ID)}")
print("Authentication: HMAC-SHA256")
print("Press Ctrl+C to stop.\n")

rpm_values = list(range(1000, 6001, 250))
rpm_values += list(range(5750, 999, -250))

i = 0

try:

    while True:

        rpm = rpm_values[i % len(rpm_values)]

        speed = int(
            max(
                0,
                min(
                    180,
                    round(
                        0.017 * rpm
                        - 8
                        + 2.5 * __import__("math").sin(i / 2)
                    )
                )
            )
        )

        temperature = int(
            max(
                60,
                min(
                    115,
                    round(
                        70
                        + 0.0065 * (rpm - 1000)
                        + 2.0 * __import__("math").sin(i / 4)
                    )
                )
            )
        )

        vehicle_data = [
            (rpm >> 8) & 0xFF,
            rpm & 0xFF,
            speed,
            temperature
        ]

        authenticated_payload = create_authenticated_payload(
            CAN_ID,
            vehicle_data
        )

        message = can.Message(
            arbitration_id=CAN_ID,
            data=authenticated_payload,
            is_extended_id=False
        )

        try:

            bus.send(message)

            print(
                f"RPM: {rpm:4d} | "
                f"Speed: {speed:3d} km/h | "
                f"Temp: {temperature:3d} C | "
                f"AUTHENTICATED"
            )

        except can.CanError as error:

            print(
                f"CAN transmission error: {error}"
            )

        i += 1
        time.sleep(0.5)

except KeyboardInterrupt:

    print("\nAuthenticated ECU stopped.")

finally:

    bus.shutdown()
