
import pandas as pd
import joblib

from pathlib import Path

# ----------------------------------------
# 1. PROJECT PATHS
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "logistic_regression_churn_model.joblib"
THRESHOLD_PATH = BASE_DIR / "models" / "classification_threshold.txt"

DATA_PATH = BASE_DIR / "data" / "subscription_churn_features.csv"

OUTPUT_PATH = BASE_DIR / "data" / "churn_predictions.csv"

# ----------------------------------------
# 2. LOAD TRAINED MODEL
# ----------------------------------------

print("=" * 60)
print("SAASCOMMAND360 - CHURN PREDICTION")
print("=" * 60)

model = joblib.load(MODEL_PATH)

threshold = float(
    THRESHOLD_PATH.read_text(encoding="utf-8").strip()
)

print("\nTrained model loaded successfully!")
print("Classification threshold:", threshold)

# ----------------------------------------
# 3. LOAD SUBSCRIPTION DATA
# ----------------------------------------

df = pd.read_csv(DATA_PATH)

print("\nDataset loaded successfully!")
print("Dataset shape:", df.shape)

# ----------------------------------------
# 4. CREATE ENGINEERED FEATURES
# ----------------------------------------

df["overdue_invoice_ratio"] = (
    df["overdue_invoice_count"] /
    df["invoice_count"].replace(0, 1)
)

df["failed_invoice_ratio"] = (
    df["failed_invoice_count"] /
    df["invoice_count"].replace(0, 1)
)

df["paid_invoice_ratio"] = (
    df["paid_invoice_count"] /
    df["invoice_count"].replace(0, 1)
)

df["open_ticket_ratio"] = (
    df["open_ticket_count"] /
    df["ticket_count"].replace(0, 1)
)

df["critical_ticket_ratio"] = (
    df["critical_ticket_count"] /
    df["ticket_count"].replace(0, 1)
)

# ----------------------------------------
# 5. PREPARE MODEL INPUT
# ----------------------------------------

# Remove identifiers and target column.
# The model pipeline handles preprocessing.

X = df.drop(
    columns=[
        "subscription_id",
        "account_id",
        "churn"
    ],
    errors="ignore"
)

# ----------------------------------------
# 6. PREDICT CHURN PROBABILITIES
# ----------------------------------------

probabilities = model.predict_proba(X)[:, 1]

predictions = (
    probabilities >= threshold
).astype(int)

# ----------------------------------------
# 7. CREATE PREDICTION RESULTS
# ----------------------------------------

results = pd.DataFrame()

results["subscription_id"] = df["subscription_id"]
results["account_id"] = df["account_id"]

results["churn_probability"] = probabilities

results["predicted_churn"] = predictions

results["churn_status"] = results["predicted_churn"].map({
    1: "Churn Risk",
    0: "No Churn Risk"
})

# ----------------------------------------
# 8. SAVE PREDICTIONS
# ----------------------------------------

results.to_csv(
    OUTPUT_PATH,
    index=False
)

# ----------------------------------------
# 9. DISPLAY RESULTS
# ----------------------------------------

print("\n" + "=" * 60)
print("CHURN PREDICTION RESULTS")
print("=" * 60)

print(results.head(10).to_string(index=False))

print("\nPrediction Summary:")

print(
    results["churn_status"].value_counts()
)

print("\nPredictions saved at:")
print(OUTPUT_PATH)

print("\nCHURN PREDICTION COMPLETED!")
