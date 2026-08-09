void readTemp() {
  bearingTemp = sht1x.readTemperatureC();
}

void highTemp (){
  // Local Threshold Alert (Safety Check)
if (bearingTemp > 45.0) {  // If temp is above 45C
  digitalWrite(LED_BUILTIN, HIGH); // Turn on onboard LED
  Serial.println("ALERT: High Temperature detected locally!");
} else {
  digitalWrite(LED_BUILTIN, LOW);
}
}