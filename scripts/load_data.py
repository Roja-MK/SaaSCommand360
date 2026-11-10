
import psycopg2
from getpass import getpass
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "dev" / "raw"

# PostgreSQL connection
password = getpass("Enter PostgreSQL password: ")

connection = None

# Load parent tables before child tables
datasets = [
    {
        "file": "accounts.csv",
        "table": "accounts",
        "columns": "account_id, company_name, industry, size, region, owner"
    },
    {
        "file": "users.csv",
        "table": "users",
        "columns": "user_id, account_id, role, created_at"
    },
    {
        "file": "subscriptions.csv",
        "table": "subscriptions",
        "columns": "subscription_id, account_id, plan, start_date, end_date, billing_cycle, status"
    },
    {
        "file": "product_events.csv",
        "table": "product_events",
        "columns": "event_id, user_id, feature, event_timestamp"
    },
    {
        "file": "invoices.csv",
        "table": "invoices",
        "columns": "invoice_id, account_id, subscription_id, amount, invoice_date, due_date, paid_date, status"
    },
    {
        "file": "support.csv",
        "table": "support_tickets",
        "columns": "ticket_id, account_id, severity, status, created_at, resolved_at"
    }
]

try:
    print("\nConnecting to PostgreSQL...")

    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="saascommand360_dev",
        user="postgres",
        password=password
    )

    cursor = connection.cursor()

    print("\nStarting CSV data loading...\n")

    total_records = 0

    for dataset in datasets:

        file_path = DATA_DIR / dataset["file"]

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Loading {dataset['file']}...")

        copy_sql = f"""
            COPY {dataset['table']} ({dataset['columns']})
            FROM STDIN
            WITH (
                FORMAT CSV,
                HEADER TRUE,
                NULL ''
            );
        """

        with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
            cursor.copy_expert(copy_sql, csv_file)

        loaded_rows = cursor.rowcount
        total_records += loaded_rows

        print(f"Loaded {loaded_rows:,} records into {dataset['table']}")

    connection.commit()

    print("\n" + "=" * 55)
    print(f"TOTAL RECORDS LOADED: {total_records:,}")
    print("All datasets loaded successfully!")
    print("=" * 55)

except Exception as error:

    if connection:
        connection.rollback()

    print("\nDATA LOADING FAILED!")
    print(error)
    print("Database transaction rolled back.")

finally:

    if connection:
        connection.close()
        print("\nPostgreSQL connection closed.")
