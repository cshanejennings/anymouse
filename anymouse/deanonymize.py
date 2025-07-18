"""Core deanonymization logic."""
import copy
import json
import re


def deanonymize_payload(payload: dict, config: dict) -> dict:
    """Replace tokens with original values in a nested payload via provided mapping."""
    message = payload.get("message", "")
    tokens = payload.get("tokens", {})
    if not message or not tokens:
        return {"message": message}  # Early return if no work needed
    
    try:
        result = json.loads(message)  # Parse stringified message to dict
    except json.JSONDecodeError:
        return {"message": message}  # Fallback if not valid JSON
    
    pattern = re.compile(r"\[name\d+\]")  # Matches placeholders like [name1]
    
    def recurse(current: dict):
        for key in list(current.keys()):
            value = current[key]
            if isinstance(value, str):
                # Replace all placeholders in the string
                current[key] = pattern.sub(lambda m: tokens.get(m.group(0), m.group(0)), value)
            elif isinstance(current[key], dict):
                recurse(current[key])
    
    recurse(result)
    restored_message = json.dumps(result)
    return {"message": restored_message}


def deanonymize_text(message: str, tokens: dict) -> str:
    """Replace placeholders in message with their mapped values.

    Parameters
    ----------
    message: str
        Text containing placeholders like ``[name1]``.
    tokens: dict
        Mapping of placeholders to original values.

    Returns
    -------
    str
        Message with placeholders replaced by original values.
    """
    if not tokens:
        return message

    pattern = re.compile(r"\[name\d+\]")

    def repl(match: re.Match) -> str:
        placeholder = match.group(0)
        return tokens.get(placeholder, placeholder)

    return pattern.sub(repl, message)

