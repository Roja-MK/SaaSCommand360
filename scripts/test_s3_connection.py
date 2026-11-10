
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load AWS credentials
load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Connect to AWS S3
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)

try:
    # Check bucket access
    response = s3.head_bucket(Bucket=BUCKET_NAME)

    print("AWS S3 CONNECTION SUCCESSFUL!")
    print("Bucket Name:", BUCKET_NAME)
    print("Region:", AWS_REGION)

except ClientError as e:
    print("AWS S3 CONNECTION FAILED!")
    print(e.response["Error"])
