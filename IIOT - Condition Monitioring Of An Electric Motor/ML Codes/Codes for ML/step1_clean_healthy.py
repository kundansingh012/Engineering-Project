"""
Step 1: Cleaning the Healthy.xlsx data
- Read the file
- Drop empty rows
- Rename columns
- Add label column
- Quality checks
- Save as CSV
"""

import pandas as pd

# ---------- 1. Read the file ----------
INPUT_PATH = "/sessions/eloquent-epic-brahmagupta/mnt/uploads/Healthy.xlsx"
OUTPUT_PATH = "/sessions/eloquent-epic-brahmagupta/mnt/outputs/Healthy_clean.csv"

df = pd.read_excel(INPUT_PATH)
print("=" * 60)
print("BEFORE CLEANING")
print("=" * 60)
print(f"Original shape: {df.shape}")
print(f"Original columns: {list(df.columns)}")

# ---------- 2. Drop empty rows ----------
# Drop rows where ALL columns are NaN
df = df.dropna(how="all").reset_index(drop=True)

# ---------- 3. Rename columns ----------
rename_map = {
    "motor/temperature": "temperature",
    "motor/rpm": "rpm",
    "motor/current": "current",
    "motor/vibration/rmsX": "rms_x",
    "motor/vibration/rmsY": "rms_y",
    "motor/vibration/rmsZ": "rms_z",
    "motor/vibration/crestX": "crest_x",
    "motor/vibration/crestY": "crest_y",
    "motor/vibration/crestZ": "crest_z",
}
df = df.rename(columns=rename_map)

# ---------- 4. Add label column ----------
df["label"] = "Healthy"

# ---------- 5. Quality checks ----------
print("\n" + "=" * 60)
print("AFTER CLEANING")
print("=" * 60)
print(f"Shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")

print("\n--- Data types ---")
print(df.dtypes)

print("\n--- Missing values per column ---")
print(df.isna().sum())

print("\n--- Duplicate rows ---")
n_dup = df.duplicated().sum()
print(f"Number of fully duplicated rows: {n_dup}")

print("\n--- Descriptive statistics ---")
# Only numeric columns for describe
print(df.describe().T.round(4))

print("\n--- First 5 rows of cleaned data ---")
print(df.head())

print("\n--- Last 5 rows of cleaned data ---")
print(df.tail())

# ---------- 6. Save cleaned data ----------
df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved cleaned data to: {OUTPUT_PATH}")
