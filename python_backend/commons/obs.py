import os, boto3
from botocore.config import Config

def obs_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("OBS_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("OBS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("OBS_SECRET_KEY"),
        region_name=os.getenv("OBS_REGION"),
        config=Config(signature_version="s3v4"),
    )