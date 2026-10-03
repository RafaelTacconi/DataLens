"""Tests for honest execution metrics (R40)."""

from app.db.executor import honest_metrics


def test_only_measured_metrics_shown():
    """R40: unmeasured metrics like rows_scanned are never shown."""
    metrics = {"rows_returned": 3, "truncated": False, "rows_scanned": 999999}
    honest = honest_metrics(metrics)
    assert "rows_scanned" not in honest
    assert honest["rows_returned"] == 3
    assert honest["truncated"] is False