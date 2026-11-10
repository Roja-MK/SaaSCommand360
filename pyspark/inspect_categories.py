
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import desc

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = (
    BASE_DIR / "backups" / "postgres_backup" / "20261106_103134"
)

TABLE_COLUMNS = {
    "accounts": ["industry", "size", "region"],
    "users": ["role"],
    "subscriptions": ["plan", "billing_cycle", "status"],
    "invoices": ["status"],
    "support_tickets": ["severity", "status"],
    "product_events": ["feature"]
}

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SaaSCommand360_CategoryInspection")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\nCATEGORICAL VALUE INSPECTION")
    print("=" * 60)

    for table, columns in TABLE_COLUMNS.items():

        file_path = BRONZE_DIR / f"{table}.csv"

        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(str(file_path))
        )

        for column in columns:

            print("\n" + "-" * 50)
            print(f"TABLE: {table.upper()}")
            print(f"COLUMN: {column}")

            print("Distinct values and record counts:")

            (
                df.groupBy(column)
                .count()
                .orderBy(desc("count"))
                .show(50, truncate=False)
            )

finally:
    spark.stop()

print("\nCATEGORY INSPECTION COMPLETED!")
