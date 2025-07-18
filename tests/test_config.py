import pytest
from anymouse.config import validate_config

def test_config_validation():
    # Valid config with flat and nested fields
    valid_config = {"fields": ["patient_name", "appointment.doctor"]}
    result = validate_config(valid_config)
    assert result == valid_config  # Returns unchanged if valid

    # Invalid config: fields not a list
    invalid_config = {"fields": "patient_name"}
    with pytest.raises(ValueError, match="Fields must be a list of strings"):
        validate_config(invalid_config)

    # Invalid config: fields contains non-string
    invalid_config = {"fields": ["patient_name", 123]}
    with pytest.raises(ValueError, match="Fields must be a list of strings"):
        validate_config(invalid_config)

    # Empty config (allowed, defaults to no fields)
    empty_config = {}
    result = validate_config(empty_config)
    assert result == {"fields": []}  # Adds default empty fields