"""SQL validation (R9).

Generated SQL is a draft and is never executed directly. It must pass
AST-based validation (sqlglot, SQLite dialect) before it is canonicalised and
run. This module only inspects SQL; it never executes it (Guide §4).
"""

import sqlglot
from sqlglot import exp

# Functions that can read or write files or load code; never allowed.
PROHIBITED_FUNCTIONS = {"load_extension", "writefile", "readfile", "eval"}


class ValidationError(Exception):
    """Generated SQL failed validation."""


def validate_sql(sql, schema, allowed_tables, plan=None):
    """Validate generated SQL against the schema and allowed tables.

    Args:
        sql: the generated SQL string (a draft, never executed directly).
        schema: a mapping {table: {column, ...}} of the target database.
        allowed_tables: an iterable of table names that may be read.
        plan: an optional structured plan, reserved for plan-matching checks.

    Returns:
        The parsed sqlglot statement.

    Raises:
        ValidationError: if the SQL is unsafe or does not match the schema.
    """
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as err:
        raise ValidationError(f"could not parse SQL: {err}") from err

    if len(statements) != 1:
        raise ValidationError("exactly one statement is required")

    stmt = statements[0]
    if not isinstance(stmt, exp.Select):
        raise ValidationError("only SELECT (or WITH...SELECT) is allowed")

    allowed = set(allowed_tables)
    errors = []

    for table in stmt.find_all(exp.Table):
        name = table.name
        if name not in schema:
            errors.append(f"unknown table: {name}")
        elif name not in allowed:
            errors.append(f"table not exposed: {name}")

    referenced = {t.name for t in stmt.find_all(exp.Table)}
    for col in stmt.find_all(exp.Column):
        table = col.table
        name = col.name
        if table:
            if table in schema and name not in schema[table]:
                errors.append(f"unknown column: {table}.{name}")
        elif referenced and not any(
                name in schema[t] for t in referenced if t in schema):
            errors.append(f"unknown column: {name}")

    for func in stmt.find_all(exp.Func):
        if func.sql_name().lower() in PROHIBITED_FUNCTIONS:
            errors.append(f"prohibited function: {func.sql_name()}")

    if errors:
        raise ValidationError("; ".join(errors))
    return stmt