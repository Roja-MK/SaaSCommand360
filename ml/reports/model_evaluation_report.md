# SaaSCommand360 - ML Model Evaluation Report

Generated on: 2026-11-11 15:38:04

## 1. Project Overview
SaaSCommand360 uses machine learning to identify SaaS subscriptions that may churn during the defined prediction window.

## 2. Dataset Information
- Total eligible records: 321
- Total accounts: 234
- Training records: 255
- Testing records: 66
- Holdout churn cases: 11
- Holdout non-churn cases: 55

## 3. Model Performance Comparison

| Model               |   Accuracy |   Precision |   Recall |   F1 Score |   ROC AUC |   PR AUC |
|:--------------------|-----------:|------------:|---------:|-----------:|----------:|---------:|
| Dummy Classifier    |   0.833333 |    0        | 0        |   0        |  0.5      | 0.166667 |
| Logistic Regression |   0.363636 |    0.155556 | 0.636364 |   0.25     |  0.477686 | 0.245026 |
| Random Forest       |   0.666667 |    0.176471 | 0.272727 |   0.214286 |  0.570248 | 0.218307 |

## 4. Confusion Matrix Details

| Model               |   True Positives |   True Negatives |   False Positives |   False Negatives |
|:--------------------|-----------------:|-----------------:|------------------:|------------------:|
| Dummy Classifier    |                0 |               55 |                 0 |                11 |
| Logistic Regression |                7 |               17 |                38 |                 4 |
| Random Forest       |                3 |               41 |                14 |                 8 |

## 5. Model Interpretation

- Logistic Regression recall: 0.636
- Logistic Regression precision: 0.156
- Logistic Regression F1 score: 0.250
- Random Forest recall: 0.273
- Random Forest precision: 0.176
- Random Forest F1 score: 0.214

## 6. Selected Model

Provisional model selection: Logistic Regression

Logistic Regression is selected provisionally because it detected more churn cases in the holdout dataset. However, it also generated many false positives.

## 7. Limitations

- The dataset contains only 321 eligible subscription records.
- The holdout dataset contains only 11 churn cases.
- Model performance may vary because of the small dataset.
- Logistic Regression has a high false-positive count.
- Random Forest missed several actual churn cases.
- Results require validation on more real-world data.

## 8. Conclusion

The current models demonstrate a baseline approach for SaaS churn prediction. Logistic Regression is the provisional choice when detecting more potential churn cases is the priority. Further data collection, validation and model improvement are required before production deployment.