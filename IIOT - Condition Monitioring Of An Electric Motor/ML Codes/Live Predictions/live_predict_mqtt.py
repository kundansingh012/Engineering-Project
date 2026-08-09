"""
Live motor-fault prediction via MQTT.

The Arduino publishes 6 vibration features every 20 seconds, one per topic:
    motor/vibration/rmsX
    motor/vibration/rmsY
    motor/vibration/rmsZ
    motor/vibration/crestX
    motor/vibration/crestY
    motor/vibration/crestZ

This script:
  1. Subscribes to all 6 topics on the configured MQTT broker
  2. Waits until it has a fresh value for each of the 6
  3. Standardizes them with the SAVED scaler (the same one trained on train data)
  4. Predicts the class with the saved SVM model
  5. Prints the prediction with timestamps and confidence scores
  6. Logs every prediction to a CSV file

REQUIREMENTS:
    pip install paho-mqtt scikit-learn pandas numpy joblib

EXPECTED FILES (next to this script):
    models_v2/SVM_rbf.joblib
    scaler_v2.joblib
    label_encoder_v2.joblib
"""

import os
import csv
import time
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import paho.mqtt.client as mqtt

# ============================================================
# CONFIGURATION  ←  EDIT THESE FOR YOUR NETWORK
# ============================================================
BROKER_IP   = "10.126.166.46"   # <-- put the new broker IP here
BROKER_PORT = 1883
MQTT_USER   = None              # set if your broker needs auth
MQTT_PASS   = None

MODEL_PATH   = "SVM_rbf.joblib"
SCALER_PATH  = "scaler_v2.joblib"
ENCODER_PATH = "label_encoder_v2.joblib"

LOG_CSV = "live_predictions.csv"

# The Arduino publishes 9 topics. We subscribe to all of them, but
# only the 6 vibration topics are fed into the SVM.

# These ARE used by the model:
VIBRATION_TOPIC_TO_FEATURE = {
    "motor/vibration/rmsX":   "rms_x",
    "motor/vibration/rmsY":   "rms_y",
    "motor/vibration/rmsZ":   "rms_z",
    "motor/vibration/crestX": "crest_x",
    "motor/vibration/crestY": "crest_y",
    "motor/vibration/crestZ": "crest_z",
}
FEATURE_ORDER = ["rms_x", "rms_y", "rms_z", "crest_x", "crest_y", "crest_z"]

# These are NOT used by the model, but we display + log them for context:
CONTEXT_TOPIC_TO_NAME = {
    "motor/temperature": "temperature",
    "motor/rpm":         "rpm",
    "motor/current":     "current",
}

ALL_TOPICS = list(VIBRATION_TOPIC_TO_FEATURE.keys()) + list(CONTEXT_TOPIC_TO_NAME.keys())

# Color codes for the terminal (just makes output easier to read)
GREEN  = "\033[92m"
RED    = "\033[91m"
BLUE   = "\033[94m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ============================================================
# Load model + preprocessing artifacts
# ============================================================
print(f"{BOLD}Loading trained model and preprocessing artifacts ...{RESET}")
model   = joblib.load(MODEL_PATH)
scaler  = joblib.load(SCALER_PATH)
encoder = joblib.load(ENCODER_PATH)
class_names = list(encoder.classes_)
print(f"  Model    : {MODEL_PATH}   ({type(model).__name__})")
print(f"  Scaler   : {SCALER_PATH}")
print(f"  Encoder  : {ENCODER_PATH}")
print(f"  Classes  : {class_names}")
print()

# ============================================================
# Buffers for the latest readings
# ============================================================
# `current_sample` holds the 6 vibration features (used by the model).
# `current_context` holds temperature / rpm / current (display + log only).
current_sample  = {}
current_context = {}

# Prepare the log file (write header if it doesn't exist yet)
LOG_HEADER = (["timestamp"]
              + FEATURE_ORDER
              + list(CONTEXT_TOPIC_TO_NAME.values())
              + ["prediction"]
              + [f"score_{c}" for c in class_names])
if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(LOG_HEADER)

# ============================================================
# Prediction function
# ============================================================
def predict_and_print():
    """Run prediction on the currently buffered sample, then clear the buffer."""
    # Build feature vector in the correct order
    x = np.array([[current_sample[f] for f in FEATURE_ORDER]])

    # Apply the same scaler used during training
    x_scaled = scaler.transform(x)

    # Predict
    y_idx = model.predict(x_scaled)[0]
    y_name = encoder.inverse_transform([y_idx])[0]

    # Confidence scores (SVC decision_function gives margin to each class)
    if hasattr(model, "decision_function"):
        scores = model.decision_function(x_scaled)[0]
        score_dict = dict(zip(class_names, scores))
    else:
        score_dict = {c: float("nan") for c in class_names}

    # Pretty print
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = GREEN if y_name == "Healthy" else RED

    print(f"\n{BLUE}─── New reading @ {ts} ───{RESET}")

    # Context block — temperature / RPM / current (not used by the model)
    print(f"  {YELLOW}Context (not used by model):{RESET}")
    temp_v = current_context.get("temperature")
    rpm_v  = current_context.get("rpm")
    cur_v  = current_context.get("current")
    print(f"    Temperature : {temp_v if temp_v is not None else '—'} °C")
    print(f"    RPM         : {rpm_v  if rpm_v  is not None else '—'}")
    print(f"    Current     : {cur_v  if cur_v  is not None else '—'} mA")

    # Vibration features — used by the SVM
    print(f"  {BOLD}Vibration features (used by SVM):{RESET}")
    pairs = [("rms_x", "crest_x"), ("rms_y", "crest_y"), ("rms_z", "crest_z")]
    for a, b in pairs:
        print(f"    {a:8s} = {current_sample[a]:.6f}    "
              f"{b:8s} = {current_sample[b]:.6f}")

    # Prediction
    print(f"  {BOLD}Prediction: {color}{y_name}{RESET}")
    print(f"  Decision scores:")
    for c, s in sorted(score_dict.items(), key=lambda kv: -kv[1]):
        marker = " ←" if c == y_name else ""
        print(f"    {c:14s} {s:+8.3f}{marker}")

    # Log to CSV — write all 9 features + prediction + scores
    with open(LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow([ts]
                   + [current_sample[f] for f in FEATURE_ORDER]
                   + [current_context.get(k) for k in CONTEXT_TOPIC_TO_NAME.values()]
                   + [y_name]
                   + [score_dict[c] for c in class_names])

    # Reset both buffers for the next 20-second window
    current_sample.clear()
    current_context.clear()

# ============================================================
# MQTT callbacks
# ============================================================
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"{GREEN}Connected to MQTT broker {BROKER_IP}:{BROKER_PORT}{RESET}")
        for topic in ALL_TOPICS:
            client.subscribe(topic)
            print(f"  Subscribed: {topic}")
        print(f"\n{YELLOW}Waiting for the next 20-second report from the Arduino ...{RESET}")
    else:
        print(f"{RED}MQTT connect failed (rc = {rc}){RESET}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()

    try:
        value = float(payload)
    except ValueError:
        print(f"{RED}Bad payload on {topic}: {payload!r}{RESET}")
        return

    # Route to the correct buffer:
    #   - vibration topics -> current_sample (used by the model)
    #   - rpm / temp / current -> current_context (display + log only)
    if topic in VIBRATION_TOPIC_TO_FEATURE:
        feature_name = VIBRATION_TOPIC_TO_FEATURE[topic]
        current_sample[feature_name] = value
    elif topic in CONTEXT_TOPIC_TO_NAME:
        context_name = CONTEXT_TOPIC_TO_NAME[topic]
        current_context[context_name] = value
    else:
        return  # unknown topic - ignore

    # Once we have all 6 vibration features, run the SVM
    if len(current_sample) == 6:
        predict_and_print()


def on_disconnect(client, userdata, rc, properties=None, reason_code=None):
    print(f"{YELLOW}Disconnected from MQTT broker. Reconnecting ...{RESET}")


# ============================================================
# Main
# ============================================================
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    print(f"Connecting to {BROKER_IP}:{BROKER_PORT} ...")
    client.connect(BROKER_IP, BROKER_PORT, keepalive=60)

    # Blocks here forever — listens and reacts to messages
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopped by user. Predictions logged to {LOG_CSV}{RESET}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
