import json
import pytest
from anymouse.anonymize import anonymize_payload
from anymouse.deanonymize import deanonymize_payload

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

def test_recursive_deanonymization_round_trip():
    original_payload = {
        "patient_name": "Jane Doe",
        "referrer_name": "Dr. John Smith",
        "appointment": {
            "doctor": "Dr. Fiona McCulloch"
        }
    }
    config = {
        "fields": ["patient_name", "referrer_name", "appointment.doctor"]
    }
    
    # Anonymize first
    anon_result = anonymize_payload(original_payload, config)
    
    # Deanonymize using the anon output as input
    dean_input = {
        "message": anon_result["message"],
        "tokens": anon_result["tokens"]
    }
    dean_result = deanonymize_payload(dean_input, config)  # Note: config passed but not used yet; for future hooks
    
    # Parse the deanonymized message back to dict
    restored_dict = json.loads(dean_result["message"])
    
    assert restored_dict == original_payload
    assert "Dr. Fiona McCulloch" in dean_result["message"]  # Ensure originals are restored
    assert "[name3]" not in dean_result["message"]  # Placeholders gone