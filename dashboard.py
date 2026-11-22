import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENT_FILE = os.path.join(BASE_DIR, "reports", "defence_events.jsonl")

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Automotive ECU Security Dashboard</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 28px;
    background: #101827;
    color: #e8eef8;
    font-family: Arial, sans-serif;
}
header { margin-bottom: 28px; }
h1 { margin: 0 0 8px; font-size: 27px; }
.subtitle { color: #91a1b8; }
.status { color: #55d6a1; font-size: 13px; margin-top: 12px; }
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.card, .panel {
    background: #1b293b;
    border: 1px solid #2c3c52;
    border-radius: 12px;
    padding: 20px;
}
.card p { color: #9aabc1; margin: 0 0 12px; }
.number { font-size: 32px; font-weight: bold; }
.low { color: #55d6a1; }
.medium { color: #f4ca64; }
.high { color: #ff9b59; }
.critical { color: #ff626e; }
.panel { margin-bottom: 24px; overflow-x: auto; }
h2 { font-size: 18px; margin: 0 0 18px; }
.bars { display: grid; gap: 14px; }
.bar-row {
    display: grid;
    grid-template-columns: 95px 1fr 35px;
    align-items: center;
    gap: 12px;
    font-size: 14px;
}
.track {
    height: 12px;
    background: #2c3c52;
    border-radius: 10px;
    overflow: hidden;
}
.fill { height: 100%; border-radius: 10px; }
.fill.low { background: #55d6a1; }
.fill.medium { background: #f4ca64; }
.fill.high { background: #ff9b59; }
.fill.critical { background: #ff626e; }
table { width: 100%; border-collapse: collapse; min-width: 750px; }
th, td {
    padding: 13px 12px;
    text-align: left;
    border-bottom: 1px solid #304057;
    font-size: 13px;
}
th { color: #9aabc1; }
td { color: #e0e8f3; }
.tag {
    padding: 5px 9px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11px;
}
.tag.LOW { background: #174b3b; color: #69e0ad; }
.tag.MEDIUM { background: #51451f; color: #f4d477; }
.tag.HIGH { background: #61351f; color: #ffad75; }
.tag.CRITICAL { background: #5b222b; color: #ff8490; }
.empty { color: #91a1b8; padding: 20px 0; }
.footer { color: #8292a8; font-size: 12px; text-align: center; }
@media(max-width: 600px) {
    body { padding: 16px; }
    h1 { font-size: 22px; }
}
</style>
</head>
<body>

<header>
    <h1>Automotive ECU Security Dashboard</h1>
    <div class="subtitle">
        Risk-aware CAN intrusion detection and defence monitoring
    </div>
    <div class="status" id="connection">Connecting to security logs...</div>
</header>

<section class="cards">
    <div class="card">
        <p>Total Incidents</p>
        <div class="number" id="total">0</div>
    </div>
    <div class="card">
        <p>Low Risk</p>
        <div class="number low" id="low">0</div>
    </div>
    <div class="card">
        <p>Medium Risk</p>
        <div class="number medium" id="medium">0</div>
    </div>
    <div class="card">
        <p>High Risk</p>
        <div class="number high" id="high">0</div>
    </div>
    <div class="card">
        <p>Critical Risk</p>
        <div class="number critical" id="critical">0</div>
    </div>
</section>
<section class="panel">
    <h2>Attack-Type Analytics</h2>
    <p class="subtitle">Distribution of detected attack evidence</p>
    <div class="bars" id="attackBars"></div>
</section>
<section class="panel">
    <h2>Risk Score Timeline</h2>
    <p class="subtitle">Risk progression across detected incidents (0–100)</p>
    <canvas id="riskChart" width="1000" height="280"
        style="width:100%; height:280px;"></canvas>
</section>
<section class="panel">
    <h2>Risk Level Distribution</h2>
    <div class="bars" id="bars"></div>
</section>

<section class="panel">
    <h2>Security Incident History</h2>
    <table>
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>CAN ID</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Recommended Action</th>
                <th>Evidence</th>
            </tr>
        </thead>
        <tbody id="incidentRows"></tbody>
    </table>
    <div class="empty" id="empty" hidden>No security incidents recorded yet.</div>
</section>

<div class="footer">
    Local monitoring dashboard | Refreshes every 3 seconds
</div>

<script>
const levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

function element(id) {
    return document.getElementById(id);
}

function makeCell(value) {
    const td = document.createElement("td");
    td.textContent = value;
    return td;
}

function renderBars(counts, total) {
    element("bars").replaceChildren();

    levels.forEach(level => {
        const count = counts[level];
        const percentage = total ? (count / total) * 100 : 0;

        const row = document.createElement("div");
        row.className = "bar-row";

        const label = document.createElement("span");
        label.textContent = level;

        const track = document.createElement("div");
        track.className = "track";

        const fill = document.createElement("div");
        fill.className = "fill " + level.toLowerCase();
        fill.style.width = percentage + "%";

        track.appendChild(fill);

        const number = document.createElement("span");
        number.textContent = count;

        row.append(label, track, number);
        element("bars").appendChild(row);
    });
}
function drawRiskTimeline(events) {
    const canvas = element("riskChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    const data = events.slice(-20);
    const left = 55;
    const right = 25;
    const top = 20;
    const bottom = 45;

    const chartWidth = width - left - right;
    const chartHeight = height - top - bottom;

    // Background grid and risk scale
    ctx.font = "13px Arial";
    ctx.textAlign = "right";
    ctx.fillStyle = "#9aabc1";

    [0, 25, 50, 75, 100].forEach(value => {
        const y = top + chartHeight * (1 - value / 100);

        ctx.strokeStyle = "#34445a";
        ctx.beginPath();
        ctx.moveTo(left, y);
        ctx.lineTo(width - right, y);
        ctx.stroke();

        ctx.fillText(value, left - 12, y + 4);
    });

    if (data.length === 0) {
        ctx.textAlign = "center";
        ctx.fillText("No incidents recorded yet", width / 2, height / 2);
        return;
    }

    const points = data.map((event, index) => ({
        x: data.length === 1
            ? left + chartWidth / 2
            : left + index * chartWidth / (data.length - 1),
        y: top + chartHeight *
            (1 - Math.min(100, Math.max(0, Number(event.risk_score) || 0)) / 100),
        score: Number(event.risk_score) || 0
    }));

    // Risk score line
    ctx.beginPath();
    ctx.strokeStyle = "#55d6a1";
    ctx.lineWidth = 3;

    points.forEach((point, index) => {
        if (index === 0) {
            ctx.moveTo(point.x, point.y);
        } else {
            ctx.lineTo(point.x, point.y);
        }
    });

    ctx.stroke();

    // Data points and score labels
    points.forEach(point => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#55d6a1";
        ctx.fill();

        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.fillText(point.score, point.x, point.y - 12);
    });

    // Incident numbers
    ctx.fillStyle = "#9aabc1";
    ctx.textAlign = "center";

    points.forEach((point, index) => {
        ctx.fillText(index + 1, point.x, height - 15);
    });
}
function renderAttackAnalytics(events) {
    const attackTypes = {
        "UNKNOWN CAN ID": 0,
        "HIGH CAN MESSAGE FREQUENCY": 0,
        "INVALID DATA LENGTH": 0,
        "RPM LIMIT EXCEEDED": 0,
        "SPEED LIMIT EXCEEDED": 0,
        "TEMPERATURE LIMIT EXCEEDED": 0
    };

    // Count evidence occurrences across recorded incidents
    events.forEach(event => {
        (event.evidence || []).forEach(item => {
            if (Object.hasOwn(attackTypes, item.reason)) {
                attackTypes[item.reason]++;
            }
        });
    });

    const container = element("attackBars");
    container.replaceChildren();

    const maximum = Math.max(1, ...Object.values(attackTypes));

    Object.entries(attackTypes).forEach(([name, count]) => {
        const row = document.createElement("div");
        row.className = "bar-row";

        const label = document.createElement("span");
        label.textContent = name;
        label.style.fontSize = "12px";

        const track = document.createElement("div");
        track.className = "track";

        const fill = document.createElement("div");
        fill.className = "fill high";
        fill.style.width = (count / maximum * 100) + "%";

        track.appendChild(fill);

        const number = document.createElement("span");
        number.textContent = count;

        row.append(label, track, number);
        container.appendChild(row);
    });
}
function renderEvents(events) {
    const counts = {
        LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0
    };

    events.forEach(event => {
        if (counts[event.risk_level] !== undefined) {
            counts[event.risk_level]++;
        }
    });

    element("total").textContent = events.length;

    levels.forEach(level => {
        element(level.toLowerCase()).textContent = counts[level];
    });

    renderBars(counts, events.length);
renderAttackAnalytics(events);
drawRiskTimeline(events);
    const tbody = element("incidentRows");
    tbody.replaceChildren();

    element("empty").hidden = events.length !== 0;

    [...events].reverse().forEach(event => {
        const row = document.createElement("tr");

        let timestamp = event.timestamp || "";
        timestamp = timestamp.replace("T", " ").replace("Z", "");

        const evidence = (event.evidence || [])
            .map(item => item.reason)
            .join(", ");

        const cells = [
            timestamp,
            event.can_id || "",
            event.risk_score ?? "",
        ];

        cells.forEach(value => row.appendChild(makeCell(value)));

        const levelCell = document.createElement("td");
        const tag = document.createElement("span");
        tag.className = "tag " + (event.risk_level || "");
        tag.textContent = event.risk_level || "UNKNOWN";
        levelCell.appendChild(tag);
        row.appendChild(levelCell);

        row.appendChild(makeCell(event.recommended_action || ""));
        row.appendChild(makeCell(evidence));

        tbody.appendChild(row);
    });
}

async function refreshDashboard() {
    try {
        const response = await fetch("/api/events?t=" + Date.now());

        if (!response.ok) {
            throw new Error("Unable to read incident logs");
        }

        const events = await response.json();
        renderEvents(events);

        element("connection").textContent =
            "● Connected | Live log monitoring active";

    } catch (error) {
        element("connection").textContent =
            "● Connection error | Check dashboard server";
    }
}

refreshDashboard();
setInterval(refreshDashboard, 3000);
</script>

</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.startswith("/api/events"):

            events = []

            try:
                if os.path.exists(EVENT_FILE):
                    with open(EVENT_FILE, "r", encoding="utf-8") as file:
                        for line in file:
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue

            except OSError:
                self.send_error(500, "Could not read incident log")
                return

            data = json.dumps(events).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        elif self.path == "/":

            data = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        else:
            self.send_error(404)


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("127.0.0.1", 8000),
        DashboardHandler
    )

    print("========================================")
    print("   AUTOMOTIVE ECU SECURITY DASHBOARD")
    print("========================================")
    print("Open: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    finally:
        server.server_close()
