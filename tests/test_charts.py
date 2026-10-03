"""Tests for app/analysis/charts.py (R34)."""

from app.analysis.charts import build_chart
from app.db.executor import execute_query
from tests.fixtures.make_fixture import build_fixture


def test_build_chart_from_result(tmp_path):
    """R34: a chart is built from the result DataFrame."""
    db = build_fixture(str(tmp_path / "trades.db"), "a")
    df, _ = execute_query(
        db,
        "SELECT region, SUM(notional_value) AS total FROM trades GROUP BY region",
        ["trades", "regions"],
    )
    chart = build_chart(df, "region", "total")
    assert chart["x"] == "region"
    assert chart["y"] == "total"
    assert len(chart["data"]) == 3