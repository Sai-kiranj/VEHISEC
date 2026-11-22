from flask import Flask, render_template, jsonify
import csv
import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "logs",
    "can_log.csv"
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():

    rows = []

    if os.path.exists(LOG_FILE):

        with open(LOG_FILE, "r", newline="") as file:

            reader = csv.DictReader(file)
            rows = list(reader)

    total = len(rows)

    normal = sum(
        1
        for row in rows
        if row.get("Status") == "NORMAL"
    )

    anomalies = sum(
        1
        for row in rows
        if row.get("Status") == "ANOMALY"
    )

    unknown = sum(
        1
        for row in rows
        if row.get("Reason") == "UNKNOWN CAN ID"
    )

    if rows:

        latest_row = rows[-1]

        latest = (
            f"{latest_row.get('Timestamp')} | "
            f"{latest_row.get('Status')} | "
            f"{latest_row.get('Reason')}"
        )

    else:

        latest = "No CAN traffic recorded."

    recent_rows = rows[-20:]

    return jsonify({
        "total": total,
        "normal": normal,
        "anomalies": anomalies,
        "unknown": unknown,
        "latest": latest,
        "rows": recent_rows
    })


STATE_FILE = os.path.join(
    BASE_DIR,
    "dashboard",
    "vehicle_state.json"
)


@app.route("/can-log")
def can_log():
    rows = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

    return jsonify({
        "rows": rows[-20:]
    })


@app.route("/vehicle")
def vehicle():
    return render_template("vehicle.html")


@app.route("/vehicle-data")
def vehicle_data():

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            state = json.load(file)
    else:
        state = {
            "rpm": 0,
            "speed": 0,
            "temperature": 0,
            "authentication": "WAITING",
            "status": "WAITING",
            "reason": "Waiting for authenticated CAN data"
        }

    return jsonify(state)


if __name__ == "__main__":

    print("========================================")
    print("     AUTOMOTIVE ECU SECURITY DASHBOARD")
    print("========================================")
    print("Dashboard URL: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
