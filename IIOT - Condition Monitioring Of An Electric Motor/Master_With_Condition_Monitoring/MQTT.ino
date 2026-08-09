WiFiClient mqttWiFiClient;
MqttClient mqttClient(mqttWiFiClient);

//const char broker[] = "192.168.0.89"; // Replace with your computer's IP
const char broker[] = "10.126.166.46";

int port = 1883;

void connectToBroker() {
  Serial.print("Attempting to connect to MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    return;
  }
  Serial.println("Connected to the MQTT broker!");
}

void sendDataMQTT() {
  // 1. Maintain connection with the broker
  //mqttClient.poll();

  // 2. Publish Standard Sensors
  mqttClient.beginMessage("motor/rpm");
  mqttClient.print(RPM);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/temperature");
  mqttClient.print(bearingTemp);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/current");
  mqttClient.print(currentmA);
  mqttClient.endMessage();

  // 3. Publish RMS (Vibration Energy)
  mqttClient.beginMessage("motor/vibration/rmsX");
  mqttClient.print(rmsX, 4);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/vibration/rmsY");
  mqttClient.print(rmsY, 4);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/vibration/rmsZ");
  mqttClient.print(rmsZ, 4);
  mqttClient.endMessage();

  // 4. Publish Crest Factor (Impact Severity)
  mqttClient.beginMessage("motor/vibration/crestX");
  mqttClient.print(crestX, 4);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/vibration/crestY");
  mqttClient.print(crestY, 4);
  mqttClient.endMessage();

  mqttClient.beginMessage("motor/vibration/crestZ");
  mqttClient.print(crestZ, 4);
  mqttClient.endMessage();

  // Data publish confirmation
  Serial.println("MQTT analysis data published.");
}
