
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = (
    BASE_DIR / "backups" / "postgres_backup" / "20261106_103134"
)

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SaaSCommand360_BusinessRuleValidation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


def load_table(name):
    return (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(BRONZE_DIR / f"{name}.csv"))
    )


def check_rule(description, df, condition):
    invalid_count = df.filter(condition).count()

    print(f"\n{description}")
    print(f"Invalid records: {invalid_count:,}")

    if invalid_count == 0:
        print("RESULT: PASSED")
    else:
        print("RESULT: NEEDS REVIEW")


try:
    print("\nBUSINESS RULE VALIDATION")
    print("=" * 60)

    # Load required tables
    subscriptions = load_table("subscriptions")
    invoices = load_table("invoices")
    tickets = load_table("support_tickets")

    # 1. Subscription end date must not be before start date.
    check_rule(
        "SUBSCRIPTIONS: End date before start date",
        subscriptions,
        col("end_date").isNotNull() &
        (col("end_date") < col("start_date"))
    )

    # 2. Invoice amount should not be negative.
    check_rule(
        "INVOICES: Negative invoice amount",
        invoices,
        col("amount") < 0
    )

    # 3. Invoice due date must not be before invoice date.
    check_rule(
        "INVOICES: Due date before invoice date",
        invoices,
        col("due_date") < col("invoice_date")
    )

    # 4. Payment date must not be before invoice date.
    check_rule(
        "INVOICES: Paid date before invoice date",
        invoices,
        col("paid_date").isNotNull() &
        (col("paid_date") < col("invoice_date"))
    )

    # 5. Ticket resolution must not be before creation.
    check_rule(
        "SUPPORT_TICKETS: Resolution before creation",
        tickets,
        col("resolved_at").isNotNull() &
        (col("resolved_at") < col("created_at"))
    )

finally:
    spark.stop()

print("\nBUSINESS RULE VALIDATION COMPLETED!")
