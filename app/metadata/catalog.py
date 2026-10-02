"""Catalog, business context and business terms (R16).

Per-workspace business knowledge stored in the metadata database. Objects may
be marked not exposed; a not-exposed object is hidden from LLM context and
excluded from the exposed-table allow-list (SDD §14).
"""


def set_business_context(conn, workspace_id, text):
    """Store or replace a workspace's plain-language business context."""
    conn.execute(
        "UPDATE workspaces SET business_context=? WHERE id=?",
        (text, workspace_id),
    )
    conn.commit()


def get_business_context(conn, workspace_id):
    """The workspace's business context, or None if none is set."""
    row = conn.execute(
        "SELECT business_context FROM workspaces WHERE id=?",
        (workspace_id,),
    ).fetchone()
    return row["business_context"] if row else None


def add_catalog_entry(conn, workspace_id, object_type, name, description,
                      exposed=True):
    """Add a table or column to the workspace catalog."""
    conn.execute(
        "INSERT INTO catalog (workspace_id, object_type, name, description, "
        "exposed) VALUES (?, ?, ?, ?, ?)",
        (workspace_id, object_type, name, description, 1 if exposed else 0),
    )
    conn.commit()


def get_exposed_tables(conn, workspace_id):
    """The names of exposed tables in a workspace (the allow-list)."""
    rows = conn.execute(
        "SELECT name FROM catalog WHERE workspace_id=? AND object_type='table' "
        "AND exposed=1",
        (workspace_id,),
    ).fetchall()
    return {r["name"] for r in rows}


def add_business_term(conn, workspace_id, term, definition):
    """Add a business term and its definition to a workspace."""
    conn.execute(
        "INSERT INTO business_terms (workspace_id, term, definition) "
        "VALUES (?, ?, ?)",
        (workspace_id, term, definition),
    )
    conn.commit()


def get_business_terms(conn, workspace_id):
    """The workspace's business terms as {term: definition}."""
    rows = conn.execute(
        "SELECT term, definition FROM business_terms WHERE workspace_id=?",
        (workspace_id,),
    ).fetchall()
    return {r["term"]: r["definition"] for r in rows}