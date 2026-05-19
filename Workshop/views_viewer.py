"""
Manufacturing Ecosystem — Data Viewer
======================================
Reads from the Manufaktur database and displays all analytics views
and the fact_production table using pandas DataFrames.

Requirements:
    pip install sqlalchemy sqlalchemy-utils psycopg2-binary python-dotenv pandas
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy_utils import create_database, database_exists

load_dotenv()

# ── Connection config ────────────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "Manufaktur")

DB_URL_ADMIN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
DB_URL       = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Analytics views defined in Manufaktur.sql
ANALYTICS_VIEWS = [
    "kpi_monthly",
    "clustering_skill_performance",
    "supply_forecast",
    "financial_health_monthly",
    "trend_mom_growth",
]

# ── DB setup ─────────────────────────────────────────────────────────────────

def ensure_database() -> None:
    if not database_exists(DB_URL):
        print(f"[DB] '{DB_NAME}' not found — creating...")
        create_database(DB_URL)
    else:
        print(f"[DB] '{DB_NAME}' exists.")


def get_engine():
    return create_engine(DB_URL)


# ── Data access ───────────────────────────────────────────────────────────────

def fetch_available_views(engine) -> pd.DataFrame:
    """Return all view names in the public schema."""
    query = text("""
        SELECT table_name AS view_name
        FROM   information_schema.views
        WHERE  table_schema = 'public'
        ORDER  BY table_name
    """)
    return pd.read_sql(query, engine)


def fetch_view(engine, view_name: str, limit: int = 5) -> pd.DataFrame:
    """Fetch up to `limit` rows from a named view."""
    query = text(f'SELECT * FROM "{view_name}" LIMIT :lim')
    return pd.read_sql(query, engine, params={"lim": limit})


def fetch_all_analytics_views(engine, limit: int = 5) -> dict[str, pd.DataFrame]:
    """
    Fetch data from every view in ANALYTICS_VIEWS.
    Each view gets its own connection so one failure doesn't abort the rest.
    """
    results = {}
    for view_name in ANALYTICS_VIEWS:
        try:
            results[view_name] = fetch_view(engine, view_name, limit)
        except Exception as exc:
            print(f"[WARN] Could not query '{view_name}': {exc}")
            results[view_name] = pd.DataFrame()   # empty placeholder
    return results


def fetch_fact_production(engine, limit: int = 5) -> pd.DataFrame:
    query = text('SELECT * FROM fact_production ORDER BY production_id LIMIT :lim')
    return pd.read_sql(query, engine, params={"lim": limit})


# ── Display helper ────────────────────────────────────────────────────────────

def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ensure_database()
    engine = get_engine()

    try:
        # 1. Show all views present in the database
        _section("ALL VIEWS IN PUBLIC SCHEMA")
        df_views = fetch_available_views(engine)
        print(df_views.to_string(index=False))

        # 2. Analytics views
        _section("ANALYTICS VIEW CONTENTS (first 5 rows each)")
        view_data = fetch_all_analytics_views(engine, limit=5)

        for view_name, df in view_data.items():
            print(f"\n--- {view_name} ---")
            if df.empty:
                print("  (no data or view unavailable)")
            else:
                pd.set_option("display.max_columns", None)
                pd.set_option("display.width", 200)
                print(df.to_string(index=False))

        # 3. Core fact table
        _section("FACT PRODUCTION (first 5 rows)")
        df_fact = fetch_fact_production(engine, limit=5)
        print(df_fact.to_string(index=False))

    except Exception as exc:
        print(f"[ERROR] {exc}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()