
import pandas as pd
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

comparison_file = DATA_DIR / "holdout_model_comparison.csv"
predictions_file = DATA_DIR / "holdout_predictions.csv"

# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

comparison = pd.read_csv(comparison_file)
predictions = pd.read_csv(predictions_file)

# --------------------------------------------------
# 3. DATASET INFORMATION
# --------------------------------------------------

total_records = 321
training_records = 255
testing_records = 66
total_accounts = 234

actual_churn = int(
    predictions[predictions["Model"] == "Dummy Classifier"]["Actual"].sum()
)

actual_non_churn = testing_records - actual_churn

# --------------------------------------------------
# 4. CONFUSION MATRIX DETAILS
# --------------------------------------------------

confusion_details = []

for model in predictions["Model"].unique():

    model_data = predictions[predictions["Model"] == model]

    actual = model_data["Actual"]
    predicted = model_data["Predicted"]

    tp = int(((actual == 1) & (predicted == 1)).sum())
    tn = int(((actual == 0) & (predicted == 0)).sum())
    fp = int(((actual == 0) & (predicted == 1)).sum())
    fn = int(((actual == 1) & (predicted == 0)).sum())

    confusion_details.append({
        "Model": model,
        "True Positives": tp,
        "True Negatives": tn,
        "False Positives": fp,
        "False Negatives": fn
    })

confusion_df = pd.DataFrame(confusion_details)

# --------------------------------------------------
# 5. FINAL MODEL SELECTION
# --------------------------------------------------

lr = comparison[
    comparison["Model"] == "Logistic Regression"
].iloc[0]

rf = comparison[
    comparison["Model"] == "Random Forest"
].iloc[0]

selected_model = "Logistic Regression"

# --------------------------------------------------
# 6. GENERATE REPORT
# --------------------------------------------------

report = []

report.append("# SaaSCommand360 - ML Model Evaluation Report")
report.append("")
report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("")

report.append("## 1. Project Overview")
report.append(
    "SaaSCommand360 uses machine learning to identify SaaS subscriptions "
    "that may churn during the defined prediction window."
)
report.append("")

report.append("## 2. Dataset Information")
report.append(f"- Total eligible records: {total_records}")
report.append(f"- Total accounts: {total_accounts}")
report.append(f"- Training records: {training_records}")
report.append(f"- Testing records: {testing_records}")
report.append(f"- Holdout churn cases: {actual_churn}")
report.append(f"- Holdout non-churn cases: {actual_non_churn}")
report.append("")

report.append("## 3. Model Performance Comparison")
report.append("")
report.append(comparison.to_markdown(index=False))
report.append("")

report.append("## 4. Confusion Matrix Details")
report.append("")
report.append(confusion_df.to_markdown(index=False))
report.append("")

report.append("## 5. Model Interpretation")
report.append("")
report.append(
    f"- Logistic Regression recall: {lr['Recall']:.3f}"
)
report.append(
    f"- Logistic Regression precision: {lr['Precision']:.3f}"
)
report.append(
    f"- Logistic Regression F1 score: {lr['F1 Score']:.3f}"
)
report.append(
    f"- Random Forest recall: {rf['Recall']:.3f}"
)
report.append(
    f"- Random Forest precision: {rf['Precision']:.3f}"
)
report.append(
    f"- Random Forest F1 score: {rf['F1 Score']:.3f}"
)
report.append("")

report.append("## 6. Selected Model")
report.append("")
report.append(f"Provisional model selection: {selected_model}")
report.append("")
report.append(
    "Logistic Regression is selected provisionally because it detected "
    "more churn cases in the holdout dataset. However, it also generated "
    "many false positives."
)
report.append("")

report.append("## 7. Limitations")
report.append("")
report.append(
    "- The dataset contains only 321 eligible subscription records."
)
report.append(
    "- The holdout dataset contains only 11 churn cases."
)
report.append(
    "- Model performance may vary because of the small dataset."
)
report.append(
    "- Logistic Regression has a high false-positive count."
)
report.append(
    "- Random Forest missed several actual churn cases."
)
report.append(
    "- Results require validation on more real-world data."
)
report.append("")

report.append("## 8. Conclusion")
report.append("")
report.append(
    "The current models demonstrate a baseline approach for SaaS churn "
    "prediction. Logistic Regression is the provisional choice when "
    "detecting more potential churn cases is the priority. Further data "
    "collection, validation and model improvement are required before "
    "production deployment."
)

# --------------------------------------------------
# 7. SAVE REPORT
# --------------------------------------------------

report_path = REPORT_DIR / "model_evaluation_report.md"

report_path.write_text(
    "\n".join(report),
    encoding="utf-8"
)

# Save confusion matrix summary separately
confusion_path = DATA_DIR / "confusion_matrix_summary.csv"
confusion_df.to_csv(confusion_path, index=False)

print("=" * 60)
print("SAASCOMMAND360 - MODEL EVALUATION REPORT")
print("=" * 60)

print("\nModel comparison:")
print(comparison.to_string(index=False))

print("\nConfusion matrix summary:")
print(confusion_df.to_string(index=False))

print("\nSelected model:", selected_model)

print("\nGenerated files:")
print(report_path)
print(confusion_path)

print("\nMODEL EVALUATION REPORT GENERATED SUCCESSFULLY!")
