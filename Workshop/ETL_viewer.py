"""
Manufacturing Ecosystem — Full Database Inspector
==================================================
1. Lists every table and view in the public schema with their columns/types
2. Previews the first 10 rows of every table and view

Requirements:
    pip install sqlalchemy sqlalchemy-utils psycopg2-binary python-dotenv pandas
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy_utils import create_database, database_exists

load_dotenv()

# ── Connection config ─────────────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "Manufaktur")

DB_URL_ADMIN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
DB_URL       = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

pd.set_option("display.max_columns",  None)
pd.set_option("display.max_rows",     None)
pd.set_option("display.width",        220)
pd.set_option("display.max_colwidth", 40)

# ── DB helpers ────────────────────────────────────────────────────────────────

def ensure_database() -> None:
    if not database_exists(DB_URL):
        print(f"[DB] '{DB_NAME}' not found — creating...")
        create_database(DB_URL)
    else:
        print(f"[DB] '{DB_NAME}' exists.")


def get_engine():
    return create_engine(DB_URL)


# ── Schema inspection ─────────────────────────────────────────────────────────

def fetch_object_names(engine) -> tuple[list[str], list[str]]:
    """Return (tables, views) in the public schema, alphabetically sorted."""
    with engine.connect() as conn:
        tables = [
            r[0] for r in conn.execute(text("""
                SELECT table_name
                FROM   information_schema.tables
                WHERE  table_schema = 'public'
                  AND  table_type   = 'BASE TABLE'
                ORDER  BY table_name
            """))
        ]
        views = [
            r[0] for r in conn.execute(text("""
                SELECT table_name
                FROM   information_schema.views
                WHERE  table_schema = 'public'
                ORDER  BY table_name
            """))
        ]
    return tables, views


def fetch_columns(engine) -> dict[str, list[tuple[str, str]]]:
    """
    Return {object_name: [(column_name, data_type), ...]}
    for every table and view in the public schema.
    """
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT table_name,
                   column_name,
                   data_type
            FROM   information_schema.columns
            WHERE  table_schema = 'public'
            ORDER  BY table_name, ordinal_position
        """)).mappings()

        schema: dict[str, list] = {}
        for row in rows:
            schema.setdefault(row["table_name"], []).append(
                (row["column_name"], row["data_type"])
            )
    return schema


# ── Data preview ──────────────────────────────────────────────────────────────

def fetch_preview(engine, name: str, limit: int = 10) -> pd.DataFrame:
    """Fetch the first `limit` rows of a table or view."""
    with engine.connect() as conn:
        return pd.read_sql(
            text(f'SELECT * FROM "{name}" LIMIT :lim'),
            conn,
            params={"lim": limit},
        )


# ── Display helpers ───────────────────────────────────────────────────────────

def _banner(title: str, char: str = "=", width: int = 70) -> None:
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def print_schema(tables: list[str], views: list[str],
                 schema: dict[str, list[tuple[str, str]]]) -> None:
    """Print a structured schema summary for all tables and views."""
    _banner("SCHEMA SUMMARY")
    print(f"  Tables : {len(tables)}")
    print(f"  Views  : {len(views)}")

    for kind, names in [("TABLE", tables), ("VIEW", views)]:
        for name in names:
            cols = schema.get(name, [])
            print(f"\n  [{kind}] {name}  ({len(cols)} columns)")
            for col, dtype in cols:
                print(f"      {col:<35} {dtype}")


def print_previews(engine, tables: list[str], views: list[str],
                   limit: int = 10) -> None:
    """Print first `limit` rows for every table and view."""
    _banner(f"DATA PREVIEW  —  first {limit} rows per object")

    for kind, names in [("TABLE", tables), ("VIEW", views)]:
        for name in names:
            print(f"\n{'─' * 70}")
            print(f"  [{kind}] {name}")
            print(f"{'─' * 70}")
            try:
                df = fetch_preview(engine, name, limit)
                if df.empty:
                    print("  (no rows)")
                else:
                    print(df.to_string(index=False))
            except Exception as exc:
                print(f"  ERROR: {exc}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ensure_database()
    engine = get_engine()

    try:
        tables, views = fetch_object_names(engine)
        schema        = fetch_columns(engine)

        # 1. Schema overview
        print_schema(tables, views, schema)

        # 2. Row previews
        print_previews(engine, tables, views, limit=10)

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()