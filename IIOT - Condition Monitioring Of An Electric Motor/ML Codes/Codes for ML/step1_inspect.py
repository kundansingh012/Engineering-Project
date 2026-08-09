"""
Step 1 (new): Initial inspection of motor_dataset_v2.csv
Quick sanity checks before doing any analysis or modeling:
  - shape, dtypes, missing values, duplicates
  - class balance
  - descriptive statistics
  - first / last rows
"""

import pandas as pd

# ===========================================================
# CONFIGURATION
# ===========================================================
INPUT_PATH = "motor_dataset_v2.csv"

FEATURES = ["temperature", "rpm", "current",
            "rms_x", "rms_y", "rms_z",
            "crest_x", "crest_y", "crest_z"]

# ===========================================================
# 1. Load
# ===========================================================
df = pd.read_csv(INPUT_PATH)
print("=" * 60)
print("BASIC STRUCTURE")
print("=" * 60)
print(f"Shape: {df.shape}   (rows, columns)")
print(f"Columns: {list(df.columns)}")

# ===========================================================
# 2. Data types
# ===========================================================
print("\n--- Data types ---")
print(df.dtypes)

# ===========================================================
# 3. Missing values
# ===========================================================
print("\n--- Missing values per column ---")
print(df.isna().sum())

# ===========================================================
# 4. Duplicate rows (based on the feature values, not the label)
# ===========================================================
n_dup = df[FEATURES].duplicated().sum()
print(f"\n--- Duplicate rows (feature values only): {n_dup} ---")

# ===========================================================
# 5. Class balance
# ===========================================================
print("\n--- Class balance ---")
print(df["label"].value_counts())
print("\n--- Class balance (percentages) ---")
print((df["label"].value_counts(normalize=True) * 100).round(2))

# ===========================================================
# 6. Descriptive statistics
# ===========================================================
print("\n" + "=" * 60)
print("DESCRIPTIVE STATISTICS")
print("=" * 60)
print(df[FEATURES].describe().T.round(4))

# ===========================================================
# 7. First and last rows
# ===========================================================
print("\n--- First 5 rows ---")
print(df.head().round(4))
print("\n--- Last 5 rows ---")
print(df.tail().round(4))

# ===========================================================
# 8. Per-class mean of each feature (quick preview)
# ===========================================================
print("\n" + "=" * 60)
print("PER-CLASS MEAN OF EACH FEATURE")
print("=" * 60)
print(df.groupby("label")[FEATURES].mean().round(4).T)

print("\nInspection complete. Ready for EDA.")
