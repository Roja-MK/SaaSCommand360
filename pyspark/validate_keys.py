
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = (
    BASE_DIR / "backups" / "postgres_backup" / "20261106_103134"
)

TABLES = {
    "accounts": "account_id",
    "users": "user_id",
    "subscriptions": "subscription_id",
    "invoices": "invoice_id",
    "support_tickets": "ticket_id",
    "product_events": "event_id"
}

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SaaSCommand360_KeyValidation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\nPRIMARY KEY VALIDATION")
    print("=" * 55)

    for table, primary_key in TABLES.items():

        file_path = BRONZE_DIR / f"{table}.csv"

        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(str(file_path))
        )

        total_records = df.count()

        null_count = df.filter(
            col(primary_key).isNull()
        ).count()

        duplicate_count = (
            df.groupBy(primary_key)
            .count()
            .filter(col("count") > 1)
            .count()
        )

        print(f"\nTABLE: {table.upper()}")
        print(f"Primary key: {primary_key}")
        print(f"Total records: {total_records:,}")
        print(f"NULL primary keys: {null_count:,}")
        print(f"Duplicate primary keys: {duplicate_count:,}")

        if null_count == 0 and duplicate_count == 0:
            print("RESULT: PRIMARY KEY VALID")
        else:
            print("RESULT: VALIDATION FAILED")

finally:
    spark.stop()
