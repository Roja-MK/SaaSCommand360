
import duckdb
import os

SILVER_PATH = "data/silver"

con = duckdb.connect("saascommand360.duckdb")

print("\n========== SILVER LAYER INSPECTION ==========\n")

for root, dirs, files in os.walk(SILVER_PATH):
    for file in files:
        if file.endswith(".parquet"):
            file_path = os.path.join(root, file)

            print(f"\nTABLE FILE: {file}")

            result = con.execute(
                f"SELECT COUNT(*) FROM read_parquet('{file_path}')"
            ).fetchone()

            print("Total Records:", result[0])

            schema = con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{file_path}')"
            ).fetchall()

            print("Columns:")
            for column in schema:
                print(" -", column[0], ":", column[1])

con.close()

print("\n========== INSPECTION COMPLETED ==========")
