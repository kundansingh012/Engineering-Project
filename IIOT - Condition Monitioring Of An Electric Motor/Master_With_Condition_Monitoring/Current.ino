void readCurrent() {
  float voltage = (analogRead(A3) / 1023.0) * 3.3;
  currentmA = ((voltage / shuntResistor) * 1000);
}
    