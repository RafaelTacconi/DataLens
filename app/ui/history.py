"""History view (R29).

Shows the stored query runs for a workspace.
"""

from app.metadata.store import get_query_history


def history_view(conn, workspace_id):
    """Return the stored query runs for the history view.

    Args:
        conn: the metadata sqlite3 connection.
        workspace_id: the workspace.

    Returns:
        A list of dicts, one per stored run.
    """
    return get_query_history(conn, workspace_id)