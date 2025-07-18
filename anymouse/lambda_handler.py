"""
AWS Lambda entrypoint for Anymouse anonymization service.
Dispatches requests to anonymize, deanonymize, or test config.
"""
import json
import logging
from .anonymize import anonymize_payload
from .deanonymize import deanonymize_payload
from .config import validate_config, load_config_from_s3

# Configure logging for CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    AWS Lambda handler. Expects event with 'action' key:
      - action: 'anonymize', 'deanonymize', or 'config_test'
      - payload: dict (for anonymize/deanonymize)
      - config: dict (optional for anonymize/deanonymize, required for config_test)
      - config_source: dict with 's3' key containing 'bucket' and 'key' (optional)
      - headers: dict with 'X-API-Key' (required)
    """
    # Check API key
    headers = event.get("headers", {})
    api_key = headers.get("X-API-Key")
    if api_key != "test-api-key-123":  # Hardcoded for testing; use SSM in prod
        logger.info("action=auth_check status=401 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return {"error": "Missing or invalid API key", "statusCode": 401}
    
    # Load config from S3 if specified, else use inline config
    try:
        config_source = event.get("config_source", {})
        if "s3" in config_source:
            config = load_config_from_s3(config_source["s3"]["bucket"], config_source["s3"]["key"])
        else:
            config = validate_config(event.get("config", {}))
    except ValueError as e:
        logger.info("action=config_validation status=400 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return {"error": f"Invalid config: {str(e)}", "statusCode": 400}

    action = event.get("action")
    payload = event.get("payload")
    
    if action == "anonymize":
        response = {"anonymized": anonymize_payload(payload, config), "statusCode": 200}
        logger.info("action=anonymize status=200 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return response
    elif action == "deanonymize":
        response = {"deanonymized": deanonymize_payload(payload, config), "statusCode": 200}
        logger.info("action=deanonymize status=200 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return response
    elif action == "config_test":
        response = {"status": "success", "config": config, "statusCode": 200}
        logger.info("action=config_test status=200 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return response
    else:
        logger.info("action=invalid status=400 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return {"error": "Invalid action", "statusCode": 400}
