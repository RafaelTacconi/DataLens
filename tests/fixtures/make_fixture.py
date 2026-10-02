"""Build the synthetic SQLite fixtures for the artifact test.

SYNTHETIC - no real sample was provided (contract Part 8, B1). Two variants
with different content, so the artifact test can prove the pipeline derives
rather than recites.

Schema: `regions(region_code, region_name)` and
`trades(trade_id, region, instrument, notional_value, trade_date)`.
"""

import sqlite3

_SCHEMA = """
CREATE TABLE regions (
    region_code TEXT PRIMARY KEY,
    region_name TEXT
);
CREATE TABLE trades (
    trade_id INTEGER PRIMARY KEY,
    region TEXT,
    instrument TEXT,
    notional_value REAL,
    trade_date TEXT
);
"""

# variant "a": expected 2026 totals - North 1,500,000; South 900,000;
# East 600,000. Trade 6 is dated 2025 and must be excluded by the date filter.
_VARIANT_A = {
    "regions": [("N", "North"), ("S", "South"), ("E", "East")],
    "trades": [
        (1, "N", "GOLD", 500000.0, "2026-03-01"),
        (2, "N", "GOLD", 1000000.0, "2026-05-15"),
        (3, "S", "SILVER", 400000.0, "2026-02-10"),
        (4, "S", "SILVER", 500000.0, "2026-07-01"),
        (5, "E", "PLAT", 600000.0, "2026-04-20"),
        (6, "N", "GOLD", 0.0, "2025-12-31"),
    ],
}

# variant "b": different regions and amounts - West 2,500,000; Central 100,000.
_VARIANT_B = {
    "regions": [("W", "West"), ("C", "Central")],
    "trades": [
        (1, "W", "GOLD", 2000000.0, "2026-01-15"),
        (2, "C", "SILVER", 100000.0, "2026-06-01"),
        (3, "W", "GOLD", 500000.0, "2026-09-01"),
    ],
}


def build_fixture(path, variant="a"):
    """Create a SQLite database at `path` with the trades/regions schema.

    Args:
        path: the file path to create.
        variant: "a" or "b", selecting the data set.

    Returns:
        The path as a string.
    """
    data = _VARIANT_A if variant == "a" else _VARIANT_B
    conn = sqlite3.connect(path)
    try:
        conn.executescript(_SCHEMA)
        conn.executemany("INSERT INTO regions VALUES (?, ?)", data["regions"])
        conn.executemany(
            "INSERT INTO trades VALUES (?, ?, ?, ?, ?)", data["trades"])
        conn.commit()
    finally:
        conn.close()
    return str(path)