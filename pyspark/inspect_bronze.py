
from pathlib import Path
from pyspark.sql import SparkSession

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = (
    BASE_DIR
    / "backups"
    / "postgres_backup"
    / "20261106_103134"
)

TABLES = [
    "accounts",
    "users",
    "subscriptions",
    "invoices",
    "support_tickets",
    "product_events"
]

# ==========================================
# 2. CREATE SPARK SESSION
# ==========================================

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SaaSCommand360_BronzeInspection")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("\n" + "=" * 60)
print("SAASCOMMAND360 - BRONZE DATA INSPECTION")
print("=" * 60)

# ==========================================
# 3. INSPECT ALL SIX TABLES
# ==========================================

try:

    for table in TABLES:

        print("\n" + "=" * 60)
        print(f"TABLE: {table.upper()}")
        print("=" * 60)

        file_path = BRONZE_DIR / f"{table}.csv"

        # Check whether CSV exists
        if not file_path.exists():
            print(f"ERROR: File not found - {file_path}")
            continue

        print(f"\nFile: {file_path.name}")

        # Read CSV using Spark
        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .option("mode", "PERMISSIVE")
            .csv(str(file_path))
        )

        # --------------------------------------
        # COLUMN NAMES
        # --------------------------------------

        print("\n1. COLUMN NAMES")

        for column in df.columns:
            print(f"- {column}")

        # --------------------------------------
        # DATA TYPES
        # --------------------------------------

        print("\n2. DATA TYPES")

        df.printSchema()

        # --------------------------------------
        # TOTAL RECORD COUNT
        # --------------------------------------

        print("\n3. TOTAL RECORDS")

        total_records = df.count()

        print(f"Total records: {total_records:,}")

        # --------------------------------------
        # SAMPLE RECORDS
        # --------------------------------------

        print("\n4. SAMPLE RECORDS")

        df.show(5, truncate=False)

        # --------------------------------------
        # NULL VALUE COUNTS
        # --------------------------------------

        print("\n5. NULL VALUE COUNTS")

        from pyspark.sql.functions import col, sum as spark_sum, when

        null_counts = df.select(
            [
                spark_sum(
                    when(
                        col(column).isNull(),
                        1
                    ).otherwise(0)
                ).alias(column)
                for column in df.columns
            ]
        )

        null_counts.show(truncate=False)

        # --------------------------------------
        # DUPLICATE RECORD COUNT
        # --------------------------------------

        print("\n6. DUPLICATE RECORDS")

        duplicate_count = (
            total_records - df.dropDuplicates().count()
        )

        print(f"Duplicate records: {duplicate_count:,}")

        print(f"\nINSPECTION COMPLETED: {table.upper()}")

# ==========================================
# 4. STOP SPARK SESSION
# ==========================================

finally:

    spark.stop()

print("\n" + "=" * 60)
print("ALL BRONZE TABLES INSPECTED SUCCESSFULLY!")
print("=" * 60)

