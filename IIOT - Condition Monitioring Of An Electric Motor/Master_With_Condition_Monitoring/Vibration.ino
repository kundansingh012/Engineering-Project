void readVibration() {
  //if (IMU.accelerationAvailable()) {
  float x, y, z;
  IMU.readAcceleration(x, y, z);

  // 1. Accumulate Sum of Squares for RMS: Σ(xi^2)
  sumSqX += (x * x);
  sumSqY += (y * y);
  sumSqZ += (z * z);

  // 2. Track Absolute Peak for Crest Factor: Max(|x|)
  if (abs(x) > peakX) peakX = abs(x);
  if (abs(y) > peakY) peakY = abs(y);
  if (abs(z) > peakZ) peakZ = abs(z);

  sampleCount++;
  //}
}
void calculateVibrationStats() {
  if (sampleCount > 0) {
    // RMS = sqrt( (1/N) * Σ(xi^2) )
    rmsX = sqrt(sumSqX / sampleCount);
    rmsY = sqrt(sumSqY / sampleCount);
    rmsZ = sqrt(sumSqZ / sampleCount);

    // Crest Factor = Max(x) / RMS
    crestX = (rmsX > 0) ? (peakX / rmsX) : 0;
    crestY = (rmsY > 0) ? (peakY / rmsY) : 0;
    crestZ = (rmsZ > 0) ? (peakZ / rmsZ) : 0;
  }
}

void resetStats() {
  // RESET accumulators for the next 20-second window
  sumSqX = 0;
  sumSqY = 0;
  sumSqZ = 0;
  peakX = 0;
  peakY = 0;
  peakZ = 0;
  sampleCount = 0;
}
