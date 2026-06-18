-- =====================================================
-- ETL.SQL
-- Manufacturing Data Warehouse ETL
-- =====================================================

BEGIN;

-- =====================================================
-- 1. DIMENSION TABLES
-- =====================================================

---

-- DIM_EMPLOYEE

---

TRUNCATE TABLE dim_employee CASCADE;

INSERT INTO dim_employee (
employee_id,
full_name,
gender,
placement_city,
skill_level,
hire_date,
division_id,
division_name
)
SELECT
e.employee_id,
e.full_name,
e.gender,
e.placement_city,
e.skill_level,
e.hire_date,
d.division_id,
d.division_name
FROM employees e
JOIN divisions d
ON e.division_id = d.division_id;

---

-- DIM_PRODUCT

---

TRUNCATE TABLE dim_product CASCADE;

INSERT INTO dim_product (
product_id,
product_name,
product_type,
material,
standard_weight
)
SELECT
product_id,
product_name,
product_type,
material,
standard_weight
FROM products;

---

-- DIM_WORKSHOP

---

TRUNCATE TABLE dim_workshop CASCADE;

INSERT INTO dim_workshop (
workshop_id,
workshop_name,
city,
location_abbr,
furnace_type,
capacity_per_run
)
SELECT
workshop_id,
workshop_name,
city,
location_abbr,
furnace_type,
capacity_per_run
FROM workshops;

---

-- DIM_DATE

---

TRUNCATE TABLE dim_date CASCADE;

INSERT INTO dim_date (
date_id,
full_date,
year,
month,
month_name,
day,
week_of_year,
day_of_week,
day_name,
is_weekend,
season,
is_working_day
)
SELECT DISTINCT
TO_CHAR(
    production_date,
    'YYYYMMDD'
)::INT                                      AS date_id,

production_date                             AS full_date,

EXTRACT(YEAR FROM production_date)::SMALLINT
                                            AS year,

EXTRACT(MONTH FROM production_date)::SMALLINT
                                            AS month,

TRIM(
    TO_CHAR(
        production_date,
        'Month'
    )
)                                           AS month_name,

EXTRACT(DAY FROM production_date)::SMALLINT
                                            AS day,

EXTRACT(WEEK FROM production_date)::SMALLINT
                                            AS week_of_year,

EXTRACT(DOW FROM production_date)::SMALLINT
                                            AS day_of_week,

TRIM(
    TO_CHAR(
        production_date,
        'Day'
    )
)                                           AS day_name,
CASE
    WHEN EXTRACT(DOW FROM production_date)
         IN (0,6)
    THEN TRUE
    ELSE FALSE
END                                         AS is_weekend,

CASE
    WHEN EXTRACT(MONTH FROM production_date)
         IN (12,1,2)
    THEN 'Winter'

    WHEN EXTRACT(MONTH FROM production_date)
         IN (3,4,5)
    THEN 'Spring'

    WHEN EXTRACT(MONTH FROM production_date)
         IN (6,7,8)
    THEN 'Summer'

    ELSE 'Autumn'
END                                         AS season,

CASE
    WHEN EXTRACT(DOW FROM production_date)
         IN (0,6)
    THEN FALSE
    ELSE TRUE
END                                         AS is_working_day
FROM production_logs;

-- =====================================================
-- 2. FACT TABLE
-- =====================================================

TRUNCATE TABLE fact_production;

INSERT INTO fact_production (

    production_id,

    date_id,
    employee_id,
    product_id,
    workshop_id,

    production_datetime,

    planned_quantity,
    actual_quantity,

    defects,
    production_minutes,

    defect_rate,
    productivity_index

)
SELECT

    pr.production_id,

    pr.date_id,

    pr.employee_id,
    pr.product_id,
    pr.workshop_id,

    (
        pr.production_date
        +
        pr.production_time
    )::timestamp,

    pr.planned_quantity,
    pr.actual_quantity,

    pr.defects,
    pr.production_minutes,

    pr.defect_rate,
    pr.productivity_index

FROM production_runs pr

INNER JOIN dim_date dd
    ON pr.date_id = dd.date_id

INNER JOIN dim_employee de
    ON pr.employee_id = de.employee_id

INNER JOIN dim_product dp
    ON pr.product_id = dp.product_id

INNER JOIN dim_workshop dw
    ON pr.workshop_id = dw.workshop_id;
    
-- =====================================================
-- 3. PERFORMANCE INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_fact_date
ON fact_production(date_id);

CREATE INDEX IF NOT EXISTS idx_fact_employee
ON fact_production(employee_id);

CREATE INDEX IF NOT EXISTS idx_fact_product
ON fact_production(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_workshop
ON fact_production(workshop_id);

CREATE INDEX IF NOT EXISTS idx_fact_datetime
ON fact_production(production_datetime);

COMMIT;
