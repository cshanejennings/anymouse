import json
from unittest.mock import patch
import pytest
from anymouse.lambda_handler import lambda_handler

def test_lambda_handler_authorization():
    # Valid API key event for /anonymize
    valid_event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config": {"fields": ["name"]}
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    valid_context = {}
    valid_response = lambda_handler(valid_event, valid_context)
    assert valid_response["statusCode"] == 200
    response_body = json.loads(valid_response["body"])
    assert "message" in response_body
    assert "tokens" in response_body

    # Missing API key
    no_key_event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config": {"fields": ["name"]}
        })
    }
    no_key_response = lambda_handler(no_key_event, valid_context)
    assert no_key_response["statusCode"] == 401
    response_body = json.loads(no_key_response["body"])
    assert response_body["error"] == "Missing or invalid API key"

    # Invalid API key
    invalid_key_event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config": {"fields": ["name"]}
        }),
        "headers": {"X-API-Key": "wrong-key"}
    }
    invalid_key_response = lambda_handler(invalid_key_event, valid_context)
    assert invalid_key_response["statusCode"] == 401
    response_body = json.loads(invalid_key_response["body"])
    assert response_body["error"] == "Missing or invalid API key"

def test_lambda_handler_invalid_config():
    event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config": {"fields": "not-a-list"}
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 400
    response_body = json.loads(response["body"])
    assert response_body["error"].startswith("Invalid request: ")

@patch("anymouse.lambda_handler.logger.info")
def test_lambda_handler_logging(mock_log):
    event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config": {"fields": ["name"]}
        }),
        "headers": {"X-API-Key": "test-api-key-123"},
        "requestContext": {"identity": {"sourceIp": "192.168.1.1"}}
    }
    context = {}
    response = lambda_handler(event, context)
    
    # Check response is correct
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert "message" in response_body
    assert "tokens" in response_body
    
    # Verify log call
    mock_log.assert_called_once()
    log_msg = mock_log.call_args[0][0]
    log_args = mock_log.call_args[0][1:]
    formatted_log = log_msg % log_args
    assert "action=anonymize" in formatted_log
    assert "status=200" in formatted_log
    assert "source_ip=192.168.1.1" in formatted_log
    assert "Alice" not in formatted_log
    assert "test-api-key-123" not in formatted_log

def test_config_test_endpoint():
    event = {
        "httpMethod": "POST",
        "path": "/config/test",
        "body": json.dumps({
            "config": {"fields": ["patient_name", "appointment.doctor"]}
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert response_body["status"] == "success"
    assert response_body["config"] == {"fields": ["patient_name", "appointment.doctor"]}

    # Invalid config
    invalid_event = {
        "httpMethod": "POST",
        "path": "/config/test",
        "body": json.dumps({
            "config": {"fields": "not-a-list"}
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    invalid_response = lambda_handler(invalid_event, {})
    assert invalid_response["statusCode"] == 400
    response_body = json.loads(invalid_response["body"])
    assert response_body["error"].startswith("Invalid config: ")

@patch("anymouse.config.boto3.client")
def test_lambda_handler_s3_config(mock_boto_client):
    mock_s3_config = {
        "Body": type('obj', (), {'read': lambda self: json.dumps({"fields": ["name"]}).encode('utf-8')})()
    }
    mock_boto_client.return_value.get_object.return_value = mock_s3_config
    
    event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": {"name": "Alice"},
            "config_source": {"s3": {"bucket": "my-bucket", "key": "config.json"}}
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert "tokens" in response_body
    assert response_body["tokens"] == {"[name1]": "Alice"}

def test_anonymize_text_endpoint():
    """Test /anonymize endpoint with free-form text."""
    event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({
            "payload": "Hello, I have a question for Dr. McCulloch regarding my prescription. Thank you, Jane Smith"
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert "message" in response_body
    assert "tokens" in response_body
    assert "fields" in response_body
    assert "[name1]" in response_body["message"]
    assert "[name2]" in response_body["message"]

def test_deanonymize_endpoint():
    """Test /deanonymize endpoint."""
    event = {
        "httpMethod": "POST",
        "path": "/deanonymize",
        "body": json.dumps({
            "message": "Hello, I have a question for [name1] regarding my prescription. Thank you, [name2]",
            "tokens": {
                "[name1]": "Dr. McCulloch",
                "[name2]": "Jane Smith"
            }
        }),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert response_body["message"] == "Hello, I have a question for Dr. McCulloch regarding my prescription. Thank you, Jane Smith"

def test_invalid_endpoint():
    """Test invalid endpoint returns 404."""
    event = {
        "httpMethod": "POST",
        "path": "/invalid",
        "body": json.dumps({}),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 404
    response_body = json.loads(response["body"])
    assert response_body["error"] == "Endpoint not found"

def test_missing_payload():
    """Test /anonymize with missing payload field."""
    event = {
        "httpMethod": "POST",
        "path": "/anonymize",
        "body": json.dumps({}),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 400
    response_body = json.loads(response["body"])
    assert response_body["error"] == "Missing 'payload' field"

def test_missing_deanonymize_fields():
    """Test /deanonymize with missing required fields."""
    event = {
        "httpMethod": "POST",
        "path": "/deanonymize",
        "body": json.dumps({"message": "test"}),
        "headers": {"X-API-Key": "test-api-key-123"}
    }
    response = lambda_handler(event, {})
    assert response["statusCode"] == 400
    response_body = json.loads(response["body"])
    assert response_body["error"] == "Missing 'message' or 'tokens' field"