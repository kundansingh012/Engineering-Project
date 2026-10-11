void countMagnet() {
  unsigned long now = millis();

  // reject fast false triggers
  if (now - lastPulseTime > 500) {
    pulseCount++;
    lastPulseTime = now;
  }
}

void readRPM() {
  noInterrupts();
  unsigned int pulses = pulseCount;
  pulseCount = 0;
  interrupts();

  // start with 1 pulse per revolution
  RPM = (pulses * 60000UL) / rpmWindow;
}