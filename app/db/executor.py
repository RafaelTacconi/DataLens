"""Query executor (R11, R40).

Executes already-validated canonical SQL through a guarded read-only
connection and returns a Polars DataFrame plus honest execution metrics. Uses
a capped fetch, never fetchall (SDD §22, §24).
"""

import polars as pl

from app.db.authorizer import make_authorizer
from app.db.connection import open_readonly_connection

# The only metrics the system actually measures (SDD §23).
MEASURED_METRICS = {"duration_seconds", "rows_returned", "truncated",
                    "plan_shape"}


def honest_metrics(metrics):
    """Return only the metrics the system actually measures (R40).

    Args:
        metrics: a dict of candidate metrics.

    Returns:
        A dict with only the measured metrics.
    """
    return {k: v for k, v in metrics.items() if k in MEASURED_METRICS}


def execute_query(db_path, canonical_sql, allowed_tables, row_cap=10000):
    """Execute canonical SQL read-only and return a DataFrame and metrics.

    Args:
        db_path: the resolved target database path.
        canonical_sql: the canonical SQL string (already validated).
        allowed_tables: the workspace's exposed-table allow-list.
        row_cap: the maximum number of rows to fetch.

    Returns:
        A tuple (DataFrame, metrics) where metrics holds rows_returned and
        truncated.
    """
    conn = open_readonly_connection(db_path, make_authorizer(allowed_tables))
    try:
        cur = conn.execute(canonical_sql)
        columns = [d[0] for d in cur.description]
        rows = cur.fetchmany(row_cap + 1)
        truncated = len(rows) > row_cap
        rows = rows[:row_cap]
        df = pl.DataFrame(rows, schema=columns, orient="row")
        metrics = {"rows_returned": len(rows), "truncated": truncated}
        return df, metrics
    finally:
        conn.close()