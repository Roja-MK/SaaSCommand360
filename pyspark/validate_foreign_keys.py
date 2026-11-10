
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
    .appName("SaaSCommand360_ForeignKeyValidation")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


def load_table(table_name):
    file_path = BRONZE_DIR / f"{table_name}.csv"

    return (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(file_path))
    )


try:
    print("\nFOREIGN KEY VALIDATION")
    print("=" * 60)

    # Load all required tables
    accounts = load_table("accounts")
    users = load_table("users")
    subscriptions = load_table("subscriptions")
    invoices = load_table("invoices")
    tickets = load_table("support_tickets")
    events = load_table("product_events")

    # Child table, child column, parent table, parent column
    relationships = [
        ("USERS", users, "account_id", "ACCOUNTS", accounts, "account_id"),
        ("SUBSCRIPTIONS", subscriptions, "account_id", "ACCOUNTS", accounts, "account_id"),
        ("INVOICES", invoices, "account_id", "ACCOUNTS", accounts, "account_id"),
        ("INVOICES", invoices, "subscription_id", "SUBSCRIPTIONS", subscriptions, "subscription_id"),
        ("SUPPORT_TICKETS", tickets, "account_id", "ACCOUNTS", accounts, "account_id"),
        ("PRODUCT_EVENTS", events, "user_id", "USERS", users, "user_id")
    ]

    for child_name, child_df, child_col, parent_name, parent_df, parent_col in relationships:

        # Count missing foreign keys
        null_count = child_df.filter(
            col(child_col).isNull()
        ).count()

        # Find references that do not exist in the parent table
        child_keys = (
            child_df
            .filter(col(child_col).isNotNull())
            .select(col(child_col))
            .distinct()
        )

        parent_keys = (
            parent_df
            .filter(col(parent_col).isNotNull())
            .select(col(parent_col))
            .distinct()
        )

        orphan_count = (
            child_keys
            .join(
                parent_keys,
                child_keys[child_col] == parent_keys[parent_col],
                "left_anti"
            )
            .count()
        )

        print(f"\n{child_name}.{child_col} -> {parent_name}.{parent_col}")
        print(f"NULL foreign keys: {null_count:,}")
        print(f"Unmatched references: {orphan_count:,}")

        if null_count == 0 and orphan_count == 0:
            print("RESULT: FOREIGN KEY VALID")
        else:
            print("RESULT: VALIDATION NEEDS REVIEW")

finally:
    spark.stop()

print("\nFOREIGN KEY VALIDATION COMPLETED!")
