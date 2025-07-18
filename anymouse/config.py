"""
Config loading and validation helpers.
"""
from pydantic import BaseModel, ValidationError, validator
from typing import List

class Config(BaseModel):
    fields: List[str] = []

    @validator("fields")
    def check_fields(cls, value):
        if not all(isinstance(f, str) for f in value):
            raise ValueError("Fields must be a list of strings")
        return value

def validate_config(config: dict) -> dict:
    """
    Validate and normalize a configuration dictionary.
    
    Args:
        config: Dict with optional 'fields' key (list of field paths).
    
    Returns:
        Validated config dict with 'fields' key (defaults to empty list).
    
    Raises:
        ValueError: If config is invalid (e.g., fields not a list of strings).
    """
    try:
        return Config(**config).dict()
    except ValidationError as e:
        raise ValueError(str(e))