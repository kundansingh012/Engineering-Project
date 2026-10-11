    void sendDataToThingSpeak() {
  ThingSpeak.setField(1, bearingTemp);
  ThingSpeak.setField(2, RPM);
  ThingSpeak.setField(3, currentmA);

  // Vibration Energy (RMS)
  ThingSpeak.setField(4, rmsX);
  ThingSpeak.setField(5, rmsY);
  
  ThingSpeak.setField(6, rmsZ);

  // Impact Severity (Crest Factor)
  // Sending the average Crest Factor or just the most critical axis
  ThingSpeak.setField(7, crestX); 
  ThingSpeak.setField(8, sampleCount); // Good to track for "Data Integrity" in your report

  int status = ThingSpeak.writeFields(channelID, writeAPIKey);

  if (status == 200) {
    Serial.println("ThingSpeak Update Successful.");
  } else {
    Serial.print("ThingSpeak upload failed. HTTP error code: ");
    Serial.println(status);
  }
}