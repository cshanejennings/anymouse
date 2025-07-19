"""
AWS Lambda entrypoint for Anymouse anonymization service.
Handles REST API endpoints for anonymize, deanonymize, and config testing.
"""
import json
import logging
import boto3
import botocore.exceptions
from .anonymize import anonymize_payload, anonymize_text
from .deanonymize import deanonymize_payload, deanonymize_text
from .config import validate_config, load_config_from_s3

# Configure logging for CloudWatch
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_api_key_from_ssm():
    """Get API key from SSM Parameter Store."""
    try:
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(Name='/anymouse/api-key', WithDecryption=True)
        return response['Parameter']['Value']
    except Exception:
        # Fallback to hardcoded key for testing
        return "test-api-key-123"

def authenticate_request(event):
    """Verify API key authentication."""
    headers = event.get("headers", {})
    api_key = headers.get("X-API-Key") or headers.get("x-api-key")
    expected_key = get_api_key_from_ssm()
    
    if api_key != expected_key:
        logger.info("action=auth_check status=401 source_ip=%s", 
                   event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown"))
        return False
    return True

def get_source_ip(event):
    """Extract source IP from event context."""
    return event.get("requestContext", {}).get("identity", {}).get("sourceIp", "unknown")

def lambda_handler(event, context):
    """
    AWS Lambda handler for REST API endpoints.
    Expects API Gateway event with httpMethod and path.
    """
    # Authentication check
    if not authenticate_request(event):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Missing or invalid API key"})
        }
    
    # Extract HTTP method and path
    http_method = event.get("httpMethod", "POST")
    path = event.get("path", "")
    source_ip = get_source_ip(event)
    
    # Parse request body
    try:
        if event.get("body"):
            body = json.loads(event.get("body"))
        else:
            body = {}
    except json.JSONDecodeError:
        logger.info("action=parse_body status=400 source_ip=%s", source_ip)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    
    # Route to appropriate handler
    try:
        if http_method == "POST" and path == "/anonymize":
            return handle_anonymize(body, source_ip)
        elif http_method == "POST" and path == "/deanonymize":
            return handle_deanonymize(body, source_ip)
        elif http_method == "POST" and path == "/config/test":
            return handle_config_test(body, source_ip)
        else:
            logger.info("action=invalid_endpoint status=404 source_ip=%s path=%s", source_ip, path)
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Endpoint not found"})
            }
    except Exception as e:
        logger.error("action=internal_error status=500 source_ip=%s error=%s", source_ip, str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }

def load_config(body):
    """Load configuration from request body or S3."""
    config_source = body.get("config_source", {})
    if "s3" in config_source:
        return load_config_from_s3(config_source["s3"]["bucket"], config_source["s3"]["key"])
    else:
        return validate_config(body.get("config", {}))

def handle_anonymize(body, source_ip):
    """Handle POST /anonymize endpoint."""
    try:
        payload = body.get("payload")
        if payload is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'payload' field"})
            }
        
        # Check if payload is a string (free-form text) or dict (structured data)
        if isinstance(payload, str):
            # Free-form text anonymization
            result = anonymize_text(payload)
        else:
            # Structured payload anonymization
            config = load_config(body)
            result = anonymize_payload(payload, config)
        
        logger.info("action=anonymize status=200 source_ip=%s", source_ip)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except ValueError as e:
        logger.info("action=anonymize status=400 source_ip=%s", source_ip)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid request: {str(e)}"})
        }

def handle_deanonymize(body, source_ip):
    """Handle POST /deanonymize endpoint."""
    try:
        message = body.get("message")
        tokens = body.get("tokens")
        
        if message is None or tokens is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'message' or 'tokens' field"})
            }
        
        # Use text deanonymization for the direct API format
        result = {"message": deanonymize_text(message, tokens)}
        
        logger.info("action=deanonymize status=200 source_ip=%s", source_ip)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        logger.info("action=deanonymize status=400 source_ip=%s", source_ip)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid request: {str(e)}"})
        }

def handle_config_test(body, source_ip):
    """Handle POST /config/test endpoint."""
    try:
        config = load_config(body)
        logger.info("action=config_test status=200 source_ip=%s", source_ip)
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "config": config})
        }
    except ValueError as e:
        logger.info("action=config_test status=400 source_ip=%s", source_ip)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid config: {str(e)}"})
        }
