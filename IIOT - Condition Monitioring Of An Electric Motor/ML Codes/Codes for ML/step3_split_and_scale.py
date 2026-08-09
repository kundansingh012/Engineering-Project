"""
Step 3 (new): Train/Test Split + Standardization
- Input : motor_dataset_v2.csv
- Use ONLY the 6 vibration features for modeling
- Stratified 80/20 split
- StandardScaler fit on train only, transform both
- Save split + scaler + label encoder for step 4
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ===========================================================
# CONFIGURATION
# ===========================================================
INPUT_PATH    = "motor_dataset_v2.csv"
TRAIN_PATH    = "train_scaled_v2.csv"
TEST_PATH     = "test_scaled_v2.csv"
SCALER_PATH   = "scaler_v2.joblib"
ENCODER_PATH  = "label_encoder_v2.joblib"

TEST_SIZE     = 0.20
RANDOM_SEED   = 42

# Only the 6 vibration features are used for modeling
FEATURES = ["rms_x", "rms_y", "rms_z",
            "crest_x", "crest_y", "crest_z"]

# ===========================================================
# 1. Load
# ===========================================================
df = pd.read_csv(INPUT_PATH)
print(f"Loaded {INPUT_PATH}: {df.shape}")
print(f"\nClass distribution:")
print(df["label"].value_counts())

X = df[FEATURES].values
y_raw = df["label"].values

# ===========================================================
# 2. Encode labels
# ===========================================================
le = LabelEncoder()
y = le.fit_transform(y_raw)

print("\nLabel encoding:")
for cls, code in zip(le.classes_, le.transform(le.classes_)):
    print(f"  {cls} -> {code}")

# ===========================================================
# 3. Stratified 80/20 split
# ===========================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_SEED,
)

print(f"\nSplit shapes:")
print(f"  X_train: {X_train.shape}    y_train: {y_train.shape}")
print(f"  X_test : {X_test.shape}     y_test : {y_test.shape}")

# ===========================================================
# 4. Verify stratification
# ===========================================================
def show_class_balance(name, y_arr, encoder):
    s = pd.Series(encoder.inverse_transform(y_arr)).value_counts(normalize=True) * 100
    print(f"\n{name} class balance (%):")
    print(s.round(2).to_string())

show_class_balance("Train", y_train, le)
show_class_balance("Test ", y_test, le)

# ===========================================================
# 5. Standardize - fit ONLY on train
# ===========================================================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print("\nScaler statistics (learned from training data):")
stats = pd.DataFrame({
    "mean":  scaler.mean_,
    "std":   scaler.scale_,
}, index=FEATURES).round(6)
print(stats)

print("\nSanity check on X_train_scaled (should be ~0 mean, ~1 std):")
sanity = pd.DataFrame({
    "mean": X_train_scaled.mean(axis=0),
    "std":  X_train_scaled.std(axis=0),
}, index=FEATURES).round(4)
print(sanity)

# ===========================================================
# 6. Save
# ===========================================================
train_df = pd.DataFrame(X_train_scaled, columns=FEATURES)
train_df["label"] = y_train
train_df.to_csv(TRAIN_PATH, index=False)

test_df = pd.DataFrame(X_test_scaled, columns=FEATURES)
test_df["label"] = y_test
test_df.to_csv(TEST_PATH, index=False)

joblib.dump(scaler, SCALER_PATH)
joblib.dump(le, ENCODER_PATH)

print(f"\nSaved:")
print(f"  {TRAIN_PATH}")
print(f"  {TEST_PATH}")
print(f"  {SCALER_PATH}")
print(f"  {ENCODER_PATH}")
print("\nReady for step 4 (model training).")
