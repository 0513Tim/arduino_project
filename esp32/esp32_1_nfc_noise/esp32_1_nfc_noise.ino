#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* API_BASE_URL = "http://192.168.1.100:8000";

constexpr uint8_t RST_PIN = 22;
constexpr uint8_t SS_PIN = 21;
constexpr int SOUND_PIN = 34;
constexpr int SEAT_NO = 1;

MFRC522 mfrc522(SS_PIN, RST_PIN);

String lastUid = "";
unsigned long lastNoisePost = 0;
const unsigned long noiseIntervalMs = 3000;

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi connected");
  Serial.println(WiFi.localIP());
}

String readUid() {
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) {
      uid += "0";
    }
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}

void postJson(const String& path, const String& jsonBody) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected, reconnecting...");
    connectWiFi();
  }

  HTTPClient http;
  http.begin(String(API_BASE_URL) + path);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(jsonBody);

  Serial.printf("POST %s => %d\n", path.c_str(), httpCode);
  if (httpCode > 0) {
    Serial.println(http.getString());
  } else {
    Serial.printf("HTTP error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  pinMode(SOUND_PIN, INPUT);
  connectWiFi();
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = readUid();
    if (uid != lastUid) {
      lastUid = uid;
      Serial.printf("NFC UID: %s\n", uid.c_str());
      String payload = "{\"nfc_uid\":\"" + uid + "\",\"seat_no\":" + String(SEAT_NO) + "}";
      postJson("/checkin", payload);
    }
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }

  if (millis() - lastNoisePost >= noiseIntervalMs) {
    lastNoisePost = millis();
    int noiseValue = analogRead(SOUND_PIN);
    Serial.printf("Noise value: %d\n", noiseValue);
    String payload = "{\"seat_no\":" + String(SEAT_NO) + ",\"noise_value\":" + String(noiseValue) + "}";
    postJson("/noise", payload);
  }

  delay(100);
}
