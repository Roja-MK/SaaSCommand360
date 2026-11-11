
import pandas as pd

from pathlib import Path

from sklearn.model_selection import (
    GroupShuffleSplit,
    StratifiedGroupKFold,
    cross_validate,
    cross_val_predict
)

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    make_scorer,
    classification_report
)


# --------------------------------
# 1. LOAD DATASET
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "subscription_churn_features.csv"

df = pd.read_csv(DATA_PATH)

# --------------------------------
# FEATURE ENGINEERING
# --------------------------------

# Payment behaviour ratios
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

# Customer support behaviour ratios
df["open_ticket_ratio"] = (
    df["open_ticket_count"] /
    df["ticket_count"].replace(0, 1)
)

df["critical_ticket_ratio"] = (
    df["critical_ticket_count"] /
    df["ticket_count"].replace(0, 1)
)

print("\nEngineered features created:")
print(
    df[
        [
            "overdue_invoice_ratio",
            "failed_invoice_ratio",
            "paid_invoice_ratio",
            "open_ticket_ratio",
            "critical_ticket_ratio"
        ]
    ].head()
)

print("=" * 60)
print("SAASCOMMAND360 - CHURN MODELING")
print("=" * 60)

print("\nDataset shape:", df.shape)
print("\nFirst five rows:")
print(df.head())


# --------------------------------
# 2. SEPARATE FEATURES AND TARGET
# --------------------------------

X = df.drop(
    columns=[
        "subscription_id",
        "account_id",
        "churn"
    ]
)

y = df["churn"]

# Keep account IDs separately for grouped splitting
groups = df["account_id"]

print("\nFeature shape:", X.shape)
print("Target shape:", y.shape)

print("\nChurn distribution:")
print(y.value_counts())

print("\nChurn percentage:")
print(y.value_counts(normalize=True) * 100)


# --------------------------------
# 3. DEFINE FEATURE COLUMNS
# --------------------------------

categorical_features = [
    "industry",
    "company_size",
    "region",
    "plan",
    "billing_cycle"
]

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
    "distinct_features_used",

    # Newly engineered features
    "overdue_invoice_ratio",
    "failed_invoice_ratio",
    "paid_invoice_ratio",
    "open_ticket_ratio",
    "critical_ticket_ratio"
]
# Verify that expected features exist
expected_features = categorical_features + numerical_features

missing_features = [
    col for col in expected_features
    if col not in X.columns
]

if missing_features:
    raise ValueError(
        f"Missing feature columns: {missing_features}"
    )


# --------------------------------
# 4. PREPROCESSING
# --------------------------------

categorical_transformer = OneHotEncoder(
    handle_unknown="ignore"
)

numerical_transformer = StandardScaler()

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            categorical_transformer,
            categorical_features
        ),
        (
            "numerical",
            numerical_transformer,
            numerical_features
        )
    ]
)


# --------------------------------
# 5. GROUPED TRAIN TEST SPLIT
# --------------------------------

group_split = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_indices, test_indices = next(
    group_split.split(X, y, groups=groups)
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]

train_groups = groups.iloc[train_indices]
test_groups = groups.iloc[test_indices]

print("\n" + "=" * 60)
print("GROUPED TRAIN TEST SPLIT")
print("=" * 60)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("Training accounts:", train_groups.nunique())
print("Testing accounts:", test_groups.nunique())

overlapping_accounts = set(train_groups) & set(test_groups)

print("Overlapping accounts:", len(overlapping_accounts))

print("\nTraining churn distribution:")
print(y_train.value_counts())

print("\nTesting churn distribution:")
print(y_test.value_counts())

if overlapping_accounts:
    raise ValueError(
        "Data leakage detected: accounts overlap between train and test."
    )


# --------------------------------
# 6. DEFINE MODELS
# --------------------------------

models = {
    "Dummy Classifier": DummyClassifier(
        strategy="most_frequent"
    ),

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        class_weight="balanced"
    )
}


# --------------------------------
# 7. GROUPED CROSS VALIDATION
# --------------------------------

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scoring = {
    "accuracy": "accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": make_scorer(recall_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
    "roc_auc": "roc_auc",
    "pr_auc": "average_precision"
}

print("\n" + "=" * 60)
print("GROUPED CROSS VALIDATION")
print("=" * 60)

cv_results = []

for name, model in models.items():

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model)
        ]
    )

    scores = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        groups=train_groups,
        scoring=scoring,
        return_train_score=False
    )

    result = {
        "Model": name,
        "Accuracy": scores["test_accuracy"].mean(),
        "Precision": scores["test_precision"].mean(),
        "Recall": scores["test_recall"].mean(),
        "F1 Score": scores["test_f1"].mean(),
        "ROC AUC": scores["test_roc_auc"].mean()
    }

    cv_results.append(result)

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    for metric in scoring:
        values = scores[f"test_{metric}"]

        print(
            f"{metric}: "
            f"{values.mean():.3f} "
            f"+/- {values.std():.3f}"
        )


# --------------------------------
# 8. LOGISTIC REGRESSION THRESHOLD TUNING
# --------------------------------

print("\n" + "=" * 60)
print("LOGISTIC REGRESSION THRESHOLD TUNING")
print("=" * 60)

logistic_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            models["Logistic Regression"]
        )
    ]
)

# Generate out-of-fold probabilities using training data only
oof_probabilities = cross_val_predict(
    logistic_pipeline,
    X_train,
    y_train,
    cv=cv,
    groups=train_groups,
    method="predict_proba"
)[:, 1]

threshold_results = []

thresholds = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50
]

for threshold in thresholds:

    predictions = (
        oof_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_train,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_train,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_train,
        predictions,
        zero_division=0
    )

    threshold_results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print(
        f"Threshold: {threshold:.2f} | "
        f"Precision: {precision:.3f} | "
        f"Recall: {recall:.3f} | "
        f"F1: {f1:.3f}"
    )


# --------------------------------
# 8.1 RANDOM FOREST THRESHOLD TUNING
# --------------------------------

print("\n" + "=" * 60)
print("RANDOM FOREST THRESHOLD TUNING")
print("=" * 60)

random_forest_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            models["Random Forest"]
        )
    ]
)

# Generate out-of-fold probabilities using training data only
rf_oof_probabilities = cross_val_predict(
    random_forest_pipeline,
    X_train,
    y_train,
    cv=cv,
    groups=train_groups,
    method="predict_proba"
)[:, 1]

rf_threshold_results = []

thresholds = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50
]

for threshold in thresholds:

    predictions = (
        rf_oof_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_train,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_train,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_train,
        predictions,
        zero_division=0
    )

    rf_threshold_results.append({
        "Threshold": threshold,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print(
        f"Threshold: {threshold:.2f} | "
        f"Precision: {precision:.3f} | "
        f"Recall: {recall:.3f} | "
        f"F1: {f1:.3f}"
    )





# --------------------------------
# 9. TRAIN AND EVALUATE ON HOLDOUT TEST DATA
# --------------------------------

print("\n" + "=" * 60)
print("FINAL HOLDOUT TEST EVALUATION")
print("=" * 60)

results = []
holdout_predictions = []

for name, model in models.items():

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model)
        ]
    )

    # Train model
    pipeline.fit(X_train, y_train)

    # Predict probabilities
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    # Apply selected thresholds
    if name == "Logistic Regression":
        predictions = (
            probabilities >= 0.20
        ).astype(int)

    elif name == "Random Forest":
        predictions = (
            probabilities >= 0.40
        ).astype(int)

    else:
        predictions = pipeline.predict(X_test)

    # Store holdout predictions
    for actual, probability, predicted in zip(
        y_test, probabilities, predictions
    ):
        holdout_predictions.append({
            "Model": name,
            "Actual": actual,
            "Predicted_Probability": probability,
            "Predicted": predicted
        })

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities
    )

    # Store model results
    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "ROC AUC": roc_auc,
        "PR AUC": pr_auc
    })

    # Display model evaluation
    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    if name == "Logistic Regression":
        print("Applied threshold: 0.20")

    elif name == "Random Forest":
        print("Applied threshold: 0.40")

    else:
        print("Applied threshold: 0.50 (default)")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nROC AUC:", round(roc_auc, 3))
    print("PR AUC:", round(pr_auc, 3))

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )


# --------------------------------
# 10. SAVE HOLDOUT RESULTS
# --------------------------------

# Create holdout comparison DataFrame
holdout_results = pd.DataFrame(results)

# Create predictions DataFrame
predictions_df = pd.DataFrame(holdout_predictions)

# Save holdout predictions
predictions_df.to_csv(
    "ml/data/holdout_predictions.csv",
    index=False
)

# Save holdout model comparison
holdout_results.to_csv(
    "ml/data/holdout_model_comparison.csv",
    index=False
)

print("\nHoldout predictions and model comparison saved!")

print("\n" + "=" * 60)
print("HOLDOUT MODEL COMPARISON")
print("=" * 60)

print(
    holdout_results.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)


# --------------------------------
# 11. CROSS VALIDATION MODEL COMPARISON
# --------------------------------

cv_results_df = pd.DataFrame(cv_results)

print("\n" + "=" * 60)
print("CROSS VALIDATION MODEL COMPARISON")
print("=" * 60)

print(
    cv_results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print("\nTraining and evaluation completed!")


# --------------------------------
# 12. SAVE SELECTED TRAINED MODEL
# --------------------------------

import joblib
from pathlib import Path

# Create model directory if it doesn't exist
model_dir = Path("ml/models")
model_dir.mkdir(parents=True, exist_ok=True)

# Build Logistic Regression pipeline
best_model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", models["Logistic Regression"])
    ]
)

# Train using training data only
best_model_pipeline.fit(X_train, y_train)

# Save trained pipeline
model_path = model_dir / "logistic_regression_churn_model.joblib"

joblib.dump(best_model_pipeline, model_path)

# Save classification threshold
threshold_path = model_dir / "classification_threshold.txt"
threshold_path.write_text("0.20", encoding="utf-8")

print("\n" + "=" * 60)
print("MODEL SAVING COMPLETED")
print("=" * 60)

print(f"Selected model: Logistic Regression")
print(f"Model saved at: {model_path}")
print(f"Classification threshold: 0.20")
print(f"Threshold saved at: {threshold_path}")

