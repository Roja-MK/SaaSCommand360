
import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# PostgreSQL configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB", "saascommand360"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD")
}

if not DB_CONFIG["password"]:
    raise ValueError("POSTGRES_PASSWORD is missing from .env")

# Create timestamped backup folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = BASE_DIR / "backups" / "postgres_backup" / timestamp
BACKUP_DIR.mkdir(parents=True, exist_ok=False)

TABLES = [
    "accounts",
    "users",
    "product_events",
    "subscriptions",
    "invoices",
    "support_tickets"
]

manifest = []

try:
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        conn.set_session(readonly=True)

        with conn.cursor() as cursor:
            for table in TABLES:
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                        sql.Identifier("public"),
                        sql.Identifier(table)
                    )
                )

                original_count = cursor.fetchone()[0]
                file_path = BACKUP_DIR / f"{table}.csv"

                copy_query = sql.SQL(
                    "COPY {}.{} TO STDOUT WITH (FORMAT CSV, HEADER TRUE)"
                ).format(
                    sql.Identifier("public"),
                    sql.Identifier(table)
                )

                with open(file_path, "w", encoding="utf-8", newline="") as file:
                    cursor.copy_expert(copy_query.as_string(conn), file)

                manifest.append(
                    f"{table}: {original_count:,} records"
                )

                print(
                    f"BACKUP COMPLETED: {table} - "
                    f"{original_count:,} records"
                )

        with open(
            BACKUP_DIR / "backup_manifest.txt",
            "w",
            encoding="utf-8"
        ) as file:
            file.write("SAASCOMMAND360 DATABASE BACKUP\n")
            file.write(f"Created: {datetime.now()}\n\n")
            file.write("\n".join(manifest))

    finally:
        conn.close()

    print("\nALL BACKUPS COMPLETED SUCCESSFULLY!")
    print(f"Backup location: {BACKUP_DIR}")

    # Return path for Prefect orchestration
    print(f"BACKUP_PATH={BACKUP_DIR}")

except Exception:
    print("DATABASE BACKUP FAILED!", file=sys.stderr)
    raise
