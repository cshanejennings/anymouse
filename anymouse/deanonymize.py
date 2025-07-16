"""Core deanonymization logic."""
import re


def deanonymize_payload(payload: dict, config: dict) -> dict:
    """Replace tokens with original values via mapping store (TODO)."""
    # TODO: Lookup token in DynamoDB and restore real value.
    return payload  # Stub: pass-through for now.


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

