#include <WiFi.h>
#include <PubSubClient.h>

// --- USER CONFIGURATION ---
const char* ssid = "PTCL-BB";
const char* password = "";

const char* mqtt_server = "192.168.10.12"; 
const char* mqtt_topic = "home/sensors/data";
const char* mqtt_user = "chick";
const char* mqtt_pass = "tastychicken";

// --- PINS ---
#define TRIG1 5 
#define ECHO1 18
#define TRIG2 19
#define ECHO2 21

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32_Intruder_System", mqtt_user, mqtt_pass)) {
      Serial.println("MQTT Connected");
    } else {
      delay(5000);
    }
  }
}

float getDistance(int trig, int echo) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH, 25000); // 25ms timeout
  if (duration == 0) return 999; // No echo
  return duration * 0.0343 / 2;
}

void sendData(String room, float dist) {
  String payload = "{\"room\": \"" + room + "\", \"distance\": " + String(dist) + "}";
  client.publish(mqtt_topic, payload.c_str());
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG1, OUTPUT); pinMode(ECHO1, INPUT);
  pinMode(TRIG2, OUTPUT); pinMode(ECHO2, INPUT);
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float d1 = getDistance(TRIG1, ECHO1);
  float d2 = getDistance(TRIG2, ECHO2);
Serial.println(d1);
Serial.println(d2);

  // Send data ONLY if object is close (Active Intrusion)
  // We send continuously while active so the server knows the "Event" is ongoing.
  if (d1 < 15 && d1 > 0) sendData("Room1", d1);
  if (d2 < 15 && d2 > 0) sendData("Room2", d2);

  delay(200); // Fast update rate for smooth tracking
}