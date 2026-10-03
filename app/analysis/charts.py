"""Charts (R34).

Charts are built from the result DataFrame, never from LLM text.
"""


def build_chart(df, x, y):
    """Build a chart spec from a result DataFrame.

    Args:
        df: the result Polars DataFrame.
        x: the x-axis column.
        y: the y-axis column.

    Returns:
        A dict with the x/y columns and the data rows.
    """
    return {
        "x": x,
        "y": y,
        "data": df.select([x, y]).to_dicts(),
    }