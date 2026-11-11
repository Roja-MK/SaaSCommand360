
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)

# --------------------------------
# 1. SET PROJECT PATHS
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
PLOTS_DIR = BASE_DIR / "plots"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------
# 2. LOAD SAVED DATA
# --------------------------------

predictions_df = pd.read_csv(
    DATA_DIR / "holdout_predictions.csv"
)

comparison_df = pd.read_csv(
    DATA_DIR / "holdout_model_comparison.csv"
)

print("=" * 60)
print("SAASCOMMAND360 - MODEL VISUALIZATION")
print("=" * 60)

print("\nPredictions shape:", predictions_df.shape)
print("Comparison shape:", comparison_df.shape)

models = predictions_df["Model"].unique()

# --------------------------------
# 3. CONFUSION MATRIX
# --------------------------------

for model_name in models:

    model_data = predictions_df[
        predictions_df["Model"] == model_name
    ]

    y_true = model_data["Actual"]
    y_pred = model_data["Predicted"]

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["No Churn", "Churn"]
    )

    display.plot(values_format="d")

    plt.title(f"{model_name} - Confusion Matrix")
    plt.tight_layout()

    filename = (
        model_name.lower().replace(" ", "_")
        + "_confusion_matrix.png"
    )

    plt.savefig(
        PLOTS_DIR / filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved:", filename)


# --------------------------------
# 4. ROC CURVE COMPARISON
# --------------------------------

plt.figure(figsize=(9, 6))

for model_name in models:

    model_data = predictions_df[
        predictions_df["Model"] == model_name
    ]

    y_true = model_data["Actual"]
    probabilities = model_data["Predicted_Probability"]

    fpr, tpr, _ = roc_curve(
        y_true,
        probabilities
    )

    roc_score = auc(fpr, tpr)

    plt.plot(
        fpr,
        tpr,
        label=f"{model_name} (AUC = {roc_score:.3f})"
    )

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random Classifier"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve - Model Comparison")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "roc_curve_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: roc_curve_comparison.png")


# --------------------------------
# 5. PRECISION-RECALL CURVE
# --------------------------------

plt.figure(figsize=(9, 6))

for model_name in models:

    model_data = predictions_df[
        predictions_df["Model"] == model_name
    ]

    y_true = model_data["Actual"]
    probabilities = model_data["Predicted_Probability"]

    precision, recall, _ = precision_recall_curve(
        y_true,
        probabilities
    )

    pr_score = average_precision_score(
        y_true,
        probabilities
    )

    plt.plot(
        recall,
        precision,
        label=f"{model_name} (AP = {pr_score:.3f})"
    )

plt.xlabel("Recall")
plt.ylabel("Precision")

plt.title("Precision-Recall Curve - Model Comparison")

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "precision_recall_curve.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: precision_recall_curve.png")


# --------------------------------
# 6. MODEL METRICS COMPARISON
# --------------------------------

metrics = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1 Score",
    "ROC AUC",
    "PR AUC"
]

comparison_df.set_index("Model")[metrics].plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Holdout Model Performance Comparison")
plt.ylabel("Score")
plt.xlabel("Model")

plt.ylim(0, 1)
plt.xticks(rotation=15)

plt.legend(
    title="Metrics",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(axis="y")
plt.tight_layout()

plt.savefig(
    PLOTS_DIR / "model_performance_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: model_performance_comparison.png")


# --------------------------------
# 7. FINAL SUMMARY
# --------------------------------

print("\n" + "=" * 60)
print("MODEL VISUALIZATION COMPLETED")
print("=" * 60)

print("\nGenerated plots:")

for file in PLOTS_DIR.glob("*.png"):
    print(file.name)

print("\nAll visualizations saved successfully!")
