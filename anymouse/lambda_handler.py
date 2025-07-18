"""
AWS Lambda entrypoint for Anymouse anonymization service.
Dispatches requests to anonymize or deanonymize functions.
"""
import json
import logging
from .anonymize import anonymize_payload
from .deanonymize import deanonymize_payload
from .config import validate_config

# Configure logging for CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    AWS Lambda handler. Expects event with 'action' key:
      - action: 'anonymize' or 'deanonymize'
      - payload: dict
      - config: dict (optional)
      - headers: dict with 'X-API-Key' (required)
    """
    # Check API key
    headers = event.get("headers", {})
    api_key = headers.get("X-API-Key")
    if api_key != "test-api-key-123":  # Hardcoded for testing; use SSM in prod
        logger.info("action=auth_check status=401 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return {"error": "Missing or invalid API key", "statusCode": 401}
    
    # Validate config
    try:
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
    else:
        logger.info("action=invalid status=400 source_ip=%s", event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return {"error": "Invalid action", "statusCode": 400}
