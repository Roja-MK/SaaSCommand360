
import psycopg2
import pandas as pd
from getpass import getpass
from pathlib import Path
import time

# --------------------------------
# 1. DATABASE CONNECTION
# --------------------------------

print("Connecting to SaaSCommand360 development database...", flush=True)

password = getpass("Enter PostgreSQL password: ")

connection = None

try:
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="saascommand360_dev",
        user="postgres",
        password=password
    )

    print("Database connected successfully!", flush=True)

    # --------------------------------
    # 2. FEATURE ENGINEERING QUERY
    # --------------------------------

    query = """
    SELECT
        s.subscription_id,
        s.account_id,
        a.industry,
        a.size AS company_size,
        a.region,
        s.plan,
        s.billing_cycle,
        (DATE '2026-05-10' - s.start_date) AS tenure_days,

        COALESCE(inv.invoice_count, 0) AS invoice_count,
        COALESCE(inv.total_invoice_amount, 0) AS total_invoice_amount,
        COALESCE(inv.paid_invoice_count, 0) AS paid_invoice_count,
        COALESCE(inv.overdue_invoice_count, 0) AS overdue_invoice_count,
        COALESCE(inv.failed_invoice_count, 0) AS failed_invoice_count,

        COALESCE(tickets.ticket_count, 0) AS ticket_count,
        COALESCE(tickets.open_ticket_count, 0) AS open_ticket_count,
        COALESCE(tickets.critical_ticket_count, 0) AS critical_ticket_count,

        COALESCE(usage.product_event_count, 0) AS product_event_count,
        COALESCE(usage.distinct_features_used, 0) AS distinct_features_used,

        CASE
            WHEN s.status = 'Cancelled'
             AND s.end_date > DATE '2026-05-10'
             AND s.end_date <= DATE '2026-11-10'
            THEN 1
            ELSE 0
        END AS churn

    FROM subscriptions s
    JOIN accounts a ON s.account_id = a.account_id

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS invoice_count,
            COALESCE(SUM(i.amount), 0) AS total_invoice_amount,
            COUNT(*) FILTER (WHERE i.status = 'Paid') AS paid_invoice_count,
            COUNT(*) FILTER (WHERE i.status = 'Overdue') AS overdue_invoice_count,
            COUNT(*) FILTER (WHERE i.status = 'Failed') AS failed_invoice_count
        FROM invoices i
        WHERE i.subscription_id = s.subscription_id
          AND i.invoice_date < DATE '2026-05-11'
    ) inv ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS ticket_count,
            COUNT(*) FILTER (
                WHERE t.status IN ('Open', 'In Progress')
            ) AS open_ticket_count,
            COUNT(*) FILTER (
                WHERE t.severity = 'Critical'
            ) AS critical_ticket_count
        FROM support_tickets t
        WHERE t.account_id = s.account_id
          AND t.created_at < TIMESTAMP '2026-05-11 00:00:00'
    ) tickets ON TRUE

    LEFT JOIN LATERAL (
        SELECT
            COUNT(*) AS product_event_count,
            COUNT(DISTINCT pe.feature) AS distinct_features_used
        FROM users u
        JOIN product_events pe ON pe.user_id = u.user_id
        WHERE u.account_id = s.account_id
          AND pe.event_timestamp < TIMESTAMP '2026-05-11 00:00:00'
    ) usage ON TRUE

    WHERE s.start_date <= DATE '2026-05-10'
      AND (
          s.status <> 'Cancelled'
          OR s.end_date > DATE '2026-05-10'
      )

    ORDER BY s.subscription_id;
    """

    # --------------------------------
    # 3. EXECUTE QUERY
    # --------------------------------

    cursor = connection.cursor()

    print("\nExecuting feature extraction query...", flush=True)

    start_time = time.time()
    cursor.execute(query)

    print(
        f"Query execution completed in {time.time() - start_time:.2f} seconds",
        flush=True
    )

    print("Fetching records...", flush=True)

    fetch_start = time.time()
    records = cursor.fetchall()

    print(
        f"Fetched {len(records)} records in {time.time() - fetch_start:.2f} seconds",
        flush=True
    )

    columns = [description[0] for description in cursor.description]

    df = pd.DataFrame(records, columns=columns)

    cursor.close()
    connection.close()

    # --------------------------------
    # 4. SAVE FEATURE DATASET
    # --------------------------------

    print("\nFeature extraction completed!")

    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "subscription_churn_features.csv"

    df.to_csv(output_file, index=False)

    # --------------------------------
    # 5. DISPLAY RESULTS
    # --------------------------------

    print("\nDataset shape:", df.shape)

    print("\nChurn distribution:")
    print(df["churn"].value_counts())

    print("\nDataset preview:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDataset saved successfully:")
    print(output_file)

except Exception as error:

    print("\nFeature engineering failed!")
    print(error)

finally:
    if connection is not None and not connection.closed:
        connection.close()
