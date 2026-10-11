"""
Step 3: Exploratory Data Analysis (EDA)
- Fix label inconsistency
- Variance analysis
- Boxplots for each feature by class
- Correlation matrix heatmap
- Pairplot
- PCA 2D visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ===========================================================
# CONFIGURATION - change paths if needed
# ===========================================================
INPUT_PATH = "motor_dataset.csv"
PLOTS_DIR  = "plots"   # folder where plots will be saved

import os
os.makedirs(PLOTS_DIR, exist_ok=True)

# Colors for each class (consistent across all plots)
CLASS_ORDER  = ["Healthy", "Misalignment", "SoftFoot"]
CLASS_COLORS = {"Healthy": "#2ecc71", "Misalignment": "#e74c3c", "SoftFoot": "#3498db"}

# ===========================================================
# 1. Load data and fix label inconsistency
# ===========================================================
df = pd.read_csv(INPUT_PATH)
print("Loaded:", df.shape)

# Normalize labels
df["label"] = df["label"].replace({
    "misalignment": "Misalignment",
    "Misalignment": "Misalignment",
    "Healthy": "Healthy",
    "healthy": "Healthy",
    "SoftFoot": "SoftFoot",
    "softfoot": "SoftFoot",
    "Soft_foot": "SoftFoot",
    "soft foot": "SoftFoot",
})
print("\nLabel counts after normalization:")
print(df["label"].value_counts())

# Save the cleaned dataset back (so future steps use consistent labels)
df.to_csv(INPUT_PATH, index=False)

# Define feature columns
FEATURES = ["temperature", "rpm", "current",
            "rms_x", "rms_y", "rms_z",
            "crest_x", "crest_y", "crest_z"]

# ===========================================================
# 2. Variance analysis
# ===========================================================
print("\n" + "=" * 60)
print("VARIANCE ANALYSIS")
print("=" * 60)

variance_table = pd.DataFrame({
    "mean":   df[FEATURES].mean(),
    "std":    df[FEATURES].std(),
    "min":    df[FEATURES].min(),
    "max":    df[FEATURES].max(),
    "range":  df[FEATURES].max() - df[FEATURES].min(),
    # coefficient of variation = std / mean (a scale-free measure of spread)
    "cv (%)": (df[FEATURES].std() / df[FEATURES].mean() * 100),
}).round(4)
print(variance_table)
print("\nFeatures with very low variability (cv < 1%) are likely uninformative.")

# ===========================================================
# 3. Boxplots: each feature by class
# ===========================================================
print("\nGenerating boxplots ...")
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
for ax, feat in zip(axes.flatten(), FEATURES):
    sns.boxplot(
        data=df, x="label", y=feat,
        order=CLASS_ORDER, palette=CLASS_COLORS, ax=ax,
    )
    ax.set_title(feat, fontsize=12, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
plt.suptitle("Feature distributions by class", fontsize=15, fontweight="bold", y=1.00)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/01_boxplots.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  saved: {PLOTS_DIR}/01_boxplots.png")

# Same boxplots but with log scale on y-axis - useful for crest features with outliers
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, feat in zip(axes, ["crest_x", "crest_y", "crest_z"]):
    sns.boxplot(
        data=df, x="label", y=feat,
        order=CLASS_ORDER, palette=CLASS_COLORS, ax=ax,
    )
    ax.set_yscale("log")
    ax.set_title(f"{feat} (log scale)", fontsize=12, fontweight="bold")
    ax.set_xlabel("")
plt.suptitle("Crest factors with log scale (outliers visible)", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/02_crest_log.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  saved: {PLOTS_DIR}/02_crest_log.png")

# ===========================================================
# 4. Correlation matrix
# ===========================================================
print("\nGenerating correlation matrix ...")
corr = df[FEATURES].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, vmin=-1, vmax=1, square=True,
            cbar_kws={"shrink": 0.8})
plt.title("Correlation matrix between features", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/03_correlation.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  saved: {PLOTS_DIR}/03_correlation.png")

# Print the correlation matrix to console too
print("\nCorrelation matrix:")
print(corr.round(2))

# ===========================================================
# 5. Pairplot - uses only the most likely-useful features to keep it readable
# ===========================================================
print("\nGenerating pairplot (this may take ~30 seconds) ...")
key_feats = ["rms_x", "rms_y", "crest_x", "crest_y", "crest_z"]
sns.pairplot(
    df[key_feats + ["label"]],
    hue="label",
    hue_order=CLASS_ORDER,
    palette=CLASS_COLORS,
    plot_kws={"alpha": 0.6, "s": 20},
    diag_kind="kde",
)
plt.suptitle("Pairplot of key vibration features", fontsize=14, fontweight="bold", y=1.01)
plt.savefig(f"{PLOTS_DIR}/04_pairplot.png", dpi=120, bbox_inches="tight")
plt.close()
print(f"  saved: {PLOTS_DIR}/04_pairplot.png")

# ===========================================================
# 6. PCA 2D visualization
# ===========================================================
print("\nGenerating PCA visualization ...")
X = df[FEATURES].values
y = df["label"].values

# Standardize (PCA is scale-sensitive)
X_std = StandardScaler().fit_transform(X)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_std)
print(f"Explained variance ratio (PC1, PC2): "
      f"{pca.explained_variance_ratio_[0]:.3f}, {pca.explained_variance_ratio_[1]:.3f}")
print(f"Total variance captured by 2 PCs: "
      f"{pca.explained_variance_ratio_.sum():.3f}")

plt.figure(figsize=(9, 7))
for cls in CLASS_ORDER:
    mask = (y == cls)
    plt.scatter(
        X_pca[mask, 0], X_pca[mask, 1],
        label=cls, color=CLASS_COLORS[cls],
        alpha=0.7, s=40, edgecolors="white", linewidths=0.5,
    )
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
plt.title("PCA 2D projection of the dataset", fontsize=14, fontweight="bold")
plt.legend(title="Class")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{PLOTS_DIR}/05_pca_2d.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  saved: {PLOTS_DIR}/05_pca_2d.png")

# How much each feature contributes to each PC
loadings = pd.DataFrame(
    pca.components_.T,
    columns=["PC1", "PC2"],
    index=FEATURES,
).round(3)
print("\nPCA loadings (which features drive each PC):")
print(loadings)

# ===========================================================
# 7. Per-class summary statistics
# ===========================================================
print("\n" + "=" * 60)
print("PER-CLASS MEAN OF EACH FEATURE")
print("=" * 60)
class_means = df.groupby("label")[FEATURES].mean().round(4)
print(class_means.T)

print("\n" + "=" * 60)
print("DONE. Plots saved to:", PLOTS_DIR)
print("=" * 60)
