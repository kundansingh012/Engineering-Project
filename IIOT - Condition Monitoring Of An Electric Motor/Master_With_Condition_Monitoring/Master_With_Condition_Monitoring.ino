#include <SHT1x.h>

#include <Arduino_LSM6DS3.h>  // for on board IMU sensor
#include <ThingSpeak.h>       // uploads data to cloud
#include <ArduinoMqttClient.h>

//for wifi
//#include "arduino_wifi.h"
#include <WiFiNINA.h>
#include "arduino_secrets.h"  // keep credentials out of source control - see arduino_secrets.h.example

char ssid[] = SECRET_SSID;  //WiFi SSID “eduroam/Macquarie OneNet”

// Enterprise credentials
char username[] = SECRET_USERNAME;  // student ID
char password[] = SECRET_PASSWORD;  // Password
char identity[] = SECRET_IDENTITY;  // "anonymous" for eduroam and student ID for MQOneNET

int status = WL_IDLE_STATUS;
WiFiClient client;


WiFiClient thingSpeakClient;
extern MqttClient mqttClient;

unsigned long channelID = SECRET_CH_ID;          //YOUR_CHANNEL_ID
const char* writeAPIKey = SECRET_WRITE_APIKEY;   //YOUR_WRITE_API_KEY

//Master
unsigned long lastReportTime = 0;

//Current
float shuntResistor = 898.0;
float currentmA = 0;

//Vibration
float sumSqX = 0, sumSqY = 0, sumSqZ = 0;
float peakX = 0, peakY = 0, peakZ = 0;
long sampleCount = 0;

float rmsX, rmsY, rmsZ;
float crestX, crestY, crestZ;

//Temperature
#include <SHT1x.h>
#define dataPin 4
#define clockPin 5
SHT1x sht1x(dataPin, clockPin);
float bearingTemp = 0;

// RPM
#define HALL_PIN 2
volatile unsigned int pulseCount = 0;
volatile unsigned long lastPulseTime = 0;

int RPM = 0;
unsigned long lastRPMCalcTime = 0;
const unsigned long rpmWindow = 3000;


void setup() {
  pinMode(HALL_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), countMagnet, FALLING);

  Serial.begin(115200);
  //wifi connection at uni
  while (!Serial)
    ;

  Serial.println("Starting WPA2-Enterprise Internet Test...");

  // Connect using Enterprise
  while (status != WL_CONNECTED) {
    Serial.println("Connecting to Enterprise WiFi...");
    status = WiFi.beginEnterprise(ssid, username, password, identity);
    delay(5000);
  }

  Serial.println("WiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  //connectWiFi();  //calling network.ino
  ThingSpeak.begin(thingSpeakClient);

  //start the IMU
  if (!IMU.begin()) {
    Wire.setClock(400000);
    Serial.println("Failed to initialize IMU!");
    while (1)
      ;  // Halt if sensor fails
  }
  //IMU.begin() was successful!
  Wire.setClock(400000);  // Speed up I2C to 400kHz for faster sampling
  Serial.println("IMU initialized and I2C clock boosted.");

  connectToBroker();
  Serial.println("Testing IMU...");
  float tx, ty, tz;
  IMU.readAcceleration(tx, ty, ty);
  Serial.print("Initial Read: ");
  Serial.println(tx);
}

void loop() {
  readVibration();

  //wifi/MQTT check before sending to ThingSpeak/Node-red
  //if (WiFi.status() != WL_CONNECTED) {
  // Serial.println("WiFi disconnected. Reconnecting...");
  // connectWiFi();
  // connectToBroker();  //bcz if wifi fails mqtt fails and this ensures mqtt reconnects right after wifi
  //}
  //if (!mqttClient.connected()) {
  //   Serial.println("MQTT disconnected. Reconnecting...");
  //   connectToBroker();
  // }
  mqttClient.poll();  //keep connection stable with each loop

  if (millis() - lastRPMCalcTime >= rpmWindow) {
    readRPM();
    lastRPMCalcTime = millis();
  } 

  //20 sec block
  if (millis() - lastReportTime > 20000) {
    calculateVibrationStats();  // Finalize RMS/Crest for the last 20 seconds

    readCurrent();
    //    readRPM();
    readTemp();
    highTemp();

    sendDataToThingSpeak();
    sendDataMQTT();
    printFullReport();  // to print all sensor values

    resetStats();  // RESET accumulators

    lastReportTime = millis();
  }
}