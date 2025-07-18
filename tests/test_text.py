import pytest
from anymouse import anonymize_text, deanonymize_text


def test_no_person_entities():
    text = "Hello world."
    result = anonymize_text(text)
    assert result["message"] == text
    assert result["tokens"] == {}
    assert result["fields"] == ["PERSON", "ORG", "GPE", "DATE"]


def test_multiple_distinct_names():
    text = "Alice met Bob at the park."
    result = anonymize_text(text)
    assert result["message"] == "[name1] met [name2] at the park."
    assert result["tokens"] == {"[name1]": "Alice", "[name2]": "Bob"}


def test_duplicate_name():
    text = "Alice spoke to Alice yesterday."
    result = anonymize_text(text)
    assert result["message"] == "[name1] spoke to [name1] [date1]."
    assert result["tokens"] == {"[name1]": "Alice", "[date1]": "yesterday"}


def test_name_like_non_person_word():
    text = "I visited London and saw Alice."
    result = anonymize_text(text)
    assert result["message"] == "I visited [loc1] and saw [name1]."
    assert result["tokens"] == {"[loc1]": "London", "[name1]": "Alice"}


def test_mixed_content_round_trip():
    text = "User: Alice\nID: 123\nNotes: Bob said hi."
    anon = anonymize_text(text)
    assert anon["message"] == "User: Alice\nID: 123\nNotes: [name1] said hi."
    assert anon["tokens"] == {"[name1]": "Bob"}
    dean = deanonymize_text(anon["message"], anon["tokens"])
    assert dean == text


def test_multiple_entity_types():
    text = "The patient saw Dr. John Smith at Sunnybrook Hospital in Toronto on Jan 1, 2024."
    result = anonymize_text(text)
    assert result["message"] == "The patient saw [name1] at [org1] in [loc1] on [date1]."
    assert result["tokens"] == {
        "[name1]": "Dr. John Smith",
        "[org1]": "Sunnybrook Hospital",
        "[loc1]": "Toronto",
        "[date1]": "Jan 1, 2024"
    }
    assert result["fields"] == ["PERSON", "ORG", "GPE", "DATE"]
