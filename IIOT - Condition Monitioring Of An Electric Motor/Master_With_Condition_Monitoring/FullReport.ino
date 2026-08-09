void printFullReport() {
  Serial.println("\n--- 20 Second Analysis Report ---");
  
  Serial.print("Current: "); Serial.print(currentmA); Serial.print(" mA");
  Serial.print(" | RPM: "); Serial.println(RPM);
  Serial.print("Bearing Temp: "); Serial.print(bearingTemp); Serial.println(" C");

  // X-Axis Stats
  Serial.print("X-Axis -> RMS: "); Serial.print(rmsX, 4);
  Serial.print(" | Crest: "); Serial.println(crestX, 4);

  // Y-Axis Stats
  Serial.print("Y-Axis -> RMS: "); Serial.print(rmsY, 4);
  Serial.print(" | Crest: "); Serial.println(crestY, 4);

  // Z-Axis Stats
  Serial.print("Z-Axis -> RMS: "); Serial.print(rmsZ, 4);
  Serial.print(" | Crest: "); Serial.println(crestZ, 4);

  Serial.print("Samples Collected: "); Serial.println(sampleCount);
  Serial.println("---------------------------------");
}
