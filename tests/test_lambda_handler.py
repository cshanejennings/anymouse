import pytest
from anymouse.lambda_handler import lambda_handler

def test_lambda_handler_authorization():
    # Valid API key event
    valid_event = {
        "action": "anonymize",
        "payload": {"name": "Alice"},
        "config": {"fields": ["name"]},
        "headers": {"X-API-Key": "test-api-key-123"}  # Simulated valid key
    }
    valid_context = {}  # Context not used in handler
    valid_response = lambda_handler(valid_event, valid_context)
    assert "error" not in valid_response  # Should process normally
    assert "anonymized" in valid_response or "deanonymized" in valid_response

    # Missing API key
    no_key_event = {
        "action": "anonymize",
        "payload": {"name": "Alice"},
        "config": {"fields": ["name"]}
    }
    no_key_response = lambda_handler(no_key_event, valid_context)
    assert no_key_response["error"] == "Missing or invalid API key"
    assert no_key_response["statusCode"] == 401

    # Invalid API key
    invalid_key_event = {
        "action": "anonymize",
        "payload": {"name": "Alice"},
        "config": {"fields": ["name"]},
        "headers": {"X-API-Key": "wrong-key"}
    }
    invalid_key_response = lambda_handler(invalid_key_event, valid_context)
    assert invalid_key_response["error"] == "Missing or invalid API key"
    assert invalid_key_response["statusCode"] == 401

def test_lambda_handler_invalid_config():
    event = {
        "action": "anonymize",
        "payload": {"name": "Alice"},
        "config": {"fields": "not-a-list"},
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["error"].startswith("Invalid config: ")
    assert response["statusCode"] == 400