"""Core anonymization logic for structured payloads and free-form text."""
import re
import uuid

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
    """Replace target fields with unique tokens. Store mapping in persistent storage (TODO)."""
    # TODO: Implement recursive field extraction and token replacement.
    # For now, simple shallow mapping for demonstration.
    result = payload.copy()
    fields = config.get("fields", [])
    for field in fields:
        if field in result:
            # Replace with a UUID token.
            result[field] = f"token:{uuid.uuid4().hex}"
            # TODO: Store mapping (token -> real value) in DynamoDB.
    return result


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
    """Anonymize PERSON names in free-form text.

    Parameters
    ----------
    text: str
        Input text possibly containing names.

    Returns
    -------
    dict with keys:
        - message: text with names replaced by placeholders
        - tokens: mapping from placeholder to original name
        - fields: list of fields anonymized (always ["PERSON"])
    """
    if _SPACY_AVAILABLE:
        doc = _NLP(text)
        entities = [(ent.start_char, ent.end_char, ent.text) for ent in doc.ents if ent.label_ == "PERSON"]
    else:
        pattern = _regex_name_pattern()
        entities = []
        for match in pattern.finditer(text):
            name = match.group(0)
            if name in _STOPWORDS:
                continue
            entities.append((match.start(), match.end(), name))

    if not entities:
        return {"message": text, "tokens": {}, "fields": ["PERSON"]}

    # Replace from left to right using mapping of unique names to placeholders
    entities.sort(key=lambda x: x[0])
    mapping = {}
    result_parts = []
    last = 0
    for start, end, name in entities:
        result_parts.append(text[last:start])
        if name not in mapping:
            placeholder = f"[name{len(mapping)+1}]"
            mapping[name] = placeholder
        else:
            placeholder = mapping[name]
        result_parts.append(placeholder)
        last = end
    result_parts.append(text[last:])

    tokens = {placeholder: name for name, placeholder in mapping.items()}
    return {"message": "".join(result_parts), "tokens": tokens, "fields": ["PERSON"]}

