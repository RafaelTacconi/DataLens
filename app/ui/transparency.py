"""Transparency panel (R23).

Builds the transparency record for a completed turn from stored structured
state, never reconstructed from chat text (Guide §3.12). The record carries
the 13 items the SDD §28 requires.
"""

from app.models.contracts import TransparencyRecord


def build_transparency(question, understanding, tables_used, why_sources,
                       columns_used, plan, canonical_sql, execution,
                       assumptions, resolved_period, result_summary,
                       validation_status, provenance):
    """Build a TransparencyRecord with all 13 required items.

    Args:
        question: the user's request.
        understanding: what the system understood.
        tables_used: the tables read.
        why_sources: why those sources were chosen.
        columns_used: the columns read.
        plan: the query/analysis plan.
        canonical_sql: the executed canonical SQL.
        execution: execution information.
        assumptions: the assumptions made.
        resolved_period: the resolved time period.
        result_summary: a summary of the exact result.
        validation_status: the validation status.
        provenance: provenance details.

    Returns:
        A TransparencyRecord.
    """
    return TransparencyRecord(
        request=question,
        understanding=understanding,
        tables_used=tables_used,
        why_sources=why_sources,
        columns_used=columns_used,
        plan=plan,
        canonical_sql=canonical_sql,
        execution=execution,
        assumptions=assumptions,
        resolved_period=resolved_period,
        result_summary=result_summary,
        validation_status=validation_status,
        provenance=provenance,
    )