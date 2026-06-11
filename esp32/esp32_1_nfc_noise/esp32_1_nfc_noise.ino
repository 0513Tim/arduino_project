#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* WIFI_SSID = "your_wifi_ssid";
const char* WIFI_PASSWORD = "your_wifi_password";
const char* API_BASE_URL = "your_api_base_url";

constexpr uint8_t RST_PIN = 32;
constexpr uint8_t SS_PIN = 27;
constexpr uint8_t SCK_PIN = 26;
constexpr uint8_t MOSI_PIN = 25;
constexpr uint8_t MISO_PIN = 33;
constexpr int GREEN_LED_PIN = 2;
constexpr int RED_LED_PIN = 4;
constexpr int SOUND_PIN = 34;
constexpr int SEAT_NO = 1;
constexpr int WARNING_THRESHOLD = 150;

MFRC522 mfrc522(SS_PIN, RST_PIN);

String lastUid = "";
unsigned long lastCardReadAt = 0;
unsigned long lastNoisePost = 0;
unsigned long lastSeatSyncAt = 0;
unsigned long lastBlinkToggle = 0;
const unsigned long cardCooldownMs = 3000;
const unsigned long noiseIntervalMs = 3000;
const unsigned long seatSyncIntervalMs = 3000;
bool seatOccupied = false;
bool isWarning = false;
bool redLedOn = false;

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

void updateSeatLed() {
  if (isWarning) {
    digitalWrite(GREEN_LED_PIN, LOW);
    if (millis() - lastBlinkToggle >= 300) {
      lastBlinkToggle = millis();
      redLedOn = !redLedOn;
      digitalWrite(RED_LED_PIN, redLedOn ? HIGH : LOW);
    }
    return;
  }

  redLedOn = false;
  digitalWrite(RED_LED_PIN, seatOccupied ? HIGH : LOW);
  digitalWrite(GREEN_LED_PIN, seatOccupied ? LOW : HIGH);
}

int postJson(const String& path, const String& jsonBody, String* responseBody = nullptr) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected, reconnecting...");
    connectWiFi();
  }

  HTTPClient http;
  http.begin(String(API_BASE_URL) + path);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(jsonBody);
  String response = httpCode > 0 ? http.getString() : "";

  Serial.printf("POST %s => %d\n", path.c_str(), httpCode);
  if (httpCode > 0) {
    Serial.println(response);
  } else {
    Serial.printf("HTTP error: %s\n", http.errorToString(httpCode).c_str());
  }
  if (responseBody != nullptr) {
    *responseBody = response;
  }
  http.end();
  return httpCode;
}

void syncSeatStatus() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/seats");
  int httpCode = http.GET();
  if (httpCode > 0) {
    String response = http.getString();
    String seatKey = "\"seat_id\":\"" + String(SEAT_NO < 10 ? "0" : "") + String(SEAT_NO) + "\"";
    int seatIndex = response.indexOf(seatKey);
    if (seatIndex >= 0) {
      int statusIndex = response.indexOf("\"status\":\"", seatIndex);
      if (statusIndex >= 0) {
        statusIndex += 10;
        int statusEnd = response.indexOf("\"", statusIndex);
        String status = response.substring(statusIndex, statusEnd);
        seatOccupied = status != "empty";
      }
    }
  }
  http.end();
  updateSeatLed();
}

void setup() {
  Serial.begin(115200);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  mfrc522.PCD_Init();
  pinMode(SOUND_PIN, INPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  connectWiFi();
  updateSeatLed();
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = readUid();
    unsigned long now = millis();
    if (uid != lastUid || now - lastCardReadAt > cardCooldownMs) {
      lastUid = uid;
      lastCardReadAt = now;
      Serial.printf("NFC UID: %s\n", uid.c_str());
      String payload = "{\"nfc_uid\":\"" + uid + "\",\"seat_no\":" + String(SEAT_NO) + "}";
      int httpCode = postJson("/checkin", payload);
      if (httpCode == 200) {
        seatOccupied = true;
        updateSeatLed();
      }
    }
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }

  if (millis() - lastNoisePost >= noiseIntervalMs) {
    lastNoisePost = millis();
    int noiseValue = analogRead(SOUND_PIN);
    Serial.printf("Noise value: %d\n", noiseValue);
    String payload = "{\"seat_no\":" + String(SEAT_NO) + ",\"noise_value\":" + String(noiseValue) + "}";
    String responseBody;
    int httpCode = postJson("/noise", payload, &responseBody);
    if (httpCode == 200) {
      isWarning = responseBody.indexOf("\"warning\":true") >= 0 || noiseValue >= WARNING_THRESHOLD;
      updateSeatLed();
    }
  }

  if (millis() - lastSeatSyncAt >= seatSyncIntervalMs) {
    lastSeatSyncAt = millis();
    syncSeatStatus();
  }

  updateSeatLed();
  delay(100);
}
