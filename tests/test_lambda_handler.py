from unittest.mock import patch
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

@patch("anymouse.lambda_handler.logger.info")  # Mock the logger.info call
def test_lambda_handler_logging(mock_log):
    event = {
        "action": "anonymize",
        "payload": {"name": "Alice"},
        "config": {"fields": ["name"]},
        "headers": {"X-API-Key": "test-api-key-123"},
        "requestContext": {"identity": {"sourceIp": "192.168.1.1"}}  # Simulated API Gateway context
    }
    context = {}  # Not used
    response = lambda_handler(event, context)
    
    # Check response is still correct
    assert "anonymized" in response
    assert response["statusCode"] == 200
    
    # Verify log call
    mock_log.assert_called_once()
    log_msg = mock_log.call_args[0][0]  # The format string
    log_args = mock_log.call_args[0][1:]  # The tuple of args (e.g., ('192.168.1.1',))
    formatted_log = log_msg % log_args  # Format it manually
    assert "action=anonymize" in formatted_log
    assert "status=200" in formatted_log
    assert "source_ip=192.168.1.1" in formatted_log
    assert "Alice" not in formatted_log  # No PII
    assert "test-api-key-123" not in formatted_log  # No sensitive headers

def test_config_test_endpoint():
    event = {
        "action": "config_test",
        "config": {"fields": ["patient_name", "appointment.doctor"]},
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["status"] == "success"
    assert response["config"] == {"fields": ["patient_name", "appointment.doctor"]}
    assert response["statusCode"] == 200

    # Invalid config
    invalid_event = {
        "action": "config_test",
        "config": {"fields": "not-a-list"},
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    invalid_response = lambda_handler(invalid_event, {})
    assert invalid_response["error"].startswith("Invalid config: ")
    assert invalid_response["statusCode"] == 400
