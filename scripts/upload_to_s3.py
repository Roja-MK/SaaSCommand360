
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv()

# AWS S3 configuration
BUCKET_NAME = (
    os.getenv("S3_BUCKET")
    or os.getenv("AWS_S3_BUCKET")
    or os.getenv("BUCKET_NAME")
)

REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

if not BUCKET_NAME:
    raise ValueError("S3 bucket name not found in .env file")

# Find the latest PostgreSQL backup folder
BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups" / "postgres_backup"

backup_folders = sorted(
    [folder for folder in BACKUP_DIR.iterdir() if folder.is_dir()],
    key=lambda folder: folder.stat().st_mtime,
    reverse=True
)

if not backup_folders:
    raise FileNotFoundError("No PostgreSQL backup folders found")

LATEST_BACKUP = backup_folders[0]

print("Latest backup:", LATEST_BACKUP)

# Connect to S3
s3 = boto3.client("s3", region_name=REGION)

# Upload all CSV files
csv_files = list(LATEST_BACKUP.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV files found in backup folder")

for file_path in csv_files:
    table_name = file_path.stem
    s3_key = f"bronze/{table_name}/{file_path.name}"

    print(f"Uploading: {file_path.name}")

    s3.upload_file(
        str(file_path),
        BUCKET_NAME,
        s3_key
    )

    print(f"Uploaded successfully: s3://{BUCKET_NAME}/{s3_key}")

print("\nALL CSV FILES UPLOADED TO AWS S3 SUCCESSFULLY!")
