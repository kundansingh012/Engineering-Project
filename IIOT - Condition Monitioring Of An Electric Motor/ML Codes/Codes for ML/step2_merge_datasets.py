"""
Step 2: Merging the three cleaned datasets (Healthy / Misalignment / SoftFoot)
- Read all three xlsx files
- Verify column consistency
- Concatenate into one dataframe
- Shuffle the rows
- Quality checks (shape, class balance, NaN)
- Save as motor_dataset.csv
"""

import pandas as pd
import numpy as np

# ===========================================================
# CHANGE THESE PATHS TO MATCH WHERE YOUR FILES ARE
# ===========================================================
HEALTHY_PATH      = "Healthy_clean.xlsx"
MISALIGNMENT_PATH = "Misalignment_clean.xlsx"
SOFTFOOT_PATH     = "SoftFoot_clean.xlsx"

OUTPUT_CSV  = "motor_dataset.csv"
OUTPUT_XLSX = "motor_dataset.xlsx"   # optional: same data as xlsx

# Random seed for reproducibility (so shuffling is the same every time)
RANDOM_SEED = 42

# ===========================================================
# 1. Read the three files
# ===========================================================
print("=" * 60)
print("READING FILES")
print("=" * 60)

df_h = pd.read_excel(HEALTHY_PATH)
df_m = pd.read_excel(MISALIGNMENT_PATH)
df_s = pd.read_excel(SOFTFOOT_PATH)

print(f"Healthy      : {df_h.shape}  | label values: {df_h['label'].unique()}")
print(f"Misalignment : {df_m.shape}  | label values: {df_m['label'].unique()}")
print(f"SoftFoot     : {df_s.shape}  | label values: {df_s['label'].unique()}")

# ===========================================================
# 2. Verify column consistency
# ===========================================================
print("\n" + "=" * 60)
print("CHECKING COLUMN CONSISTENCY")
print("=" * 60)

cols_h = list(df_h.columns)
cols_m = list(df_m.columns)
cols_s = list(df_s.columns)

if cols_h == cols_m == cols_s:
    print("All three files have identical columns.")
    print(f"Columns: {cols_h}")
else:
    print("WARNING: Column mismatch detected!")
    print(f"Healthy      columns: {cols_h}")
    print(f"Misalignment columns: {cols_m}")
    print(f"SoftFoot     columns: {cols_s}")
    raise ValueError("Columns do not match. Fix the source files before merging.")

# ===========================================================
# 3. Concatenate
# ===========================================================
df = pd.concat([df_h, df_m, df_s], axis=0, ignore_index=True)
print(f"\nCombined shape (before shuffle): {df.shape}")

# ===========================================================
# 4. Shuffle the rows
# ===========================================================
df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
print(f"Combined shape (after shuffle):  {df.shape}")

# ===========================================================
# 5. Quality checks
# ===========================================================
print("\n" + "=" * 60)
print("FINAL DATASET CHECKS")
print("=" * 60)

print("\n--- Class balance (counts per label) ---")
print(df["label"].value_counts())

print("\n--- Class balance (percentages) ---")
print((df["label"].value_counts(normalize=True) * 100).round(2))

print("\n--- Missing values per column ---")
print(df.isna().sum())

print("\n--- Data types ---")
print(df.dtypes)

print("\n--- First 10 rows after shuffle ---")
print(df.head(10))

print("\n--- Descriptive statistics ---")
print(df.describe().T.round(4))

# ===========================================================
# 6. Save the final dataset
# ===========================================================
df.to_csv(OUTPUT_CSV, index=False)
df.to_excel(OUTPUT_XLSX, index=False)
print(f"\nSaved final dataset to:")
print(f"  - {OUTPUT_CSV}")
print(f"  - {OUTPUT_XLSX}")
