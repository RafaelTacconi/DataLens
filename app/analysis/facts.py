"""Facts payload (R26).

Python builds the facts an explanation is allowed to use, from the actual
result. The explanation LLM must not invent additional numbers (SDD §25).
"""

from app.models.contracts import FactsPayload


def build_facts(df):
    """Build a facts payload from a result DataFrame.

    Args:
        df: the result Polars DataFrame.

    Returns:
        A FactsPayload whose facts are the DataFrame's rows.
    """
    return FactsPayload(facts=df.to_dicts())