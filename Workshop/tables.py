"""
Workshop Database Tables & Views Loader
=======================================
This module queries tables, views, and materialized views (cubes) from the
Manufaktur database using SQLAlchemy and returns them as pandas DataFrames.

It uses lazy loading (via module-level __getattr__) so that database queries
are only executed when a table or view is actually accessed/imported.
This prevents running 39 database queries on import.

To load all tables eagerly, you can call tables.load_all().
"""

import os
import sys
from typing import TYPE_CHECKING, List, Dict, Any
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables. First check current directory, then fallback to Workshop/
if not load_dotenv():
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)

DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5433")
DB_NAME     = os.getenv("DB_NAME", "Manufaktur")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# Lists of all database objects available in the public schema
TABLES: List[str] = [
    "dim_date",
    "dim_employee",
    "dim_product",
    "dim_workshop",
    "divisions",
    "employees",
    "fact_cashflow",
    "fact_demographics",
    "fact_production",
    "inventory",
    "material_supply",
    "materials",
    "production_runs",
    "products",
    "vendors",
    "workshops"
]

VIEWS: List[str] = [
    "clustering_skill_performance",
    "financial_health_monthly",
    "kpi_monthly",
    "production_overview",
    "supply_forecast",
    "trend_mom_growth",
    "vw_employee_clustering",
    "vw_fact_production_analytics",
    "vw_fact_production_structure",
    "vw_fact_production_timeseries",
    "vw_production_forecast_base"
]

CUBES: List[str] = [
    "cube_employee_daily",
    "cube_employee_weekly",
    "cube_employee_monthly",
    "cube_product_daily",
    "cube_product_weekly",
    "cube_product_monthly",
    "cube_workshop_daily",
    "cube_workshop_weekly",
    "cube_workshop_monthly",
    "cube_forecast_daily",
    "cube_forecast_weekly",
    "cube_forecast_monthly"
]

ALL_OBJECTS: List[str] = TABLES + VIEWS + CUBES
_OBJECT_SET = set(ALL_OBJECTS)

# Cache for loaded DataFrames to avoid querying multiple times
_cache: Dict[str, pd.DataFrame] = {}

def get_table(name: str) -> pd.DataFrame:
    """Fetch a table, view, or cube from the database as a pandas DataFrame."""
    if name not in _OBJECT_SET:
        raise ValueError(f"'{name}' is not a recognized table, view, or cube in this schema.")
    
    if name not in _cache:
        # Wrap table name in double quotes to handle any special naming/case sensitivity in PostgreSQL
        query = f'SELECT * FROM "{name}"'
        with engine.connect() as conn:
            _cache[name] = pd.read_sql(text(query), conn)
            
    return _cache[name]

def load_all() -> None:
    """Eagerly load all tables, views, and cubes into the module's globals."""
    module = sys.modules[__name__]
    for name in ALL_OBJECTS:
        df = get_table(name)
        setattr(module, name, df)

# Module-level __getattr__ allows lazy loading on demand
def __getattr__(name: str) -> pd.DataFrame:
    if name in _OBJECT_SET:
        df = get_table(name)
        # Store in the module's dict so subsequent accesses bypass __getattr__
        globals()[name] = df
        return df
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Module-level __dir__ returns the list of all available tables/views for inspection
def __dir__() -> List[str]:
    return sorted(list(globals().keys()) + ALL_OBJECTS)

# Type Hints for IDE autocompletion and static analysis tools
if TYPE_CHECKING:
    # Tables
    dim_date: pd.DataFrame
    dim_employee: pd.DataFrame
    dim_product: pd.DataFrame
    dim_workshop: pd.DataFrame
    divisions: pd.DataFrame
    employees: pd.DataFrame
    fact_cashflow: pd.DataFrame
    fact_demographics: pd.DataFrame
    fact_production: pd.DataFrame
    inventory: pd.DataFrame
    material_supply: pd.DataFrame
    materials: pd.DataFrame
    production_runs: pd.DataFrame
    products: pd.DataFrame
    vendors: pd.DataFrame
    workshops: pd.DataFrame

    # Views
    clustering_skill_performance: pd.DataFrame
    financial_health_monthly: pd.DataFrame
    kpi_monthly: pd.DataFrame
    production_overview: pd.DataFrame
    supply_forecast: pd.DataFrame
    trend_mom_growth: pd.DataFrame
    vw_employee_clustering: pd.DataFrame
    vw_fact_production_analytics: pd.DataFrame
    vw_fact_production_structure: pd.DataFrame
    vw_fact_production_timeseries: pd.DataFrame
    vw_production_forecast_base: pd.DataFrame

    # Materialized Views / Cubes
    cube_employee_daily: pd.DataFrame
    cube_employee_weekly: pd.DataFrame
    cube_employee_monthly: pd.DataFrame
    cube_product_daily: pd.DataFrame
    cube_product_weekly: pd.DataFrame
    cube_product_monthly: pd.DataFrame
    cube_workshop_daily: pd.DataFrame
    cube_workshop_weekly: pd.DataFrame
    cube_workshop_monthly: pd.DataFrame
    cube_forecast_daily: pd.DataFrame
    cube_forecast_weekly: pd.DataFrame
    cube_forecast_monthly: pd.DataFrame
