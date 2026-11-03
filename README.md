<div align="center">

# 🩺 Wearable Health Monitoring System

### IoT-Based Real-Time Patient Vitals using ESP32 & Wi-Fi

![ESP32](https://img.shields.io/badge/ESP32-Wi--Fi-blue?style=for-the-badge&logo=espressif)
![Arduino](https://img.shields.io/badge/Arduino-Framework-00979D?style=for-the-badge&logo=arduino)
![IoT](https://img.shields.io/badge/IoT-Health-ff6b6b?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**Monitor Heart Rate ❤️ | Blood Oxygen 🩸 | Body Temperature 🌡️ — wirelessly, in real-time.**

[📖 Documentation](#-project-overview) • [⚡ Quick Start](#-quick-start) • [🔌 Wiring](#-circuit-wiring) • [🌐 Dashboard](#-web-dashboard) • [☁️ Cloud](#-thingspeak-cloud)

</div>

---

## 📋 Project Overview

This project implements a **real-time wearable health monitoring system** using IoT sensors connected to an **ESP32 microcontroller**. Health data is transmitted wirelessly over **Wi-Fi (IEEE 802.11)** and displayed on:

- 📟 A built-in **OLED display** on the wearable itself
- 🌐 A **live web dashboard** on any phone/browser on the same Wi-Fi
- ☁️ **ThingSpeak cloud** for remote monitoring & data logging
- 🔔 **LED + Buzzer alerts** for abnormal readings

> **Cost:** ₹600–₹900 (~$8–$12 USD) | **Level:** Beginner Friendly

---

## ✨ Features

| Feature | Description |
|---|---|
| ❤️ **Heart Rate** | Measures BPM via MAX30102 optical PPG sensor |
| 🩸 **SpO₂** | Blood oxygen saturation percentage |
| 🌡️ **Temperature** | Body temperature via DS18B20 (1-Wire) |
| 📡 **Wi-Fi Streaming** | Real-time data over IEEE 802.11 b/g/n |
| 🌐 **Web Dashboard** | Self-hosted HTML/CSS/JS — no internet needed |
| 📊 **Live Charts** | Sparkline trend graphs, auto-refresh every 2s |
| 🔔 **Smart Alerts** | LED + buzzer on abnormal vitals |
| ☁️ **Cloud Logging** | ThingSpeak upload every 20 seconds |
| 📟 **OLED Display** | Local 128×64 display cycles 3 pages |
| 🔌 **REST API** | JSON endpoint at `/data` for integrations |

---

## 🔩 Hardware Components

| Component | Model | Purpose |
|---|---|---|
| Microcontroller | **ESP32 Dev Board** | MCU + Wi-Fi |
| Heart Rate + SpO₂ | **MAX30102** | Optical PPG sensor |
| Body Temperature | **DS18B20** | 1-Wire digital temp |
| Display | **SSD1306 OLED 128×64** | Local readout |
| Alert Sound | **Passive Buzzer** | Audio alerts |
| Alert Light | **Red + Green LED** | Visual status |
| Power | **Li-Po 3.7V + TP4056** | Rechargeable battery |

---

## 🔌 Circuit Wiring

```
┌──────────────────────────────────────────────────────────┐
│                    ESP32 DEV BOARD                        │
│                                                           │
│  3.3V ──┬── VCC (MAX30102)  ── VCC (SSD1306 OLED)        │
│  GND  ──┼── GND (MAX30102)  ── GND (SSD1306)             │
│          └── GND (DS18B20 Black) ── GND (Buzzer/LEDs)    │
│                                                           │
│  GPIO21 (SDA) ─── SDA (MAX30102 + SSD1306)               │
│  GPIO22 (SCL) ─── SCL (MAX30102 + SSD1306)               │
│  GPIO4        ─── Data (DS18B20) + 4.7kΩ → 3.3V          │
│  GPIO15       ─── Buzzer (+)                              │
│  GPIO12       ─── 220Ω ─── Green LED (+)                  │
│  GPIO13       ─── 220Ω ─── Red LED (+)                    │
│  5V           ─── VIN (DS18B20 Red)                       │
└──────────────────────────────────────────────────────────┘
```

> **Note:** MAX30102 (I2C: 0x57) and SSD1306 (I2C: 0x3C) share the same I2C bus — this is by design.

---

## ⚡ Quick Start

### 1. Install Arduino IDE & ESP32 Board

```
File → Preferences → Additional Board Manager URLs:
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

Tools → Board → Boards Manager → search "esp32" → Install
```

### 2. Install Required Libraries

Open **Arduino IDE → Tools → Manage Libraries** and install:

```
✅ Adafruit SSD1306
✅ Adafruit GFX Library
✅ SparkFun MAX3010x Pulse and Proximity Sensor Library
✅ DallasTemperature
✅ OneWire
✅ ArduinoJson
```

### 3. Configure Wi-Fi

Open [`firmware/main/main.ino`](firmware/main/main.ino) and edit:

```cpp
const char* WIFI_SSID     = "YOUR_WIFI_NAME";      // ← Change this
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // ← Change this
```

### 4. Upload & Connect

```
Tools → Board → ESP32 Dev Module
Tools → Port  → COMx (your port)
Click Upload (→)
```

### 5. Open Dashboard

```
Open Serial Monitor (115200 baud)
Copy the IP address shown:  📡 Open: http://192.168.x.x
Paste in any browser on the same Wi-Fi
```

---

## 🌐 Web Dashboard

The ESP32 hosts a full responsive dashboard at `http://<ESP32-IP>/`:

- **❤️ Heart Rate card** with live sparkline
- **🩸 SpO₂ card** with live sparkline
- **🌡️ Temperature card**
- **📋 Overall Status** — color-coded (green/yellow/red)
- Auto-refreshes every **2 seconds**

### JSON API

```bash
GET http://<ESP32-IP>/data
```

```json
{
  "heartRate": 72.0,
  "spo2": 98,
  "bodyTemp": 36.8,
  "status": "Normal",
  "hrStatus": "Normal",
  "spo2Status": "Normal",
  "tempStatus": "Normal",
  "alertActive": false
}
```

---

## 🌡️ Health Alert Thresholds

| Parameter | Normal | Warning | Critical |
|---|---|---|---|
| Heart Rate | 60–100 BPM | < 60 or > 100 | — |
| SpO₂ | 95–100% | 90–94% | < 90% |
| Body Temp | 36.1–37.5°C | > 37.5°C (Fever) | < 36°C (Hypothermia) |

When any value goes out of range → 🔴 Red LED + 🔊 Buzzer beep + Dashboard badge turns red.

---

## ☁️ ThingSpeak Cloud

1. Sign up at [thingspeak.com](https://thingspeak.com) (free)
2. Create a channel with 3 fields: Heart Rate, SpO₂, Temperature
3. Copy your **Write API Key** into `main.ino`:
   ```cpp
   const char* TS_API_KEY = "YOUR_API_KEY_HERE";
   ```
4. Data uploads every 20 seconds automatically

---

## 📁 Project Structure

```
HealthMonitor-IoT/
│
├── firmware/
│   ├── main/
│   │   └── main.ino              ← Main ESP32 sketch
│   └── libraries_required.txt    ← Library install guide
│
├── docs/
│   └── HealthMonitor-ProjectDoc.md   ← Full documentation
│
├── generate_pptx.py              ← Generates the PPTX presentation
├── HealthMonitor_Presentation.pptx   ← 15-slide PowerPoint
└── README.md
```

---

## 🔮 Future Enhancements

- 💾 SPIFFS data logging (on-device history)
- 📱 Flutter mobile companion app
- 🤖 TensorFlow Lite anomaly detection
- 📧 Email / SMS alerts via Twilio
- 🔋 Deep Sleep for 24h+ battery life
- 🔐 HTTPS + login authentication
- 📍 GPS patient location tracking

---

## 🧰 Technologies Used

| Technology | Role |
|---|---|
| ESP32 Wi-Fi (IEEE 802.11) | Wireless communication |
| MAX30102 PPG | Heart rate & SpO₂ sensing |
| DS18B20 1-Wire | Temperature sensing |
| I2C Protocol | OLED + sensor communication |
| HTTP REST API | JSON data endpoint |
| ThingSpeak | IoT cloud analytics |
| Arduino Framework | Firmware development |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Made with ❤️ by **Praveen Kumar**

*Wireless Communication & IoT Project — 2026*

⭐ **Star this repo if you found it useful!** ⭐

</div>

