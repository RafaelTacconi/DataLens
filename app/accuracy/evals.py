"""Evaluation set (R31).

Golden questions per workspace, evaluated on RESULTS, not SQL text (SDD §32).
A regression is visible to the user who saved the change.
"""


def evaluate_case(actual_df, expected_columns, expected_rows,
                  order_matters=False):
    """Compare an actual result against an evaluation case.

    Args:
        actual_df: the result Polars DataFrame.
        expected_columns: the expected output column names.
        expected_rows: the expected result rows.
        order_matters: whether row order must match exactly.

    Returns:
        True if the result matches the case.
    """
    actual_cols = list(actual_df.columns)
    actual_rows = [list(r) for r in actual_df.rows()]
    if set(actual_cols) != set(expected_columns):
        return False
    if order_matters:
        return actual_rows == expected_rows
    return sorted(actual_rows) == sorted(expected_rows)