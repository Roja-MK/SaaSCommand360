
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------
# 1. LOAD DATA
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "subscription_churn_features.csv"

df = pd.read_csv(DATA_PATH)

PLOT_DIR = BASE_DIR / "plots"
PLOT_DIR.mkdir(exist_ok=True)


# --------------------------------
# 2. CHURN RATE BY CATEGORICAL FEATURES
# --------------------------------

categorical_features = [
    "industry",
    "company_size",
    "region",
    "plan",
    "billing_cycle"
]

for feature in categorical_features:

    churn_rates = (
        df.groupby(feature, observed=True)["churn"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(9, 5))

    churn_rates.plot(kind="bar")

    plt.title(f"Churn Rate by {feature.replace('_', ' ').title()}")
    plt.xlabel(feature.replace("_", " ").title())
    plt.ylabel("Churn Rate (%)")

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / f"churn_by_{feature}.png",
        dpi=150
    )

    plt.close()


# --------------------------------
# 3. TENURE COMPARISON
# --------------------------------

plt.figure(figsize=(8, 5))

df.boxplot(
    column="tenure_days",
    by="churn"
)

plt.title("Tenure Comparison: Churn vs Non-Churn")
plt.suptitle("")
plt.xlabel("Churn (0 = No, 1 = Yes)")
plt.ylabel("Tenure (Days)")

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "tenure_comparison.png",
    dpi=150
)

plt.close()


# --------------------------------
# 4. NUMERICAL FEATURE COMPARISON
# --------------------------------

numerical_features = [
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

comparison = df.groupby("churn")[numerical_features].mean().T

comparison.columns = ["Non-Churn", "Churn"]

comparison.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Average Numerical Features: Churn vs Non-Churn")
plt.xlabel("Features")
plt.ylabel("Average Value")
plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "numerical_feature_comparison.png",
    dpi=150
)

plt.close()


# --------------------------------
# 5. COMPLETION
# --------------------------------

print("Feature visualizations completed!")

print("\nCharts saved in:")
print(PLOT_DIR)
