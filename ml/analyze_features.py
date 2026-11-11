
import pandas as pd
from pathlib import Path

# --------------------------------
# 1. LOAD DATASET
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "subscription_churn_features.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("SAASCOMMAND360 - CHURN FEATURE ANALYSIS")
print("=" * 60)

print("\nDataset shape:", df.shape)


# --------------------------------
# 2. CHURN DISTRIBUTION
# --------------------------------

print("\nCHURN DISTRIBUTION")

print(
    df["churn"].value_counts()
)

print("\nChurn percentage:")

print(
    (df["churn"].value_counts(normalize=True) * 100).round(2)
)


# --------------------------------
# 3. CATEGORICAL FEATURE ANALYSIS
# --------------------------------

categorical_features = [
    "industry",
    "company_size",
    "region",
    "plan",
    "billing_cycle"
]

for feature in categorical_features:

    print("\n" + "=" * 60)
    print(f"CHURN ANALYSIS BY {feature.upper()}")
    print("=" * 60)

    analysis = (
        df.groupby(feature, observed=True)
        .agg(
            total_subscriptions=("churn", "count"),
            churned_subscriptions=("churn", "sum"),
            churn_rate=("churn", "mean")
        )
        .reset_index()
    )

    analysis["churn_rate"] = (
        analysis["churn_rate"] * 100
    ).round(2)

    print(
        analysis.sort_values(
            "churn_rate",
            ascending=False
        ).to_string(index=False)
    )


# --------------------------------
# 4. NUMERICAL FEATURE ANALYSIS
# --------------------------------

numerical_features = [
    "tenure_days",
    "invoice_count",
    "total_invoice_amount",
    "paid_invoice_count",
    "overdue_invoice_count",
    "failed_invoice_count",
    "ticket_count",
    "open_ticket_count",
    "critical_ticket_count",
    "product_event_count",
    "distinct_features_used"
]

print("\n" + "=" * 60)
print("NUMERICAL FEATURE COMPARISON")
print("=" * 60)

comparison = (
    df.groupby("churn")[numerical_features]
    .mean()
    .T
)

comparison.columns = [
    "Non-Churn Average",
    "Churn Average"
]

comparison["Difference"] = (
    comparison["Churn Average"]
    - comparison["Non-Churn Average"]
)

print(
    comparison.round(2).to_string()
)


# --------------------------------
# 5. SAVE ANALYSIS RESULTS
# --------------------------------

OUTPUT_PATH = BASE_DIR / "data" / "feature_analysis.csv"

comparison.to_csv(OUTPUT_PATH)

print("\nFeature analysis saved to:")
print(OUTPUT_PATH)

print("\nFeature analysis completed!")
