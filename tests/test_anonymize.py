import json
import pytest
from anymouse.anonymize import anonymize_payload

def test_recursive_anonymization():
    payload = {
        "patient_name": "Jane Doe",
        "referrer_name": "Dr. John Smith",
        "appointment": {
            "doctor": "Dr. Fiona McCulloch"
        }
    }
    config = {
        "fields": ["patient_name", "referrer_name", "appointment.doctor"]
    }
    result = anonymize_payload(payload, config)
    
    # Parse the message back to dict for assertions (assuming message is JSON string)
    anonymized_dict = json.loads(result["message"])
    
    assert anonymized_dict["patient_name"] == "[name1]"
    assert anonymized_dict["referrer_name"] == "[name2]"
    assert anonymized_dict["appointment"]["doctor"] == "[name3]"
    assert result["tokens"] == {
        "[name1]": "Jane Doe",
        "[name2]": "Dr. John Smith",
        "[name3]": "Dr. Fiona McCulloch"
    }
    assert result["fields"] == ["patient_name", "referrer_name", "appointment.doctor"]
    assert "Jane Doe" not in result["message"]  # Ensure originals are gone