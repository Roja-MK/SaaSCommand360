
import csv
from pathlib import Path

# Get project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Location of generated CSV files
DATA_DIR = BASE_DIR / "data" / "raw"

# Expected record counts
expected_counts = {
    "accounts.csv": 2000,
    "users.csv": 5000,
    "product_events.csv": 2000000,
    "subscriptions.csv": 3000,
    "invoices.csv": 30000,
    "support.csv": 10000
}

print("\nSAASCOMMAND360 DATA VALIDATION")
print("=" * 65)

total_records = 0
all_passed = True

for filename, expected in expected_counts.items():

    file_path = DATA_DIR / filename

    # Check whether file exists
    if not file_path.exists():
        print(f"{filename}: FILE MISSING")
        all_passed = False
        continue

    # Count records without loading the entire CSV into memory
    with open(file_path, "r", newline="", encoding="utf-8") as file:

        reader = csv.reader(file)

        next(reader, None)  # Skip column headers

        actual = sum(1 for row in reader)

    total_records += actual

    # Compare actual and expected records
    if actual == expected:
        status = "PASS"
    else:
        status = "FAIL"
        all_passed = False

    print(
        f"{filename:<22} "
        f"Expected: {expected:>10,} | "
        f"Actual: {actual:>10,} | {status}"
    )

print("=" * 65)

print(f"Total Records: {total_records:,}")

if all_passed:
    print("\nAll datasets passed validation!")
else:
    print("\nSome datasets need attention.")
