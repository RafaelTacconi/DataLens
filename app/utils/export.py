"""CSV export (R22).

The CSV is generated from the actual Polars DataFrame, never from LLM text,
and is capped at the export limit (SDD §24).
"""

import io


def export_csv(df, export_cap=10000):
    """Return CSV text from a DataFrame, capped at the export limit.

    Args:
        df: the result Polars DataFrame.
        export_cap: the maximum number of rows to export.

    Returns:
        A tuple (csv_text, truncated).
    """
    capped = df.head(export_cap)
    truncated = df.height > export_cap
    buf = io.StringIO()
    capped.write_csv(buf)
    return buf.getvalue(), truncated