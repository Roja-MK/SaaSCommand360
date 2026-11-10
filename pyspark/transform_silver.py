
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from pyspark.sql import SparkSession
from pyspark.sql.functions import trim, col
from pyspark.sql.types import StringType


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Receive Bronze folder path
if len(sys.argv) < 2:
    raise ValueError(
        "Please provide the Bronze folder path."
    )

BRONZE_DIR = Path(sys.argv[1]).resolve()

if not BRONZE_DIR.is_dir():
    raise FileNotFoundError(
        f"Bronze folder not found: {BRONZE_DIR}"
    )

# Silver output directory for 10K dataset
SILVER_DIR = BASE_DIR / "data" / "dev" / "silver"

# Map database table names to CSV filenames
TABLES = {
    "accounts": "accounts.csv",
    "users": "users.csv",
    "subscriptions": "subscriptions.csv",
    "invoices": "invoices.csv",
    "support_tickets": "support_tickets.csv",
    "product_events": "product_events.csv"
}

# Start Spark
spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("SaaSCommand360_Dev_Silver_Transformation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\nSAASCOMMAND360 - DEV SILVER LAYER")
    print("=" * 60)
    print(f"Bronze source: {BRONZE_DIR}")
    print(f"Silver output: {SILVER_DIR}")

    for table, csv_file in TABLES.items():

        print(f"\nProcessing: {table.upper()}")

        input_path = BRONZE_DIR / csv_file
        output_path = SILVER_DIR / table

        if not input_path.exists():
            raise FileNotFoundError(
                f"Bronze file missing: {input_path}"
            )

        # Read Bronze CSV
        df = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(str(input_path))
        )

        bronze_count = df.count()
        print(f"Bronze records: {bronze_count:,}")

        # Trim whitespace from string columns
        for field in df.schema.fields:
            if isinstance(field.dataType, StringType):
                df = df.withColumn(
                    field.name,
                    trim(col(field.name))
                )

        silver_count = df.count()
        print(f"Silver records: {silver_count:,}")

        # Validate record counts
        if bronze_count != silver_count:
            raise ValueError(
                f"Record count mismatch for {table}: "
                f"Bronze={bronze_count}, Silver={silver_count}"
            )

        # Convert to Parquet
        pandas_df = df.toPandas()

        arrow_table = pa.Table.from_pandas(
            pandas_df,
            preserve_index=False
        )

        output_path.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = output_path / f"{table}.parquet"

        pq.write_table(
            arrow_table,
            output_file,
            compression="snappy"
        )

        print(f"Silver file created: {output_file}")

    print("\nALL SIX DEV SILVER TABLES CREATED SUCCESSFULLY!")

finally:
    spark.stop()
