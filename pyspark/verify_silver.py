
from pathlib import Path
import pyarrow.parquet as pq

BASE_DIR = Path(__file__).resolve().parent.parent
SILVER_DIR = BASE_DIR / "data" / "dev" / "silver"

EXPECTED_COUNTS = {
    "accounts": 500,
    "users": 1000,
    "subscriptions": 500,
    "invoices": 2000,
    "support_tickets": 1000,
    "product_events": 5000
}

total_records = 0

print("\nSAASCOMMAND360 - SILVER VALIDATION")
print("=" * 55)

for table, expected_count in EXPECTED_COUNTS.items():

    parquet_file = SILVER_DIR / table / f"{table}.parquet"

    if not parquet_file.exists():
        raise FileNotFoundError(
            f"Missing Parquet file: {parquet_file}"
        )

    actual_count = pq.read_metadata(parquet_file).num_rows

    status = "PASS" if actual_count == expected_count else "FAIL"

    print(
        f"{table:20} | "
        f"Expected: {expected_count:6,} | "
        f"Actual: {actual_count:6,} | "
        f"{status}"
    )

    if actual_count != expected_count:
        raise ValueError(f"Record count mismatch in {table}")

    total_records += actual_count

print("=" * 55)
print(f"TOTAL VERIFIED RECORDS: {total_records:,}")
print("ALL SILVER FILES VALIDATED SUCCESSFULLY!")
