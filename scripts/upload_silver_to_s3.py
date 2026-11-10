
import os
import boto3

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
SILVER_DIR = BASE_DIR / "data" / "silver"

load_dotenv(BASE_DIR / ".env")

BUCKET_NAME = os.getenv("S3_BUCKET")
REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

if not BUCKET_NAME:
    raise ValueError("S3_BUCKET is missing from .env")

s3 = boto3.client("s3", region_name=REGION)

print("\nSAASCOMMAND360 - SILVER S3 UPLOAD")
print("=" * 60)

files = list(SILVER_DIR.rglob("*.parquet"))

if len(files) != 6:
    raise ValueError(f"Expected 6 Parquet files, found {len(files)}")

for file_path in files:
    table_name = file_path.parent.name
    s3_key = f"silver/{table_name}/{file_path.name}"

    print(f"\nUploading: {table_name}")

    s3.upload_file(str(file_path), BUCKET_NAME, s3_key)

    response = s3.head_object(
        Bucket=BUCKET_NAME,
        Key=s3_key
    )

    print(f"S3 Location: s3://{BUCKET_NAME}/{s3_key}")
    print(f"Uploaded Size: {response['ContentLength']} bytes")
    print("RESULT: SUCCESS")

print("\n" + "=" * 60)
print("ALL SIX SILVER FILES UPLOADED SUCCESSFULLY!")

