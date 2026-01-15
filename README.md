# Smart Intruder Alert System (SIAS)

**Scalable Multi-Room IoT Security with Centralized Processing**

SIAS is an end-to-end IoT security pipeline that replaces fragmented, expensive security hardware with a centralized ESP32 hub. It monitors multiple zones simultaneously using ultrasonic sensors, transmits data via MQTT, and provides real-time alerts through a Python Flask backend and a modern web dashboard.

---

## 📖 Overview

Traditional security systems often require dedicated hardware for every room, leading to high costs and data fragmentation. SIAS solves this by using a **Four-Layer Architecture**:

1.  **Hardware Layer:** Sensors capture physical data (distance) and transmit it to the hub.
2.  **Network Layer:** MQTT Broker handles high-speed, low-bandwidth messaging.
3.  **Backend Layer:** Intelligent logic filters noise and manages event states.
4.  **Frontend/Data Layer:** A unified command center for visualization and historical logging.

---

## 🚀 Key Features

* **Centralized Intelligence:** A single ESP32 manages sensors across multiple rooms, reducing hardware costs.
* **Real-Time Latency:** Sub-second data transmission using the lightweight MQTT protocol.
* **Smart Event Filtering:** Distinguishes actual intrusions from fleeting motion using stateful tracking (events auto-close after 3 seconds of inactivity).
* **Live Dashboard:** View real-time status (Secure/Intrusion) and arm/disarm the system via a web interface.
* **Historical Auditing:** All intrusion events are timestamped and logged in MongoDB for future analysis.

---

## 🛠 Tech Stack

### Hardware
* **Controller:** ESP32 Development Module (Wi-Fi enabled).
* **Sensors:** HC-SR04 Ultrasonic Sensors (Precision detection).
* **Wiring:** GPIO direct connections (Triggers/Echoes).

### Software & Protocols
* **Communication:** MQTT (Message Queuing Telemetry Transport).
* **Broker:** Eclipse Mosquitto.
* **Backend Framework:** Python Flask (with Flask-SocketIO).
* **Database:** MongoDB (NoSQL storage for event logs).
* **Frontend:** HTML5, CSS3, JavaScript (WebSockets).

### Libraries
* **ESP32/Arduino:** `PubSubClient` (for MQTT).
* **Python:** `paho-mqtt` (MQTT client), `pymongo` (Database driver).

---

## 🏗 Architecture

The system operates on a seamless data pipeline:

1.  **Sensing:** The HC-SR04 sensors detect objects within a specific range (e.g., <15cm).
2.  **Publishing:** The ESP32 formats this as JSON (`{"room": "Room1", "distance": 12.3}`) and publishes to the MQTT topic `home/sensors/data`.
3.  **Processing:** The Python Flask server subscribes to the topic. It processes the stream, checking for active events.
4.  **Alerting:** If an intrusion is confirmed, the server pushes an update to the Web Dashboard via SocketIO.
5.  **Logging:** When an event ends (timeout > 3.0s), the start time, end time, and nearest distance are stored in MongoDB.

---

## ⚙️ Installation & Setup

### 1. Hardware Setup
Connect the Ultrasonic Sensors to the ESP32 GPIO pins as defined in the firmware:
* **Sensor 1:** Trigger -> GPIO 5, Echo -> GPIO 18
* **Sensor 2:** Trigger -> GPIO 19, Echo -> GPIO 21

### 2. MQTT Broker
Ensure you have an MQTT broker running (Mosquitto).
