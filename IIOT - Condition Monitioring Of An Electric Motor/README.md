# IIoT Condition Monitoring of an Electric Motor

An Industrial IoT system that continuously monitors an electric motor's health using vibration, current, temperature, and RPM sensing, and classifies operating conditions (normal, loose screw, misalignment) with a machine learning model. Built as part of ENGG8201 (IoT) at Macquarie University; findings were also written up as a paper submitted to ICST 2026.

## Overview

An Arduino-based sensor node (Nano 33 IoT) samples the motor's vibration (onboard IMU), shunt current, bearing temperature (SHT1x), and RPM (Hall sensor) in real time. Data is streamed to the cloud via MQTT and logged to ThingSpeak, and offline datasets are used to train classical ML classifiers that distinguish healthy operation from fault conditions such as a loose mounting screw or shaft misalignment. A live prediction GUI applies the trained model to incoming MQTT data for real-time fault detection.

## Repository Structure

- `Master_With_Condition_Monitoring/` — Arduino firmware (.ino files) for the sensor node
  - `Master_With_Condition_Monitoring.ino` — main sketch: WiFi/MQTT setup, sensor orchestration, reporting loop
  - `Vibration.ino` — IMU sampling, RMS and crest factor calculation
  - `Current.ino` — shunt-based current sensing
  - `Temperature.ino` — bearing temperature via SHT1x
  - `RPM.ino` — Hall-effect RPM measurement
  - `MQTT.ino` — MQTT broker connection and topic publishing
  - `ThingSpeak.ino` — ThingSpeak cloud logging
  - `FullReport.ino` — serial diagnostic reporting
  - `arduino_secrets.h.example` — template for WiFi/ThingSpeak credentials (copy to `arduino_secrets.h`, which is gitignored)
- `Data for ML/` — Raw and labelled sensor datasets (CSV) and reference plots (RMS, crest factor) for normal, loose-screw, and misalignment conditions
- `ML Codes/`
  - `Codes for ML/` — data cleaning, merging, EDA, train/test split, and model training/evaluation scripts (`step1`–`step4`)
  - `Live Predictions/` — trained model artifacts (Logistic Regression, SVM) and scripts for real-time MQTT-based fault prediction, including a live prediction GUI
- `Group_8_IOT_ENGG8201_Project_Submission.pdf` — course project report
- `Paper-ICST2026-motor-monitoring.pdf` — associated research paper

## Hardware

- Arduino Nano 33 IoT (onboard IMU for vibration sensing)
- SHT1x temperature/humidity sensor
- Hall-effect sensor for RPM
- Shunt resistor for current sensing
- WiFi (WPA2-Enterprise) for connectivity

## Software / Pipeline

1. **Firmware** samples vibration, current, temperature, and RPM every cycle, computes RMS and crest factor over a rolling window, and reports summarized values every 20 seconds.
2. **Data transport**: sensor data is published over MQTT and simultaneously logged to ThingSpeak for cloud visualization.
3. **ML pipeline**: collected CSV datasets are cleaned, merged, and explored (EDA), then split/scaled for training. Logistic Regression and SVM classifiers are trained to distinguish normal operation from fault conditions.
4. **Live prediction**: a GUI subscribes to the MQTT stream and applies the trained model in real time to flag anomalous motor conditions.

## Setup

1. Copy `Master_With_Condition_Monitoring/arduino_secrets.h.example` to `arduino_secrets.h` in the same folder and fill in your WiFi credentials, MQTT broker details, and ThingSpeak channel ID / write API key. This file is gitignored and will not be committed.
2. Flash `Master_With_Condition_Monitoring.ino` to the Arduino Nano 33 IoT (requires the `ArduinoMqttClient`, `ThingSpeak`, `Arduino_LSM6DS3`, `SHT1x`, and `WiFiNINA` libraries).
3. Run the ML training scripts in `ML Codes/Codes for ML/` in order (`step1` → `step4`) to reproduce the trained models from the datasets in `Data for ML/`.
4. Run `ML Codes/Live Predictions/live_predict_mqtt.py` or `live_predict_gui.py` to apply the trained model to live sensor data over MQTT.

## Technologies

Arduino (Nano 33 IoT) • MQTT • ThingSpeak • Python • Scikit-learn (Logistic Regression, SVM) • Pandas
