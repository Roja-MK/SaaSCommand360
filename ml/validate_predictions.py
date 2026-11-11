
import pandas as pd

from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ----------------------------------------
# 1. PROJECT PATHS
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FEATURES_PATH = DATA_DIR / "subscription_churn_features.csv"
PREDICTIONS_PATH = DATA_DIR / "churn_predictions.csv"

OUTPUT_PATH = DATA_DIR / "prediction_validation.csv"

# ----------------------------------------
# 2. LOAD DATA
# ----------------------------------------

actual_df = pd.read_csv(FEATURES_PATH)
prediction_df = pd.read_csv(PREDICTIONS_PATH)

# ----------------------------------------
# 3. MATCH ACTUAL AND PREDICTED RECORDS
# ----------------------------------------

validation_df = actual_df[
    ["subscription_id", "account_id", "churn"]
].merge(
    prediction_df[
        [
            "subscription_id",
            "churn_probability",
            "predicted_churn",
            "churn_status"
        ]
    ],
    on="subscription_id",
    how="inner",
    validate="one_to_one"
)

y_actual = validation_df["churn"]
y_predicted = validation_df["predicted_churn"]

# ----------------------------------------
# 4. CALCULATE METRICS
# ----------------------------------------

accuracy = accuracy_score(y_actual, y_predicted)

precision = precision_score(
    y_actual, y_predicted, zero_division=0
)

recall = recall_score(
    y_actual, y_predicted, zero_division=0
)

f1 = f1_score(
    y_actual, y_predicted, zero_division=0
)

cm = confusion_matrix(
    y_actual,
    y_predicted,
    labels=[0, 1]
)

# ----------------------------------------
# 5. DISPLAY RESULTS
# ----------------------------------------

print("=" * 60)
print("SAASCOMMAND360 - PREDICTION VALIDATION")
print("=" * 60)

print("\nTotal matched records:", len(validation_df))

print("\nActual churn distribution:")
print(y_actual.value_counts())

print("\nPredicted churn distribution:")
print(y_predicted.value_counts())

print("\nConfusion Matrix:")
print(cm)

print("\nModel Metrics:")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")

print("\nClassification Report:")
print(
    classification_report(
        y_actual,
        y_predicted,
        target_names=["No Churn", "Churn"],
        zero_division=0
    )
)

# ----------------------------------------
# 6. SAVE VALIDATION RESULTS
# ----------------------------------------

validation_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nValidation results saved at:")
print(OUTPUT_PATH)

print("\nPREDICTION VALIDATION COMPLETED!")

print("\nIMPORTANT:")
print(
    "These are in-sample predictions on the historical dataset. "
    "They do not represent independent model performance."
)
