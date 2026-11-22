<div align="center">

# 🚗 VEHISEC
### Intelligent Automotive Cybersecurity & CAN Bus Intrusion Detection System

**Securing Connected Vehicles Through Real-Time Monitoring, Authentication and Threat Detection**

<br>

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Automotive](https://img.shields.io/badge/Domain-Automotive%20Security-red?style=for-the-badge)
![CAN Bus](https://img.shields.io/badge/Protocol-CAN%20Bus-black?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-HMAC--SHA256-green?style=for-the-badge)

</div>

---

## 📌 Overview

**VEHISEC** is an automotive cybersecurity project designed to monitor vehicle communication networks and identify suspicious activities in Controller Area Network (CAN) traffic.

Modern vehicles rely on interconnected Electronic Control Units (ECUs) to exchange critical information. However, these communication networks can be vulnerable to unauthorized messages, abnormal traffic patterns and malicious manipulation.

VEHISEC addresses these challenges through CAN message monitoring, authentication mechanisms, anomaly detection and vehicle data visualization.

## 🎯 Key Features

- 🔐 **ECU Authentication:** Uses HMAC-SHA256-based message authentication.
- 📡 **CAN Bus Monitoring:** Monitors real-time CAN communication.
- 🚨 **Intrusion Detection:** Identifies unknown CAN IDs and abnormal message activity.
- 📊 **Vehicle Monitoring:** Tracks RPM, speed and temperature.
- ⚡ **Anomaly Detection:** Detects abnormal vehicle parameters and excessive CAN message frequency.
- 📝 **Event Logging:** Stores detected anomalies in CSV format.
- 📈 **Dashboard Visualization:** Provides a visual interface for monitoring vehicle security events.

## 🏗️ System Architecture

```text
        VEHICLE ENVIRONMENT
                |
                ▼
       ┌──────────────────┐
       │   ENGINE ECU     │
       │ RPM / Speed /Temp│
       └────────┬─────────┘
                |
                ▼
       ┌──────────────────┐
       │ ECU AUTHENTICATION│
       │   HMAC-SHA256    │
       └────────┬─────────┘
                |
                ▼
       ┌──────────────────┐
       │    CAN BUS       │
       │   Communication  │
       └────────┬─────────┘
                |
                ▼
       ┌──────────────────┐
       │  CAN DETECTOR    │
       │ Anomaly Detection│
       └────────┬─────────┘
                |
          ┌─────┴─────┐
          ▼           ▼
    ┌──────────┐ ┌───────────┐
    │ CSV Logs │ │ Risk Engine│
    └──────────┘ └─────┬─────┘
                       |
                       ▼
              ┌────────────────┐
              │ VEHICLE SECURITY│
              │   DASHBOARD     │
              └────────────────┘
```

## ⚙️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core development |
| SocketCAN | CAN communication |
| python-can | CAN message transmission and reception |
| HMAC-SHA256 | Message authentication |
| CSV | Event logging |
| Linux Virtual CAN | CAN network simulation |
| Dashboard | Vehicle monitoring and visualization |

## 📂 Project Structure

```text
VEHISEC/
│
├── authenticated_ecu.py
├── can_detector.py
├── vehicle_monitor.py
├── dashboard.py
├── dashboard_app.py
│
├── defence/
│   └── risk_engine.py
│
├── crypto_security.py
│
├── logs/
│   └── can_log.csv
│
└── README.md
```

*Additional modules shown above are required by imports in the existing source code and should be included in the repository.*

## 🔍 Detection Capabilities

VEHISEC monitors CAN communication for suspicious activities, including:

| Security Check | Description |
|---|---|
| Unknown CAN ID | Detects unauthorized CAN identifiers |
| RPM Monitoring | Identifies excessive engine RPM |
| Speed Monitoring | Detects abnormal speed values |
| Temperature Monitoring | Identifies high temperature readings |
| Message Frequency | Detects excessive CAN traffic |
| Data Validation | Checks invalid CAN payload lengths |

## 🔐 ECU Authentication

VEHISEC implements an HMAC-SHA256-based authentication mechanism for vehicle communication.

The authenticated ECU generates vehicle parameters and creates an authenticated CAN payload before transmission.

This helps the receiving system verify message authenticity and protect against unauthorized message injection.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Sai-kiranj/VEHISEC.git
cd VEHISEC
```

### 2. Install Dependencies

```bash
pip install python-can
```

Install any additional dependencies required by the dashboard and security modules.

### 3. Configure Virtual CAN

On Linux:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### 4. Run the ECU Simulation

```bash
python authenticated_ecu.py
```

### 5. Run the CAN Detector

Open another terminal:

```bash
python can_detector.py
```

### 6. Launch Vehicle Monitoring

Run the monitoring and dashboard scripts according to their respective configurations.

## 📊 Expected Output

The system monitors vehicle parameters such as:

- Engine RPM
- Vehicle Speed
- Engine Temperature
- CAN Message Frequency
- Authentication Status
- Security Anomaly Status

Detected security events are recorded for further analysis.

## 🔮 Future Enhancements

- Integration with physical CAN hardware.
- Machine-learning-based intrusion detection.
- Advanced ECU authentication mechanisms.
- Real-time security alert notifications.
- Cloud-based vehicle monitoring.
- Enhanced cybersecurity dashboard.

## 👨‍💻 Developer

**Sai Kiran J**
**Vishwas V**
**Vaishnavi V**

Electronics and Communication Engineering

**Areas of Interest:**
Embedded Systems | Automotive Electronics | IoT | Cybersecurity | Vehicle Networks

---

<div align="center">

### 🔒 VEHISEC
**Building Safer and Smarter Connected Vehicles.**

⭐ If you find this project interesting, consider giving it a star!

</div>
