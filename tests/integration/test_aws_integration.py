"""Integration tests for AWS services used by Anymouse."""
import json
import boto3
import pytest
import time
from moto import mock_s3, mock_ssm, mock_lambda, mock_apigateway
from unittest.mock import patch, MagicMock
import requests


class TestS3Integration:
    """Test S3 configuration loading."""
    
    @mock_s3
    def test_load_config_from_s3_success(self):
        """Test successful config loading from S3."""
        from anymouse.config import load_config_from_s3
        
        # Setup mock S3
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-config-bucket'
        s3.create_bucket(Bucket=bucket_name)
        
        # Upload test config
        test_config = {"fields": ["name", "email"]}
        s3.put_object(
            Bucket=bucket_name,
            Key='config.json',
            Body=json.dumps(test_config)
        )
        
        # Test loading
        result = load_config_from_s3(bucket_name, 'config.json')
        assert result == test_config
    
    @mock_s3
    def test_load_config_from_s3_missing_bucket(self):
        """Test error handling for missing S3 bucket."""
        from anymouse.config import load_config_from_s3
        
        with pytest.raises(ValueError, match="Failed to load config from S3"):
            load_config_from_s3('nonexistent-bucket', 'config.json')
    
    @mock_s3
    def test_load_config_from_s3_invalid_json(self):
        """Test error handling for invalid JSON in S3."""
        from anymouse.config import load_config_from_s3
        
        # Setup mock S3 with invalid JSON
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-config-bucket'
        s3.create_bucket(Bucket=bucket_name)
        s3.put_object(
            Bucket=bucket_name,
            Key='invalid.json',
            Body='invalid json content'
        )
        
        with pytest.raises(ValueError, match="Failed to load config from S3"):
            load_config_from_s3(bucket_name, 'invalid.json')


class TestSSMIntegration:
    """Test SSM parameter store integration."""
    
    @mock_ssm
    def test_get_api_key_from_ssm_success(self):
        """Test successful API key retrieval from SSM."""
        from anymouse.lambda_handler import get_api_key_from_ssm
        
        # Setup mock SSM
        ssm = boto3.client('ssm', region_name='us-east-1')
        ssm.put_parameter(
            Name='/anymouse/api-key',
            Value='test-secret-key-123',
            Type='SecureString'
        )
        
        # Test retrieval
        result = get_api_key_from_ssm()
        assert result == 'test-secret-key-123'
    
    @mock_ssm
    def test_get_api_key_from_ssm_fallback(self):
        """Test fallback to hardcoded key when SSM fails."""
        from anymouse.lambda_handler import get_api_key_from_ssm
        
        # No SSM parameter exists, should fall back
        result = get_api_key_from_ssm()
        assert result == 'test-api-key-123'


class TestLambdaIntegration:
    """Test Lambda function integration."""
    
    def test_lambda_handler_performance(self):
        """Test Lambda handler performance with various payload sizes."""
        from anymouse.lambda_handler import lambda_handler
        
        # Test with small payload
        small_event = {
            "httpMethod": "POST",
            "path": "/anonymize",
            "body": json.dumps({
                "payload": "Hello Dr. Smith"
            }),
            "headers": {"X-API-Key": "test-api-key-123"}
        }
        
        start_time = time.time()
        response = lambda_handler(small_event, {})
        small_duration = time.time() - start_time
        
        assert response["statusCode"] == 200
        assert small_duration < 1.0  # Should be under 1 second
        
        # Test with larger payload
        large_text = "Hello Dr. Smith. " * 100  # Repeat to make larger
        large_event = {
            "httpMethod": "POST",
            "path": "/anonymize",
            "body": json.dumps({
                "payload": large_text
            }),
            "headers": {"X-API-Key": "test-api-key-123"}
        }
        
        start_time = time.time()
        response = lambda_handler(large_event, {})
        large_duration = time.time() - start_time
        
        assert response["statusCode"] == 200
        assert large_duration < 2.0  # Should still be under 2 seconds
    
    def test_lambda_memory_usage(self):
        """Test Lambda memory usage patterns."""
        from anymouse.lambda_handler import lambda_handler
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process multiple requests
        event = {
            "httpMethod": "POST",
            "path": "/anonymize",
            "body": json.dumps({
                "payload": "Hello Dr. Smith, this is a test message for Jane Doe."
            }),
            "headers": {"X-API-Key": "test-api-key-123"}
        }
        
        for _ in range(10):
            response = lambda_handler(event, {})
            assert response["statusCode"] == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 50MB for 10 requests)
        assert memory_growth < 50


@pytest.mark.integration
class TestEndToEndIntegration:
    """End-to-end integration tests requiring actual AWS resources."""
    
    def test_real_api_deployment(self, api_url, api_key):
        """Test against real deployed API."""
        if not api_url or not api_key:
            pytest.skip("Real API URL and key not provided")
        
        # Test anonymize endpoint
        response = requests.post(
            f"{api_url}/anonymize",
            json={
                "payload": "Hello Dr. McCulloch, this is a message from Jane Smith."
            },
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "tokens" in data
        assert "fields" in data
        
        # Test deanonymize endpoint
        deanonymize_response = requests.post(
            f"{api_url}/deanonymize",
            json={
                "message": data["message"],
                "tokens": data["tokens"]
            },
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        assert deanonymize_response.status_code == 200
        deanonymized = deanonymize_response.json()
        assert "Dr. McCulloch" in deanonymized["message"]
        assert "Jane Smith" in deanonymized["message"]
    
    def test_api_performance_under_load(self, api_url, api_key):
        """Test API performance under concurrent load."""
        if not api_url or not api_key:
            pytest.skip("Real API URL and key not provided")
        
        import concurrent.futures
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = requests.post(
                    f"{api_url}/anonymize",
                    json={
                        "payload": f"Hello Dr. Smith from thread {threading.current_thread().ident}"
                    },
                    headers={"X-API-Key": api_key},
                    timeout=10
                )
                results.append(response.elapsed.total_seconds())
                return response.status_code == 200
            except Exception as e:
                errors.append(str(e))
                return False
        
        # Test with 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            success_count = sum(future.result() for future in futures)
        
        # Should handle at least 90% of requests successfully
        assert success_count >= 18
        assert len(errors) <= 2
        
        # Average response time should be reasonable
        if results:
            avg_response_time = sum(results) / len(results)
            assert avg_response_time < 2.0  # Under 2 seconds average


# Pytest fixtures for real API testing
@pytest.fixture
def api_url(request):
    """Get API URL from command line or environment."""
    return request.config.getoption("--api-url", default=None)

@pytest.fixture
def api_key(request):
    """Get API key from command line or environment."""
    return request.config.getoption("--api-key", default=None)


def pytest_addoption(parser):
    """Add command line options for integration tests."""
    parser.addoption(
        "--api-url",
        action="store",
        default=None,
        help="API Gateway URL for integration tests"
    )
    parser.addoption(
        "--api-key",
        action="store", 
        default=None,
        help="API key for integration tests"
    )