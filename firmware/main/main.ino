/*
 * ============================================================
 *  🩺 WEARABLE HEALTH MONITORING SYSTEM
 * ============================================================
 *  Author    : Praveen Kumar
 *  Hardware  : ESP32 + MAX30102 + DS18B20 + SSD1306 OLED
 *  Protocol  : Wi-Fi (Built-in Web Server + ThingSpeak)
 *  IDE       : Arduino IDE 2.x
 * ============================================================
 */

// ─── LIBRARIES ───────────────────────────────────────────────
#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MAX30105.h>
#include <heartRate.h>
#include <spo2_algorithm.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ─── Wi-Fi CREDENTIALS ───────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_NAME";      // ← Change this
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // ← Change this

// ─── ThingSpeak (Optional Cloud) ─────────────────────────────
const char* TS_HOST    = "api.thingspeak.com";
const char* TS_API_KEY = "YOUR_THINGSPEAK_WRITE_KEY"; // ← Change this
const int   TS_INTERVAL = 20000; // Upload every 20 seconds

// ─── PIN DEFINITIONS ─────────────────────────────────────────
#define ONE_WIRE_BUS   4    // DS18B20 data pin → GPIO4
#define BUZZER_PIN    15    // Buzzer           → GPIO15
#define LED_GREEN     12    // Green LED        → GPIO12
#define LED_RED       13    // Red LED (alert)  → GPIO13
#define OLED_SDA      21    // OLED SDA         → GPIO21 (default)
#define OLED_SCL      22    // OLED SCL         → GPIO22 (default)

// ─── OLED SETUP ──────────────────────────────────────────────
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT  64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ─── SENSOR OBJECTS ──────────────────────────────────────────
MAX30105       particleSensor;
OneWire        oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);
WebServer      server(80);

// ─── GLOBAL HEALTH DATA ──────────────────────────────────────
struct HealthData {
  float  heartRate    = 0.0;
  int32_t spo2        = 0;
  float  bodyTemp     = 0.0;
  String status       = "Normal";
  String hrStatus     = "Normal";
  String spo2Status   = "Normal";
  String tempStatus   = "Normal";
  bool   alertActive  = false;
  unsigned long timestamp = 0;
} health;

// ─── HEART RATE BUFFERS ──────────────────────────────────────
const byte  RATE_SIZE = 4;
byte        rates[RATE_SIZE];
byte        rateSpot  = 0;
long        lastBeat  = 0;
float       beatsPerMinute;
int         beatAvg;

// MAX30102 SpO2 buffers
#define BUFFER_LENGTH 100
uint32_t irBuffer[BUFFER_LENGTH];
uint32_t redBuffer[BUFFER_LENGTH];
int32_t  spo2Val;
int8_t   validSPO2;
int32_t  heartRateVal;
int8_t   validHeartRate;

unsigned long lastTSUpload = 0;
unsigned long lastSensorRead = 0;
int oledPage = 0;

// ─── SETUP ───────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n🩺 Health Monitor Booting...");

  // GPIO Setup
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_GREEN,  OUTPUT);
  pinMode(LED_RED,    OUTPUT);
  digitalWrite(LED_GREEN, HIGH);  // Green ON = system alive

  // OLED Init
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("❌ OLED not found!");
    while (true);
  }
  showBootScreen();

  // MAX30102 Init
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("❌ MAX30102 not found!");
    displayError("MAX30102 Missing!");
    while (true);
  }
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
  Serial.println("✅ MAX30102 Ready");

  // DS18B20 Init
  tempSensor.begin();
  Serial.println("✅ DS18B20 Ready");

  // Wi-Fi Connect
  connectWiFi();

  // Web Server Routes
  server.on("/",          handleRoot);
  server.on("/data",      handleData);
  server.on("/history",   handleHistory);
  server.onNotFound([]() { server.send(404, "text/plain", "Not Found"); });
  server.begin();
  Serial.println("✅ Web Server Started");
  Serial.print("📡 Open: http://");
  Serial.println(WiFi.localIP());

  displayReady();
}

// ─── MAIN LOOP ───────────────────────────────────────────────
void loop() {
  server.handleClient();

  // Read sensors every 2 seconds
  if (millis() - lastSensorRead > 2000) {
    readTemperature();
    readHeartRateSpO2();
    evaluateHealth();
    updateOLED();
    lastSensorRead = millis();
  }

  // ThingSpeak upload every 20 seconds
  if (millis() - lastTSUpload > TS_INTERVAL) {
    uploadToThingSpeak();
    lastTSUpload = millis();
  }

  // Cycle OLED page every 4 seconds
  static unsigned long lastPageFlip = 0;
  if (millis() - lastPageFlip > 4000) {
    oledPage = (oledPage + 1) % 3;
    lastPageFlip = millis();
  }
}

// ─── READ BODY TEMPERATURE ───────────────────────────────────
void readTemperature() {
  tempSensor.requestTemperatures();
  float raw = tempSensor.getTempCByIndex(0);
  if (raw != DEVICE_DISCONNECTED_C) {
    health.bodyTemp = raw;
  }
}

// ─── READ HEART RATE & SpO2 ──────────────────────────────────
void readHeartRateSpO2() {
  // Collect 100 samples
  for (byte i = 0; i < BUFFER_LENGTH; i++) {
    while (!particleSensor.available())
      particleSensor.check();
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i]  = particleSensor.getIR();
    particleSensor.nextSample();
  }

  // Calculate HR and SpO2
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, BUFFER_LENGTH, redBuffer,
    &spo2Val, &validSPO2, &heartRateVal, &validHeartRate
  );

  if (validHeartRate && heartRateVal > 20 && heartRateVal < 220)
    health.heartRate = heartRateVal;
  if (validSPO2 && spo2Val > 80)
    health.spo2 = spo2Val;

  health.timestamp = millis();
}

// ─── EVALUATE HEALTH STATUS ──────────────────────────────────
void evaluateHealth() {
  health.alertActive = false;

  // Heart Rate
  if      (health.heartRate < 60)  { health.hrStatus = "Low (Bradycardia)";  health.alertActive = true; }
  else if (health.heartRate > 100) { health.hrStatus = "High (Tachycardia)"; health.alertActive = true; }
  else                              { health.hrStatus = "Normal"; }

  // SpO2
  if      (health.spo2 < 90) { health.spo2Status = "Critical (Low O2)"; health.alertActive = true; }
  else if (health.spo2 < 95) { health.spo2Status = "Low";               health.alertActive = true; }
  else                        { health.spo2Status = "Normal"; }

  // Temperature
  if      (health.bodyTemp > 38.5) { health.tempStatus = "High (Fever)";     health.alertActive = true; }
  else if (health.bodyTemp > 37.5) { health.tempStatus = "Slightly High";     health.alertActive = true; }
  else if (health.bodyTemp < 36.0) { health.tempStatus = "Low (Hypothermia)"; health.alertActive = true; }
  else                              { health.tempStatus = "Normal"; }

  // Overall Status
  health.status = health.alertActive ? "⚠️ Alert" : "✅ Normal";

  // LEDs & Buzzer
  if (health.alertActive) {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
    tone(BUZZER_PIN, 1000, 200);
  } else {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
    noTone(BUZZER_PIN);
  }

  // Serial Monitor
  Serial.printf("❤️  HR: %.0f bpm | 🩸 SpO2: %d%% | 🌡️  Temp: %.1f°C | %s\n",
    health.heartRate, health.spo2, health.bodyTemp, health.status.c_str());
}

// ─── OLED DISPLAY ────────────────────────────────────────────
void updateOLED() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  switch (oledPage) {
    case 0: // Heart Rate page
      display.setTextSize(1);
      display.setCursor(30, 0);
      display.println("HEART RATE");
      display.drawLine(0, 10, 127, 10, SSD1306_WHITE);
      display.setTextSize(3);
      display.setCursor(20, 18);
      display.printf("%.0f", health.heartRate);
      display.setTextSize(1);
      display.setCursor(80, 28);
      display.println("bpm");
      display.setCursor(10, 52);
      display.println(health.hrStatus);
      break;

    case 1: // SpO2 page
      display.setTextSize(1);
      display.setCursor(35, 0);
      display.println("BLOOD SpO2");
      display.drawLine(0, 10, 127, 10, SSD1306_WHITE);
      display.setTextSize(3);
      display.setCursor(20, 18);
      display.printf("%d", health.spo2);
      display.setTextSize(1);
      display.setCursor(80, 28);
      display.println("%");
      display.setCursor(10, 52);
      display.println(health.spo2Status);
      break;

    case 2: // Temperature page
      display.setTextSize(1);
      display.setCursor(25, 0);
      display.println("BODY TEMPERATURE");
      display.drawLine(0, 10, 127, 10, SSD1306_WHITE);
      display.setTextSize(2);
      display.setCursor(15, 20);
      display.printf("%.1f C", health.bodyTemp);
      display.setTextSize(1);
      display.setCursor(10, 45);
      display.println(health.tempStatus);
      display.setCursor(0, 56);
      display.printf("IP: %s", WiFi.localIP().toString().c_str());
      break;
  }

  display.display();
}

// ─── WEB SERVER: MAIN DASHBOARD ──────────────────────────────
void handleRoot() {
  String html = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🩺 Health Monitor Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      min-height: 100vh; color: #fff;
    }
    header {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(10px);
      padding: 20px 30px;
      display: flex; align-items: center; gap: 15px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    header h1 { font-size: 1.6rem; font-weight: 700; }
    header p  { font-size: 0.85rem; color: #aaa; }
    .pulse-dot {
      width: 12px; height: 12px; border-radius: 50%;
      background: #00ff88; animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0%,100% { transform: scale(1); opacity: 1; }
      50%      { transform: scale(1.4); opacity: 0.6; }
    }
    .dashboard {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px; padding: 30px;
    }
    .card {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 20px;
      padding: 25px;
      backdrop-filter: blur(10px);
      transition: transform 0.3s, box-shadow 0.3s;
    }
    .card:hover { transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
    .card-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .card-label { font-size: 0.85rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    .card-value { font-size: 3rem; font-weight: 800; margin: 8px 0; }
    .card-unit  { font-size: 1rem; color: #ccc; }
    .card-status {
      display: inline-block;
      padding: 4px 12px; border-radius: 20px;
      font-size: 0.8rem; font-weight: 600;
      margin-top: 8px;
    }
    .normal  { background: rgba(0,255,136,0.2); color: #00ff88; }
    .warning { background: rgba(255,200,0,0.2);  color: #ffc800; }
    .danger  { background: rgba(255,50,50,0.2);  color: #ff3232; }
    .hr-card    { border-top: 4px solid #ff6b6b; }
    .spo2-card  { border-top: 4px solid #4ecdc4; }
    .temp-card  { border-top: 4px solid #ffa500; }
    .overall-card { border-top: 4px solid #9b59b6; grid-column: 1 / -1; }
    .overall-inner {
      display: flex; gap: 30px; align-items: center;
      flex-wrap: wrap;
    }
    .big-status { font-size: 2rem; font-weight: 800; }
    .mini-stats { display: flex; gap: 20px; flex-wrap: wrap; margin-top: 10px; }
    .mini-stat  { background: rgba(255,255,255,0.08); border-radius: 10px; padding: 10px 18px; }
    .mini-stat .label { font-size: 0.75rem; color: #aaa; }
    .mini-stat .val   { font-size: 1.3rem; font-weight: 700; }
    footer {
      text-align: center; padding: 20px;
      color: #666; font-size: 0.8rem;
    }
    .refresh-bar {
      background: rgba(255,255,255,0.05);
      padding: 10px 30px;
      display: flex; justify-content: space-between;
      font-size: 0.85rem; color: #888;
    }
    #lastUpdate { color: #00ff88; }
    .chart-container {
      background: rgba(255,255,255,0.04);
      border-radius: 12px; padding: 15px; margin-top: 15px;
    }
    canvas { width: 100% !important; max-height: 80px; }
  </style>
</head>
<body>
  <header>
    <div class="pulse-dot"></div>
    <div>
      <h1>🩺 Wearable Health Monitor</h1>
      <p>Real-Time IoT Sensor Dashboard &nbsp;|&nbsp; ESP32 Wi-Fi</p>
    </div>
  </header>

  <div class="refresh-bar">
    <span>📡 Auto-refresh every 2s</span>
    <span>Last updated: <span id="lastUpdate">—</span></span>
  </div>

  <div class="dashboard">
    <!-- Heart Rate Card -->
    <div class="card hr-card">
      <div class="card-icon">❤️</div>
      <div class="card-label">Heart Rate</div>
      <div class="card-value" id="hr">--</div>
      <div class="card-unit">beats per minute</div>
      <span class="card-status" id="hrStatus">—</span>
      <div class="chart-container">
        <canvas id="hrChart"></canvas>
      </div>
    </div>

    <!-- SpO2 Card -->
    <div class="card spo2-card">
      <div class="card-icon">🩸</div>
      <div class="card-label">Blood Oxygen (SpO₂)</div>
      <div class="card-value" id="spo2">--</div>
      <div class="card-unit">percent (%)</div>
      <span class="card-status" id="spo2Status">—</span>
      <div class="chart-container">
        <canvas id="spo2Chart"></canvas>
      </div>
    </div>

    <!-- Temperature Card -->
    <div class="card temp-card">
      <div class="card-icon">🌡️</div>
      <div class="card-label">Body Temperature</div>
      <div class="card-value" id="temp">--</div>
      <div class="card-unit">degrees Celsius (°C)</div>
      <span class="card-status" id="tempStatus">—</span>
    </div>

    <!-- Overall Status Card -->
    <div class="card overall-card">
      <div class="card-label">Overall Health Status</div>
      <div class="overall-inner">
        <div class="big-status" id="overallStatus">Connecting...</div>
        <div>
          <div class="mini-stats">
            <div class="mini-stat">
              <div class="label">❤️ HR</div>
              <div class="val" id="hrMini">--</div>
            </div>
            <div class="mini-stat">
              <div class="label">🩸 SpO₂</div>
              <div class="val" id="spo2Mini">--</div>
            </div>
            <div class="mini-stat">
              <div class="label">🌡️ Temp</div>
              <div class="val" id="tempMini">--</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    🔬 ESP32 Wearable Health Monitor &nbsp;|&nbsp; IoT Project &nbsp;|&nbsp; Praveen Kumar
  </footer>

  <script>
    // Mini sparkline chart
    function drawSparkline(canvasId, data, color) {
      const c = document.getElementById(canvasId);
      if (!c || data.length < 2) return;
      const ctx = c.getContext('2d');
      c.width = c.offsetWidth; c.height = 80;
      const w = c.width, h = c.height;
      const min = Math.min(...data) * 0.95;
      const max = Math.max(...data) * 1.05;
      ctx.clearRect(0, 0, w, h);
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.shadowBlur = 8; ctx.shadowColor = color;
      data.forEach((v, i) => {
        const x = (i / (data.length-1)) * w;
        const y = h - ((v - min) / (max - min)) * h;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      });
      ctx.stroke();
      // Fill gradient
      ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath();
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, color + '44');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad; ctx.fill();
    }

    const hrHistory   = [];
    const spo2History = [];

    function statusClass(s) {
      if (s.includes('Normal')) return 'normal';
      if (s.includes('Critical') || s.includes('High') || s.includes('Low (')) return 'danger';
      return 'warning';
    }

    async function fetchData() {
      try {
        const res  = await fetch('/data');
        const d    = await res.json();

        document.getElementById('hr').textContent    = d.heartRate.toFixed(0);
        document.getElementById('spo2').textContent  = d.spo2;
        document.getElementById('temp').textContent  = d.bodyTemp.toFixed(1);

        const hrEl = document.getElementById('hrStatus');
        hrEl.textContent = d.hrStatus; hrEl.className = 'card-status ' + statusClass(d.hrStatus);

        const sEl = document.getElementById('spo2Status');
        sEl.textContent = d.spo2Status; sEl.className = 'card-status ' + statusClass(d.spo2Status);

        const tEl = document.getElementById('tempStatus');
        tEl.textContent = d.tempStatus; tEl.className = 'card-status ' + statusClass(d.tempStatus);

        const ov = document.getElementById('overallStatus');
        ov.textContent  = d.status;
        ov.style.color  = d.alertActive ? '#ff3232' : '#00ff88';

        document.getElementById('hrMini').textContent   = d.heartRate.toFixed(0) + ' bpm';
        document.getElementById('spo2Mini').textContent = d.spo2 + '%';
        document.getElementById('tempMini').textContent  = d.bodyTemp.toFixed(1) + '°C';

        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();

        hrHistory.push(d.heartRate);   if (hrHistory.length > 20) hrHistory.shift();
        spo2History.push(d.spo2);      if (spo2History.length > 20) spo2History.shift();

        drawSparkline('hrChart',   hrHistory,   '#ff6b6b');
        drawSparkline('spo2Chart', spo2History, '#4ecdc4');

      } catch(e) { document.getElementById('overallStatus').textContent = '⚠️ Reconnecting...'; }
    }

    fetchData();
    setInterval(fetchData, 2000);
  </script>
</body>
</html>
)rawhtml";
  server.send(200, "text/html", html);
}

// ─── WEB SERVER: JSON DATA ENDPOINT ──────────────────────────
void handleData() {
  StaticJsonDocument<256> doc;
  doc["heartRate"]   = health.heartRate;
  doc["spo2"]        = health.spo2;
  doc["bodyTemp"]    = health.bodyTemp;
  doc["status"]      = health.status;
  doc["hrStatus"]    = health.hrStatus;
  doc["spo2Status"]  = health.spo2Status;
  doc["tempStatus"]  = health.tempStatus;
  doc["alertActive"] = health.alertActive;
  doc["timestamp"]   = health.timestamp;

  String json;
  serializeJson(doc, json);
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// ─── WEB SERVER: HISTORY PLACEHOLDER ─────────────────────────
void handleHistory() {
  server.send(200, "text/plain", "History endpoint - SPIFFS logging coming soon!");
}

// ─── THINGSPEAK UPLOAD ────────────────────────────────────────
void uploadToThingSpeak() {
  if (WiFi.status() != WL_CONNECTED) return;
  WiFiClient client;
  if (!client.connect(TS_HOST, 80)) return;

  String url = String("/update?api_key=") + TS_API_KEY
             + "&field1=" + health.heartRate
             + "&field2=" + health.spo2
             + "&field3=" + health.bodyTemp;

  client.print(String("GET ") + url + " HTTP/1.1\r\n"
             + "Host: " + TS_HOST + "\r\n"
             + "Connection: close\r\n\r\n");
  delay(100);
  client.stop();
  Serial.println("📤 ThingSpeak updated");
}

// ─── WI-FI CONNECTION ────────────────────────────────────────
void connectWiFi() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Connecting to WiFi...");
  display.println(WIFI_SSID);
  display.display();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\n✅ WiFi Connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n⚠️ WiFi Failed — Running offline");
  }
}

// ─── OLED HELPERS ────────────────────────────────────────────
void showBootScreen() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 5);
  display.println("HEALTH");
  display.println("MONITOR");
  display.setTextSize(1);
  display.setCursor(20, 48);
  display.println("Booting System...");
  display.display();
  delay(2000);
}

void displayReady() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("System Ready!");
  display.println("");
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.println("Open in Browser ↑");
  display.display();
  delay(3000);
}

void displayError(String msg) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 10);
  display.println("ERROR:");
  display.println(msg);
  display.display();
}

