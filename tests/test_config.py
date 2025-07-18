import json
from unittest.mock import patch
import pytest
from anymouse.config import load_config_from_s3, validate_config

def test_s3_config_loading():
    # Mock S3 response
    mock_s3_config = {
        "Body": type('obj', (), {'read': lambda self: json.dumps({"fields": ["patient_name", "appointment.doctor"]}).encode('utf-8')})()
    }
    
    with patch("boto3.client") as mock_boto_client:
        mock_s3 = mock_boto_client.return_value
        mock_s3.get_object.return_value = mock_s3_config
        
        config = load_config_from_s3("my-bucket", "config.json")
        assert config == {"fields": ["patient_name", "appointment.doctor"]}

    # Invalid S3 config
    mock_invalid_config = {
        "Body": type('obj', (), {'read': lambda self: json.dumps({"fields": "not-a-list"}).encode('utf-8')})()
    }
    
    with patch("boto3.client") as mock_boto_client:
        mock_s3 = mock_boto_client.return_value
        mock_s3.get_object.return_value = mock_invalid_config
        
        with pytest.raises(ValueError, match="Fields must be a list of strings"):
            load_config_from_s3("my-bucket", "invalid.json")

def test_validate_config():
    valid_config = {"fields": ["patient_name", "appointment.doctor"]}
    result = validate_config(valid_config)
    assert result == valid_config

    invalid_config = {"fields": "not-a-list"}
    with pytest.raises(ValueError, match="Fields must be a list of strings"):
        validate_config(invalid_config)

    invalid_non_string = {"fields": ["patient_name", 123]}
    with pytest.raises(ValueError, match="Fields must be a list of strings"):
        validate_config(invalid_non_string)

    empty_config = {}
    result = validate_config(empty_config)
    assert result == {"fields": []}