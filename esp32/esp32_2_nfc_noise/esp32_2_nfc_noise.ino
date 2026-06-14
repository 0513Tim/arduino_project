#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

const char* WIFI_SSID = "your_ssid";
const char* WIFI_PASSWORD = "your_password";
const char* API_BASE_URL = "http://xxx.xxx.xxx.xxx:8000";

constexpr uint8_t RST_PIN = 32;
constexpr uint8_t SS_PIN = 27;
constexpr uint8_t SCK_PIN = 26;
constexpr uint8_t MOSI_PIN = 25;
constexpr uint8_t MISO_PIN = 33;
constexpr int LED_PIN = 18;
constexpr int SEAT_NO = 2;

MFRC522 mfrc522(SS_PIN, RST_PIN);

String lastUid = "";
unsigned long lastCardReadAt = 0;
const unsigned long cardCooldownMs = 1000;

void blinkLed(int times, int intervalMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(intervalMs);
    digitalWrite(LED_PIN, LOW);
    delay(intervalMs);
  }
}

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
  Serial.println("Card UID: " + uid);
  return uid;
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

void setup() {
  Serial.begin(115200);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  mfrc522.PCD_Init();
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  connectWiFi();
  Serial.println("ESP32-2 register kiosk ready");
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = readUid();
    unsigned long now = millis();
    if (uid == lastUid && now - lastCardReadAt < cardCooldownMs) {
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();
      mfrc522.PCD_Init();
      mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
      delay(100);
      return;
    }

    lastUid = uid;
    lastCardReadAt = now;
    Serial.printf("Register UID: %s\n", uid.c_str());

    String scanPayload = "{\"nfc_uid\":\"" + uid + "\",\"seat_no\":" + String(SEAT_NO) + ",\"source\":\"esp32-2-register\"}";
    String responseBody;
    int httpCode = postJson("/scan_uid", scanPayload, &responseBody);
    if (httpCode == 200) {
      if (responseBody.indexOf("\"registered\":true") >= 0) {
        Serial.println("UID already registered");
        blinkLed(3, 100);
      } else {
        Serial.println("UID not registered yet");
        blinkLed(1, 250);
      }
    }

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    mfrc522.PCD_Init();
    mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
    delay(150);
  }

  delay(20);
}
