"""
AWS Lambda entrypoint for Anymouse anonymization service.
Dispatches requests to anonymize or deanonymize functions.
"""

import json
from .anonymize import anonymize_payload
from .deanonymize import deanonymize_payload

"""
AWS Lambda entrypoint for Anymouse anonymization service.
Dispatches requests to anonymize or deanonymize functions.
"""
import json
from .anonymize import anonymize_payload
from .deanonymize import deanonymize_payload

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
        return {"error": "Missing or invalid API key", "statusCode": 401}
    
    action = event.get("action")
    payload = event.get("payload")
    config = event.get("config", {})

    if action == "anonymize":
        return {"anonymized": anonymize_payload(payload, config), "statusCode": 200}
    elif action == "deanonymize":
        return {"deanonymized": deanonymize_payload(payload, config), "statusCode": 200}
    else:
        return {"error": "Invalid action", "statusCode": 400}
