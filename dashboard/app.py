
import streamlit as st
import pandas as pd

from pathlib import Path

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SaaSCommand360",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "ml" / "data"
PLOTS_DIR = BASE_DIR / "ml" / "plots"

# ==========================================
# 2. LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    validation = pd.read_csv(
        DATA_DIR / "prediction_validation.csv"
    )

    model_comparison = pd.read_csv(
        DATA_DIR / "holdout_model_comparison.csv"
    )

    feature_importance_path = DATA_DIR / "feature_importance.csv"

    if feature_importance_path.exists():
        feature_importance = pd.read_csv(
            feature_importance_path
        )
    else:
        feature_importance = pd.DataFrame()

    return validation, model_comparison, feature_importance


try:
    validation, model_comparison, feature_importance = load_data()

except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.info(
        "Make sure the ML scripts have been executed "
        "and the required CSV files exist."
    )
    st.stop()


# ==========================================
# 3. SIDEBAR
# ==========================================

st.sidebar.title("SaaSCommand360")

st.sidebar.markdown("---")

st.sidebar.subheader("Dashboard Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Overview",
        "Churn Analysis",
        "Model Performance",
        "Feature Importance",
        "Prediction Details"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "SaaS Subscription Churn Prediction Platform"
)


# ==========================================
# 4. COMMON METRICS
# ==========================================

total_subscriptions = len(validation)

actual_churn = int(validation["churn"].sum())

actual_non_churn = total_subscriptions - actual_churn

predicted_churn = int(
    validation["predicted_churn"].sum()
)

predicted_non_churn = (
    total_subscriptions - predicted_churn
)

churn_rate = (
    actual_churn / total_subscriptions * 100
    if total_subscriptions else 0
)

prediction_rate = (
    predicted_churn / total_subscriptions * 100
    if total_subscriptions else 0
)


# ==========================================
# 5. DASHBOARD HEADER
# ==========================================

st.title("📊 SaaSCommand360")

st.markdown(
    "### SaaS Subscription Churn Analytics Dashboard"
)

st.markdown(
    "Monitor subscription churn, analyze customer risk "
    "and evaluate machine learning performance."
)

st.markdown("---")


# ==========================================
# PAGE 1: OVERVIEW
# ==========================================

if page == "Overview":

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Subscriptions",
        total_subscriptions
    )

    col2.metric(
        "Actual Churn",
        actual_churn
    )

    col3.metric(
        "Actual Churn Rate",
        f"{churn_rate:.2f}%"
    )

    col4.metric(
        "Predicted Churn Risk",
        predicted_churn
    )

    st.markdown("---")

    left, right = st.columns(2)

    with left:

        st.subheader("Actual Subscription Status")

        actual_chart = pd.DataFrame({
            "Status": ["Churn", "No Churn"],
            "Subscriptions": [
                actual_churn,
                actual_non_churn
            ]
        })

        st.bar_chart(
            actual_chart.set_index("Status")
        )

    with right:

        st.subheader("Predicted Churn Risk")

        prediction_chart = pd.DataFrame({
            "Status": ["Churn Risk", "No Churn Risk"],
            "Subscriptions": [
                predicted_churn,
                predicted_non_churn
            ]
        })

        st.bar_chart(
            prediction_chart.set_index("Status")
        )

    st.markdown("---")

    st.subheader("Actual vs Predicted Churn")

    comparison_chart = pd.DataFrame({
        "Category": ["Actual Churn", "Predicted Churn"],
        "Subscriptions": [
            actual_churn,
            predicted_churn
        ]
    })

    st.bar_chart(
        comparison_chart.set_index("Category")
    )


# ==========================================
# PAGE 2: CHURN ANALYSIS
# ==========================================

elif page == "Churn Analysis":

    st.subheader("Churn Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Churned Subscriptions",
        actual_churn
    )

    col2.metric(
        "Active / Non-Churn",
        actual_non_churn
    )

    col3.metric(
        "Churn Rate",
        f"{churn_rate:.2f}%"
    )

    st.markdown("---")

    st.subheader("Churn Distribution")

    churn_distribution = pd.DataFrame({
        "Subscription Status": [
            "Churn",
            "No Churn"
        ],
        "Count": [
            actual_churn,
            actual_non_churn
        ]
    })

    st.bar_chart(
        churn_distribution.set_index(
            "Subscription Status"
        )
    )

    st.subheader("Churn by Subscription Plan")

    features_path = DATA_DIR / "subscription_churn_features.csv"

    if features_path.exists():

        features = pd.read_csv(features_path)

        if "plan" in features.columns:

            plan_analysis = (
                features.groupby("plan")["churn"]
                .agg(["count", "sum", "mean"])
                .reset_index()
            )

            plan_analysis["churn_rate"] = (
                plan_analysis["mean"] * 100
            )

            st.dataframe(
                plan_analysis.drop(columns=["mean"]),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("Plan column is not available.")

    else:
        st.warning("Subscription feature dataset not found.")


# ==========================================
# PAGE 3: MODEL PERFORMANCE
# ==========================================

elif page == "Model Performance":

    st.subheader("Machine Learning Model Performance")

    st.markdown(
        "Comparison of models using the independent holdout dataset."
    )

    st.dataframe(
        model_comparison,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("Performance Comparison")

    metric = st.selectbox(
        "Select Performance Metric",
        [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "ROC AUC",
            "PR AUC"
        ]
    )

    performance_chart = model_comparison[
        ["Model", metric]
    ].set_index("Model")

    st.bar_chart(performance_chart)

    st.markdown("---")

    st.subheader("Confusion Matrix")

    confusion_path = DATA_DIR / "confusion_matrix_summary.csv"

    if confusion_path.exists():

        confusion = pd.read_csv(confusion_path)

        st.dataframe(
            confusion,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Run the model evaluation script to generate "
            "the confusion matrix summary."
        )


# ==========================================
# PAGE 4: FEATURE IMPORTANCE
# ==========================================

elif page == "Feature Importance":

    st.subheader("Feature Importance Analysis")

    if not feature_importance.empty:

        importance_columns = feature_importance.columns.tolist()

        feature_column = next(
            (
                col for col in importance_columns
                if col.lower() in ["feature", "features"]
            ),
            None
        )

        importance_column = next(
            (
                col for col in importance_columns
                if col.lower() in ["importance", "importance_score"]
            ),
            None
        )

        if feature_column and importance_column:

            top_features = (
                feature_importance
                .sort_values(
                    by=importance_column,
                    ascending=False
                )
                .head(15)
                .sort_values(
                    by=importance_column,
                    ascending=True
                )
            )

            st.subheader("Top 15 Important Features")

            st.bar_chart(
                top_features.set_index(feature_column)[
                    [importance_column]
                ]
            )

            st.dataframe(
                top_features,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "Could not identify feature and importance columns."
            )

            st.write(feature_importance.head())

    else:

        st.warning(
            "Feature importance data is not available."
        )


# ==========================================
# PAGE 5: PREDICTION DETAILS
# ==========================================

elif page == "Prediction Details":

    st.subheader("Subscription Churn Predictions")

    st.markdown(
        "Explore predicted churn probabilities and subscription risk."
    )

    minimum_probability = st.slider(
        "Minimum churn probability (%)",
        min_value=0,
        max_value=100,
        value=20
    )

    filtered = validation[
        validation["churn_probability"] >=
        minimum_probability / 100
    ]

    st.metric(
        "Subscriptions Matching Filter",
        len(filtered)
    )

    st.dataframe(
        filtered[
            [
                "subscription_id",
                "account_id",
                "churn_probability",
                "predicted_churn"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("Churn Probability Distribution")

    probability_chart = validation[
        ["churn_probability"]
    ]

    st.bar_chart(
        probability_chart
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Predictions",
        data=csv_data,
        file_name="filtered_churn_predictions.csv",
        mime="text/csv"
    )


# ==========================================
# 6. FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "SaaSCommand360 | Machine Learning Powered "
    "Subscription Churn Analytics"
)
