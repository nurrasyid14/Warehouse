import os
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy_utils import create_database, database_exists, drop_database

load_dotenv()

# ── Connection config ────────────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")

DB_URL_ADMIN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
DB_URL       = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Analytics views defined in manufacturing_ecosystem.sql
ANALYTICS_VIEWS = [
    "kpi_monthly",
    "clustering_skill_performance",
    "supply_forecast",
    "financial_health_monthly",
    "trend_mom_growth",
]

# ── Database management ──────────────────────────────────────────────────────

def reset_database() -> None:
    """Drop (if exists) and recreate the target database."""
    admin_engine = create_engine(DB_URL_ADMIN, isolation_level="AUTOCOMMIT")
    with admin_engine.connect():          # just ping the admin connection
        pass

    if database_exists(DB_URL):
        drop_database(DB_URL)
        print(f"[RESET] Database '{DB_NAME}' dropped")

    create_database(DB_URL)
    print(f"[RESET] Database '{DB_NAME}' created")
    admin_engine.dispose()


# ── SQL execution ────────────────────────────────────────────────────────────

def run_sql_file(engine, path: str) -> None:
    """
    Execute a SQL file in a single transaction.
    The file may contain DO $$ ... $$ PL/pgSQL blocks, so we pass
    execution to the raw DBAPI connection via text() with no auto-escape.
    """
    print(f"\n[RUNNING] {path}")
    start = time.time()

    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    # Use a raw connection so PL/pgSQL DO blocks and multi-statement
    # scripts execute correctly without SQLAlchemy statement splitting.
    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"[DONE]    {path}  ({round(time.time() - start, 2)}s)")


# ── Validation ───────────────────────────────────────────────────────────────

def validate_tables(engine) -> None:
    """Print row counts for every table in the public schema."""
    inspector = inspect(engine)
    tables    = sorted(inspector.get_table_names(schema="public"))

    print(f"\n[VALIDATION] Tables found: {len(tables)}")
    print(f"{'Table':<30} {'Rows':>8}")
    print("-" * 40)

    with engine.connect() as conn:
        for table in tables:
            try:
                count = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{table}"')
                ).scalar()
                print(f"{table:<30} {count:>8,}")
            except Exception as exc:
                print(f"{table:<30}   ERROR: {exc}")


def validate_views(engine) -> None:
    """Print row counts for every analytics view.
    Each view gets its own connection so a missing view doesn't abort
    subsequent queries with InFailedSqlTransaction.
    """
    print(f"\n[VALIDATION] Analytics views:")
    print(f"{'View':<35} {'Rows':>8}")
    print("-" * 45)

    for view in ANALYTICS_VIEWS:
        # Fresh connection per view — isolates failures
        with engine.connect() as conn:
            try:
                count = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{view}"')
                ).scalar()
                print(f"{view:<35} {count:>8,}")
            except Exception as exc:
                # Strip noisy backtrace, keep just the core message
                print(f"{view:<35}   ERROR: {exc.orig if hasattr(exc, 'orig') else exc}")


# ── Preview helpers ──────────────────────────────────────────────────────────

def preview_fact_production(engine, limit: int = 5) -> None:
    """Show the first N rows of fact_production."""
    print(f"\n[PREVIEW] fact_production (first {limit} rows):")
    _print_query(engine, "SELECT * FROM fact_production ORDER BY production_id LIMIT :lim", {"lim": limit})


def preview_view(engine, view_name: str, limit: int = 5) -> None:
    """Show the first N rows of any view."""
    print(f"\n[PREVIEW] {view_name} (first {limit} rows):")
    _print_query(engine, f'SELECT * FROM "{view_name}" LIMIT :lim', {"lim": limit})


def _print_query(engine, sql: str, params: dict | None = None) -> None:
    with engine.connect() as conn:
        try:
            result = conn.execute(text(sql), params or {})
            rows   = result.fetchall()
            cols   = result.keys()

            if not rows:
                print("  (no rows returned)")
                return

            # Simple columnar print
            col_widths = {c: max(len(str(c)), *(len(str(r._mapping[c])) for r in rows)) for c in cols}
            header = "  " + "  ".join(str(c).ljust(col_widths[c]) for c in cols)
            print(header)
            print("  " + "-" * (len(header) - 2))
            for row in rows:
                print("  " + "  ".join(str(row._mapping[c]).ljust(col_widths[c]) for c in cols))

        except Exception as exc:
            print(f"  ERROR: {exc}")


# ── Main pipeline ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # 0. Clean start
    reset_database()

    engine = create_engine(DB_URL)

    # 1. Build entire schema: OLTP + DW + views + indexes (one file)
    run_sql_file(engine, "Manufaktur.sql")

    # 2. Validate all tables
    validate_tables(engine)

    # 3. Validate all analytics views
    validate_views(engine)

    # 4. Spot-check key fact table
    preview_fact_production(engine, limit=5)

    # 5. Spot-check every analytics view
    for view in ANALYTICS_VIEWS:
        preview_view(engine, view, limit=3)

    print("\n[PIPELINE] Complete.")
    engine.dispose()