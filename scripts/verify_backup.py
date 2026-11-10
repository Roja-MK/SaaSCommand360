
import psycopg2
import csv
from pathlib import Path
from getpass import getpass

BASE_DIR = Path(__file__).resolve().parent.parent

BACKUP_ROOT = BASE_DIR / "backups" / "postgres_backup"

# Find latest backup folder
backup_folders = sorted(
    [p for p in BACKUP_ROOT.iterdir() if p.is_dir()]
)

if not backup_folders:
    raise FileNotFoundError("No backup folder found!")

BACKUP_DIR = backup_folders[-1]

TABLES = [
    "accounts",
    "users",
    "product_events",
    "subscriptions",
    "invoices",
    "support_tickets"
]

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="saascommand360",
    user="postgres",
    password=getpass("Enter PostgreSQL password: ")
)

all_valid = True

try:
    with conn.cursor() as cursor:

        for table in TABLES:

            # Count records in PostgreSQL
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            original_count = cursor.fetchone()[0]

            # Count records in backup CSV
            csv_path = BACKUP_DIR / f"{table}.csv"

            with open(
                csv_path, "r", encoding="utf-8", newline=""
            ) as file:
                backup_count = sum(
                    1 for _ in csv.DictReader(file)
                )

            if original_count == backup_count:
                print(f"PASS: {table} - {backup_count:,} records")
            else:
                all_valid = False
                print(
                    f"FAIL: {table} | "
                    f"Original: {original_count:,} | "
                    f"Backup: {backup_count:,}"
                )

    print("\nBACKUP VERIFICATION:",
          "SUCCESS" if all_valid else "FAILED")

finally:
    conn.close()
