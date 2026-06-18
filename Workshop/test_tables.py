import os
import sys

# Ensure the parent directory is in sys.path so we can import Workshop
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from Workshop import tables
    print("[SUCCESS] Successfully imported Workshop.tables")
except Exception as e:
    print(f"[ERROR] Failed to import Workshop.tables: {e}")
    sys.exit(1)

def run_tests():
    # 1. Test lazy loading of a table
    print("\n--- 1. Testing lazy loading of dim_date ---")
    try:
        df_date = tables.dim_date
        print(f"dim_date loaded successfully. Shape: {df_date.shape}")
        print("First 3 rows:")
        print(df_date.head(3))
    except Exception as e:
        print(f"[FAIL] Error loading dim_date: {e}")

    # 2. Test lazy loading of a view
    print("\n--- 2. Testing lazy loading of kpi_monthly ---")
    try:
        df_kpi = tables.kpi_monthly
        print(f"kpi_monthly loaded successfully. Shape: {df_kpi.shape}")
        print("First 3 rows:")
        print(df_kpi.head(3))
    except Exception as e:
        print(f"[FAIL] Error loading kpi_monthly: {e}")

    # 3. Test lazy loading of a cube (materialized view)
    print("\n--- 3. Testing lazy loading of cube_employee_monthly ---")
    try:
        df_cube = tables.cube_employee_monthly
        print(f"cube_employee_monthly loaded successfully. Shape: {df_cube.shape}")
        print("First 3 rows:")
        print(df_cube.head(3))
    except Exception as e:
        print(f"[FAIL] Error loading cube_employee_monthly: {e}")

    # 4. Check __dir__ content
    print("\n--- 4. Checking module directory and dynamic list ---")
    available_attrs = dir(tables)
    print(f"Number of available attributes: {len(available_attrs)}")
    print(f"Is 'dim_date' listed? {'dim_date' in available_attrs}")
    print(f"Is 'cube_employee_weekly' listed? {'cube_employee_weekly' in available_attrs}")
    print(f"Is 'non_existent_table' listed? {'non_existent_table' in available_attrs}")

    # 5. Check eager loading (load_all)
    print("\n--- 5. Testing load_all() (Eager loading of all objects) ---")
    try:
        tables.load_all()
        print("[SUCCESS] load_all() executed without error.")
        # Verify another table is now in the cache / module namespace
        df_prod = tables.fact_production
        print(f"fact_production loaded. Shape: {df_prod.shape}")
    except Exception as e:
        print(f"[FAIL] Error running load_all(): {e}")

if __name__ == "__main__":
    run_tests()
