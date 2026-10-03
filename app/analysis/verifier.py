"""Number verifier (R27).

Every numerical claim in an explanation is checked against the facts payload.
If verification fails, the explanation is not shown as factual (SDD §25).
"""

import re

_NUMBER = re.compile(r"\d[\d,]*\.?\d*")


def _normalize(num):
    """Normalize a number string so 1500000 and 1500000.0 compare equal."""
    cleaned = num.replace(",", "")
    try:
        return str(float(cleaned))
    except ValueError:
        return cleaned


def _numbers(text):
    """All numbers in a text, normalized."""
    return [_normalize(n) for n in _NUMBER.findall(text)]


def _fact_numbers(facts_payload):
    """All numeric values in the facts payload, normalized."""
    out = set()
    for fact in facts_payload.facts:
        for value in fact.values():
            if isinstance(value, (int, float)):
                out.add(_normalize(str(value)))
    return out


def verify_numbers(explanation, facts_payload):
    """Whether every number in the explanation appears in the facts.

    Args:
        explanation: the explanation text.
        facts_payload: the FactsPayload the explanation may use.

    Returns:
        True if every number in the explanation matches a fact value.
    """
    fact_numbers = _fact_numbers(facts_payload)
    return all(num in fact_numbers for num in _numbers(explanation))