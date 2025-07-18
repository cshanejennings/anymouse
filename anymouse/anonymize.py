"""Core anonymization logic for structured payloads and free-form text."""
import re
import uuid
import copy
import json
import uuid  # Not used now, but keep if needed for other tokens

try:
    import spacy
    try:
        _NLP = spacy.load("en_core_web_sm")
        _SPACY_AVAILABLE = True
    except Exception:
        _SPACY_AVAILABLE = False
        _NLP = None
except ImportError:
    _SPACY_AVAILABLE = False
    _NLP = None


def anonymize_payload(payload: dict, config: dict) -> dict:
    """Replace target fields with unique tokens in a nested payload."""
    fields = config.get("fields", [])
    result = copy.deepcopy(payload)  # Deep copy to avoid modifying original
    tokens = {}
    field_index = 1
    fields_set = set(fields)  # For quick lookup

    def recurse(current: dict, path: str = ""):
        nonlocal field_index
        for key in list(current.keys()):  # Avoid runtime errors during iteration
            full_path = f"{path}.{key}" if path else key
            if full_path in fields_set:
                placeholder = f"[name{field_index}]"
                tokens[placeholder] = current[key]
                current[key] = placeholder
                field_index += 1
            elif isinstance(current[key], dict):
                recurse(current[key], full_path if path else key)

    recurse(result)
    message = json.dumps(result)  # Stringify as per edge case format
    return {"message": message, "tokens": tokens, "fields": fields}


_STOPWORDS = {
    "The",
    "This",
    "That",
    "A",
    "An",
    "It",
    "London",
    "Apple",
    "Google",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "Hello",
    "User",
    "ID",
    "Notes"
}


def _regex_name_pattern() -> re.Pattern:
    """Return compiled regex to roughly match capitalized names."""
    return re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")


def anonymize_text(text: str) -> dict:
    """Anonymize PERSON, ORG, GPE, and DATE entities in free-form text.

    Parameters
    ----------
    text: str
        Input text possibly containing entities.

    Returns
    -------
    dict with keys:
        - message: text with entities replaced by placeholders
        - tokens: mapping from placeholder to original entity
        - fields: list of entity types anonymized
    """
    entity_types = ["PERSON", "ORG", "GPE", "DATE"]  # Supported types
    type_prefixes = {"PERSON": "name", "ORG": "org", "GPE": "loc", "DATE": "date"}
    if _SPACY_AVAILABLE:
        doc = _NLP(text)
        entities = [(ent.start_char, ent.end_char, ent.text, ent.label_) for ent in doc.ents if ent.label_ in entity_types]
    else:
        # Fallback to regex for PERSON only
        pattern = _regex_name_pattern()
        entities = []
        for match in pattern.finditer(text):
            name = match.group(0)
            if name in _STOPWORDS:
                continue
            entities.append((match.start(), match.end(), name, "PERSON"))

    if not entities:
        return {"message": text, "tokens": {}, "fields": entity_types}

    # Replace from left to right, assigning unique placeholders by type
    entities.sort(key=lambda x: x[0])  # Sort by start position
    type_counters = {t: 1 for t in entity_types}  # e.g., {"PERSON": 1, "ORG": 1, ...}
    mapping = {}  # entity_text -> placeholder
    result_parts = []
    last = 0
    for start, end, entity_text, entity_type in entities:
        result_parts.append(text[last:start])
        if entity_text not in mapping:
            prefix = type_prefixes[entity_type]
            placeholder = f"[{prefix}{type_counters[entity_type]}]"
            mapping[entity_text] = placeholder
            type_counters[entity_type] += 1
        else:
            placeholder = mapping[entity_text]
        result_parts.append(placeholder)
        last = end
    result_parts.append(text[last:])

    tokens = {placeholder: entity_text for entity_text, placeholder in mapping.items()}
    return {"message": "".join(result_parts), "tokens": tokens, "fields": entity_types}
