BEGIN;

-- ==========================================
-- 1. BUILD DIMENSIONS (REBUILD SAFE)
-- ==========================================

TRUNCATE dim_employee;
INSERT INTO dim_employee
SELECT 
    e.employee_id,
    e.full_name,
    e.skill_level,
    e.hire_date,
    d.division_id,
    d.division_name
FROM employees e
JOIN divisions d ON e.division_id = d.division_id;

TRUNCATE dim_product;
INSERT INTO dim_product
SELECT 
    product_id,
    product_name,
    product_type,
    material,
    standard_weight
FROM products;

TRUNCATE dim_workshop;
INSERT INTO dim_workshop
SELECT
    workshop_id,
    workshop_name,
    location,
    furnace_type
FROM workshops;

TRUNCATE dim_date;
INSERT INTO dim_date
SELECT DISTINCT
    TO_CHAR(production_date,'YYYYMMDD')::int          AS date_id,
    production_date                                    AS full_date,
    EXTRACT(YEAR    FROM production_date)::int         AS year,
    EXTRACT(QUARTER FROM production_date)::int         AS quarter,
    EXTRACT(MONTH   FROM production_date)::int         AS month,
    TO_CHAR(production_date,'Month')                   AS month_name,
    EXTRACT(WEEK    FROM production_date)::int         AS week_of_year,
    EXTRACT(DOW     FROM production_date)::int         AS day_of_week,
    TO_CHAR(production_date,'Day')                     AS day_name,
    EXTRACT(DAY     FROM production_date)::int         AS day,
    CASE WHEN EXTRACT(DOW FROM production_date) IN (0,6)
         THEN TRUE ELSE FALSE END                      AS is_weekend
FROM production_logs;


-- ==========================================
-- 2. BUILD FACT TABLE (JOIN = STREAM LOOKUP)
-- ==========================================

ALTER TABLE fact_production
ADD COLUMN IF NOT EXISTS production_datetime TIMESTAMP;

TRUNCATE TABLE fact_production;

INSERT INTO fact_production (
    production_id,
    date_id,
    production_datetime,
    employee_id,
    product_id,
    workshop_id,
    quantity,
    defects,
    production_minutes,
    defect_rate,
    productivity
)
SELECT
    l.log_id AS production_id,

    -- DATE KEY (surrogate for dimension join)
    TO_CHAR(l.production_date, 'YYYYMMDD')::INT AS date_id,

    -- FULL TIMESTAMP (for analytics / VAR)
    l.production_date AS production_datetime,

    -- FOREIGN KEYS
    l.employee_id,
    l.product_id,
    l.workshop_id,

    -- MEASURES
    l.quantity,
    l.defects,
    l.production_minutes,

    -- DERIVED METRICS (safe division)
    ROUND(
        (l.defects::NUMERIC / NULLIF(l.quantity, 0)),
        4
    ) AS defect_rate,

    ROUND(
        (l.quantity::NUMERIC / NULLIF(l.production_minutes, 0)),
        4
    ) AS productivity

FROM production_logs l
INNER JOIN dim_employee de 
    ON l.employee_id = de.employee_id
INNER JOIN dim_product dp  
    ON l.product_id  = dp.product_id
INNER JOIN dim_workshop dw 
    ON l.workshop_id = dw.workshop_id;

COMMIT;