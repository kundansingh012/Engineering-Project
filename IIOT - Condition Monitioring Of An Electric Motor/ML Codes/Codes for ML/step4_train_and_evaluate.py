"""
Step 4 (new): Train and evaluate SVM (RBF) and Logistic Regression
on the 6 vibration features (motor_dataset_v2).

Outputs:
  - results_summary_v2.csv      : final comparison table (2 rows)
  - confusion_matrices_v2/*.png : 2 confusion matrices
  - classification_reports_v2.txt
  - models_v2/*.joblib          : the trained best model for each
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
)

# ===========================================================
# CONFIGURATION
# ===========================================================
TRAIN_PATH    = "train_scaled_v2.csv"
TEST_PATH     = "test_scaled_v2.csv"
ENCODER_PATH  = "label_encoder_v2.joblib"

CM_DIR        = "confusion_matrices_v2"
MODELS_DIR    = "models_v2"
SUMMARY_CSV   = "results_summary_v2.csv"
REPORTS_TXT   = "classification_reports_v2.txt"

CV_FOLDS      = 5
RANDOM_SEED   = 42

os.makedirs(CM_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ===========================================================
# 1. Load data and label encoder
# ===========================================================
train_df = pd.read_csv(TRAIN_PATH)
test_df  = pd.read_csv(TEST_PATH)
le       = joblib.load(ENCODER_PATH)
class_names = list(le.classes_)

FEATURES = [c for c in train_df.columns if c != "label"]

X_train = train_df[FEATURES].values
y_train = train_df["label"].values
X_test  = test_df[FEATURES].values
y_test  = test_df["label"].values

print(f"Train: {X_train.shape}, Test: {X_test.shape}")
print(f"Features ({len(FEATURES)}): {FEATURES}")
print(f"Classes: {class_names}\n")

# ===========================================================
# 2. Define models and grids
# ===========================================================
MODELS = {
    "SVM_rbf": {
        "estimator": SVC(kernel="rbf", random_state=RANDOM_SEED),
        "param_grid": {
            "C":     [0.1, 1, 10, 100],
            "gamma": ["scale", 0.01, 0.1, 1],
        },
    },
    "LogReg": {
        "estimator": LogisticRegression(
            solver="lbfgs", max_iter=2000, random_state=RANDOM_SEED,
        ),
        "param_grid": {
            "C": [0.01, 0.1, 1, 10, 100],
        },
    },
}

cv_strategy = StratifiedKFold(
    n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_SEED,
)

# ===========================================================
# 3. Helper: confusion matrix plot
# ===========================================================
def plot_cm(cm, labels, title, save_path):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels,
                cbar=True, square=True)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

# ===========================================================
# 4. Train and evaluate each model
# ===========================================================
summary_rows = []
text_reports = []

for model_name, cfg in MODELS.items():
    print("=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    gs = GridSearchCV(
        estimator=cfg["estimator"],
        param_grid=cfg["param_grid"],
        cv=cv_strategy,
        scoring="accuracy",
        n_jobs=-1,
        refit=True,
    )
    gs.fit(X_train, y_train)

    best_model  = gs.best_estimator_
    best_params = gs.best_params_
    cv_score    = gs.best_score_

    # Evaluate on the held-out test set
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0,
    )

    # Confusion matrix figure
    cm = confusion_matrix(y_test, y_pred)
    cm_path = f"{CM_DIR}/{model_name}.png"
    plot_cm(cm, class_names,
            f"{model_name}\nTest accuracy = {acc:.3f}",
            cm_path)

    # Per-class report (text)
    report_text = classification_report(
        y_test, y_pred, target_names=class_names, zero_division=0, digits=3,
    )
    text_reports.append(
        f"\n{'=' * 70}\n"
        f"Model: {model_name}\n"
        f"Best params: {best_params}\n"
        f"CV accuracy: {cv_score:.4f}    Test accuracy: {acc:.4f}\n"
        f"{'=' * 70}\n{report_text}\n"
        f"Confusion matrix (rows = true, cols = predicted):\n"
        f"{pd.DataFrame(cm, index=class_names, columns=class_names).to_string()}\n"
    )

    # Save model
    model_path = f"{MODELS_DIR}/{model_name}.joblib"
    joblib.dump(best_model, model_path)

    summary_rows.append({
        "model":           model_name,
        "best_params":     json.dumps(best_params),
        "cv_accuracy":     round(cv_score, 4),
        "test_accuracy":   round(acc, 4),
        "precision_macro": round(prec, 4),
        "recall_macro":    round(rec, 4),
        "f1_macro":        round(f1, 4),
    })

    print(f"Best params  : {best_params}")
    print(f"CV accuracy  : {cv_score:.4f}")
    print(f"Test accuracy: {acc:.4f}")
    print(f"Macro F1     : {f1:.4f}")
    print(f"Saved CM     -> {cm_path}")
    print(f"Saved model  -> {model_path}\n")

# ===========================================================
# 5. Save summary table and text reports
# ===========================================================
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(SUMMARY_CSV, index=False)

with open(REPORTS_TXT, "w") as f:
    f.write("".join(text_reports))

# ===========================================================
# 6. Pretty print final summary
# ===========================================================
print("=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(summary_df.to_string(index=False))
print(f"\nSaved summary to : {SUMMARY_CSV}")
print(f"Saved reports to : {REPORTS_TXT}")
print(f"Saved CMs to     : {CM_DIR}/")
print(f"Saved models to  : {MODELS_DIR}/")
