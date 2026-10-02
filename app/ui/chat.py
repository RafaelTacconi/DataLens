"""Chat result display (R21).

The exact result table comes from the Polars DataFrame, never from LLM text.
At most 30 rows are shown in chat; larger results are truncated and the
truncation is stated (SDD §24).
"""


def display_rows(df, row_cap=30):
    """Return the rows to show in chat and whether the result was truncated.

    Args:
        df: the result Polars DataFrame.
        row_cap: the maximum number of rows to show in chat.

    Returns:
        A tuple (rows, truncated) where rows is a list of dicts.
    """
    rows = df.to_dicts()
    truncated = len(rows) > row_cap
    return rows[:row_cap], truncated