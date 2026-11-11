# SaaSCommand360 – End-to-End SaaS Analytics Data Engineering Pipeline

## Project Overview

SaaSCommand360 is an end-to-end data engineering project designed to build a local analytics pipeline for a SaaS business.

The pipeline generates sample SaaS business data, stores it in PostgreSQL, creates backups, transforms raw data into optimized Parquet files using PySpark, and builds analytical models using dbt Core and DuckDB. Prefect orchestrates the complete workflow.

The project demonstrates data ingestion, transformation, data quality validation, analytical modelling, and workflow orchestration.

## Architecture

```text
Python + Faker
      |
      v
10,000 Sample Records
      |
      v
PostgreSQL (Development Database)
      |
      v
Timestamped Database Backup
      |
      v
PySpark Transformation
      |
      v
Silver Layer (Parquet)
      |
      v
DuckDB
      |
      v
dbt Core – Gold Layer
      |
      v
Dimensions + Facts + Analytics Marts
      |
      v
Data Quality Tests

Prefect orchestrates the workflow.
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and pipeline scripts |
| Faker | Synthetic SaaS data generation |
| Pandas | Data processing |
| PostgreSQL | Relational database and data storage |
| PySpark | Data transformation |
| Parquet | Columnar data storage |
| DuckDB | Local analytical database |
| dbt Core | Data modelling and testing |
| Prefect | Workflow orchestration |
| Git | Version control |

## Dataset

The project uses 10,000 synthetic records across six datasets.

| Dataset | Records |
|---|---:|
| Accounts | 500 |
| Users | 1,000 |
| Subscriptions | 500 |
| Invoices | 2,000 |
| Support Tickets | 1,000 |
| Product Events | 5,000 |
| **Total** | **10,000** |

Referential integrity is maintained through primary key and foreign key relationships.

## Data Pipeline Layers

### 1. Data Generation

Python and Faker generate realistic synthetic SaaS business data.

The generated CSV files are stored in:

`data/dev/raw/`

### 2. PostgreSQL – Bronze Layer

The generated datasets are loaded into the PostgreSQL development database.

Database: `saascommand360_dev`

The database contains six related tables with primary key and foreign key constraints.

### 3. Backup

The pipeline creates timestamped backups of all six PostgreSQL tables.

Backup location:

`backups/postgres_backup/`

### 4. PySpark – Silver Layer

PySpark processes the backed-up CSV files.

Transformations include:
- Reading source CSV files.
- Cleaning string values.
- Processing datasets.
- Validating record counts.
- Converting data into Parquet format.

Output location:

`data/dev/silver/`

### 5. DuckDB and dbt – Gold Layer

DuckDB provides local analytical storage, while dbt builds the Gold-layer models.

**Staging models**
- stg_accounts
- stg_users
- stg_subscriptions
- stg_invoices
- stg_support_tickets
- stg_product_events

**Dimension models**
- dim_accounts
- dim_subscriptions
- dim_users

**Fact models**
- fact_invoices
- fact_product_events
- fact_support_tickets

**Analytics marts**
- mart_customer_overview
- mart_product_usage
- mart_revenue_overview
- mart_subscription_overview
- mart_support_overview

### 6. Prefect – Workflow Orchestration

Prefect coordinates the pipeline in the following order:

1. PostgreSQL backup.
2. PySpark Silver transformation.
3. dbt model execution.
4. dbt data quality testing.

Task retries are configured to handle execution failures.

## Project Structure

```text
SaaSCommand360/
|
|-- data/
|   |-- raw/
|   |-- silver/
|   |-- processed/
|   \-- dev/
|       |-- raw/
|       \-- silver/
|
|-- scripts/
|   |-- generate_data.py
|   |-- load_data.py
|   |-- export_backup.py
|   |-- validate_data.py
|   \-- other utility scripts
|
|-- pyspark/
|   |-- transform_silver.py
|   \-- verify_silver.py
|
|-- dbt_gold/
|   |-- models/
|   |   |-- staging/
|   |   \-- gold/
|   |       |-- dimensions/
|   |       |-- facts/
|   |       \-- marts/
|   |-- dbt_project.yml
|   \-- profiles.yml (stored separately)
|
|-- orchestration/
|   \-- saascommand360_flow.py
|
|-- duckdb/
|-- sql/
|-- backups/
|-- requirements.txt
|-- .gitignore
\-- README.md
```

## Setup and Execution

### Prerequisites

- Python 3.13.7
- PostgreSQL
- Git
- Windows 11 or compatible environment

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SaaSCommand360
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

Configure your PostgreSQL connection details:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=saascommand360_dev
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

Use your own local PostgreSQL credentials. Never commit `.env` to GitHub.

### 5. Generate sample data

```powershell
python .\scripts\generate_data.py
```

### 6. Load data into PostgreSQL

First create the development database and its required tables using the project database schema.

Then execute:

```powershell
python .\scripts\load_data.py
```

### 7. Run the complete pipeline

From the project root:

```powershell
.\venv\Scripts\python.exe .\orchestration\saascommand360_flow.py
```

Prefect executes the backup, Silver transformation, dbt modelling, and testing tasks.

### 8. Verify Silver data

```powershell
.\venv\Scripts\python.exe .\pyspark\verify_silver.py
```

### 9. Run dbt independently

```powershell
cd .\dbt_gold
dbt debug
dbt run
dbt test
```

## Validation Results

The development pipeline has been successfully executed and validated.

- 10,000 synthetic records generated.
- Six PostgreSQL tables loaded.
- All six datasets backed up.
- Silver Parquet files validated.
- Eleven Gold models built.
- dbt data tests completed successfully.
- Prefect workflow completed successfully.

## Key Learning Outcomes

- Building an end-to-end data engineering pipeline.
- Generating and managing relational datasets.
- Working with PostgreSQL constraints and database backups.
- Transforming CSV data into Parquet using PySpark.
- Building analytical data models using dbt.
- Querying analytical data using DuckDB.
- Orchestrating multi-step workflows using Prefect.
- Implementing data validation and quality checks.

## Machine Learning – Customer Churn Prediction

SaaSCommand360 also includes a machine learning workflow to identify SaaS subscriptions that may be at risk of customer churn.

### Churn Prediction Workflow

1. Extract subscription, invoice, support ticket, and product usage features.
2. Engineer additional features such as overdue invoice ratio and open ticket ratio.
3. Prepare the dataset for machine learning.
4. Split training and testing data using account-level grouping to prevent account overlap.
5. Train and compare classification models.
6. Evaluate models using precision, recall, F1-score, ROC-AUC, and PR-AUC.
7. Save the selected model and generate churn predictions.

### Machine Learning Models

- Dummy Classifier
- Logistic Regression
- Random Forest

Logistic Regression is the provisional selection for recall-oriented churn detection.

The model evaluation uses a separate holdout dataset. Current results indicate that further model improvement is needed, particularly to reduce false positives.

### Model Evaluation

The model evaluation includes:

- Confusion matrices
- ROC curves
- Precision-recall curves
- Feature importance analysis
- Model performance comparison

Generated reports and visualizations are stored in:

- `ml/reports/`
- `ml/plots/`
- `ml/data/`

### Streamlit Dashboard

An interactive Streamlit dashboard provides five sections:

1. Overview
2. Churn Analysis
3. Model Performance
4. Feature Importance
5. Prediction Details

To launch the dashboard:

```powershell
python -m streamlit run dashboard/app.py
```

### Important Evaluation Note

Predictions generated for the historical feature dataset are in-sample predictions. They should not be confused with independent holdout evaluation results.

## Future Enhancements

## Future Enhancements

- Improve churn prediction performance and reduce false positives.
- Generate predictions for new subscription records.
- Add more advanced data quality checks.
- Implement incremental data processing.
- Add pipeline monitoring and failure notifications.
- Improve analytical marts with additional SaaS business KPIs.

## Author

**Abhilash M S**

Data Engineering | Python | SQL | PostgreSQL | PySpark | dbt | DuckDB | Prefect
