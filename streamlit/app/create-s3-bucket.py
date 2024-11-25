import boto3
import config
from botocore.exceptions import ClientError

def create_s3_bucket(bucket_name, region):
    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.create_bucket(Bucket=bucket_name)

        print(f"Bucket '{bucket_name}' created successfully!")
    except ClientError as e:
        print(f"Error: {e}")
        return False
    return True

bucket_name = config.bucket_name
region = config.region

create_s3_bucket(bucket_name, region)
