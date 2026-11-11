
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


print("=" * 60)
print("SAASCOMMAND360 - FEATURE IMPORTANCE")
print("=" * 60)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "ml" / "data" / "subscription_churn_features.csv"
OUTPUT_PATH = BASE_DIR / "ml" / "data" / "feature_importance.csv"
CHART_PATH = BASE_DIR / "ml" / "plots" / "feature_importance.png"

# Load dataset
df = pd.read_csv(DATA_PATH)

# Create engineered ratio features

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

print("\nDataset shape:", df.shape)

# Separate features and target
X = df.drop(columns=["subscription_id", "account_id", "churn"])
y = df["churn"]
groups = df["account_id"]

# Identify feature types
categorical_features = [
    "industry",
    "company_size",
    "region",
    "plan",
    "billing_cycle"
]

numerical_features = [
    col for col in X.columns
    if col not in categorical_features
]

# Split by account to prevent account overlap
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
y_train = y.iloc[train_idx]

print("\nTraining records:", len(X_train))
print("Training accounts:", groups.iloc[train_idx].nunique())

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)

# Random Forest
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=200,
                max_depth=6,
                random_state=42,
                class_weight="balanced"
            )
        )
    ]
)

# Train only on training data
model.fit(X_train, y_train)

# Extract feature importance
feature_names = (
    model.named_steps["preprocessor"]
    .get_feature_names_out()
)

importances = (
    model.named_steps["classifier"]
    .feature_importances_
)

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

# Display top 15
print("\nTOP 15 IMPORTANT FEATURES")
print(importance_df.head(15).to_string(index=False))

# Save CSV
importance_df.to_csv(OUTPUT_PATH, index=False)

# Save chart
top_features = importance_df.head(15).sort_values(
    by="Importance"
)

CHART_PATH.parent.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(12, 8))

plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)

plt.title("Top 15 Feature Importance - Training Data")
plt.xlabel("Importance")
plt.ylabel("Features")
plt.tight_layout()

plt.savefig(CHART_PATH, dpi=300)
plt.close()

print("\nFeature importance saved to:", OUTPUT_PATH)
print("Chart saved to:", CHART_PATH)

print("\nFeature importance analysis completed!")
