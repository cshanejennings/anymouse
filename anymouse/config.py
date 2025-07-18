"""Config loading and validation helpers."""
import json
import boto3
import botocore.exceptions
from pydantic import BaseModel, ValidationError, field_validator
from typing import List

class Config(BaseModel):
    fields: List[str] = []

    @field_validator("fields", mode="before")
    @classmethod
    def check_fields(cls, value):
        if not isinstance(value, list) or not all(isinstance(f, str) for f in value):
            raise ValueError("Fields must be a list of strings")
        return value

def validate_config(config: dict) -> dict:
    """
    Validate and normalize a configuration dictionary.
    
    Args:
        config: Dict with optional 'fields' key (list of field paths).
    
    Returns:
        Validated config dict with 'fields' key (defaults to empty list).
    
    Raises:
        ValueError: If config is invalid (e.g., fields not a list of strings).
    """
    try:
        return Config(**config).model_dump()
    except ValidationError as e:
        raise ValueError(str(e))

def load_config_from_s3(bucket: str, key: str) -> dict:
    """
    Load and validate a configuration from an S3 bucket.
    
    Args:
        bucket: S3 bucket name.
        key: S3 object key (e.g., 'config.json').
    
    Returns:
        Validated config dict.
    
    Raises:
        ValueError: If config is invalid or S3 access fails.
    """
    try:
        s3_client = boto3.client("s3")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        config_data = json.loads(response["Body"].read().decode("utf-8"))
        return validate_config(config_data)
    except (botocore.exceptions.ClientError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to load config from S3: {str(e)}")
