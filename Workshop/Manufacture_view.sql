-- 1. STRUCTURE VIEW 
CREATE OR REPLACE VIEW vw_fact_production_structure AS
SELECT
    column_name,
    data_type,
    is_nullable,
    ordinal_position
FROM information_schema.columns
WHERE table_name = 'fact_production'
  AND table_schema = 'public'
ORDER BY ordinal_position;


-- ==========================================
-- 2. ANALYTICS VIEW
-- ==========================================
CREATE OR REPLACE VIEW vw_fact_production_analytics AS
SELECT
    -- IDENTIFIERS
    f.production_id,

    -- TIME FEATURES (FIX: include full_date)
    f.date_id,
    d.full_date,
    d.year::int,
    d.month::int,
    d.day::int,
    d.week_of_year::int,
    d.day_of_week::int,
    d.is_weekend,

    -- EMPLOYEE FEATURES
    e.skill_level,
    e.division_name,

    -- PRODUCT FEATURES
    p.product_name,
    p.product_type,
    p.material,
    p.standard_weight,

    -- WORKSHOP FEATURES
    w.location,
    w.furnace_type,

    -- NUMERIC FEATURES
    f.quantity,
    f.defects,
    f.production_minutes,
    f.defect_rate,
    f.productivity,

    -- DERIVED FEATURES
    (f.quantity - f.defects) AS good_output,
    CASE WHEN f.defects > 0 THEN 1 ELSE 0 END AS has_defect

FROM fact_production f
JOIN dim_date d      ON f.date_id = d.date_id
JOIN dim_employee e  ON f.employee_id = e.employee_id
JOIN dim_product p   ON f.product_id  = p.product_id
JOIN dim_workshop w  ON f.workshop_id = w.workshop_id;


-- ==========================================
-- 3. CLUSTERING VIEW
-- ==========================================
CREATE OR REPLACE VIEW vw_employee_clustering AS
SELECT
    f.employee_id,

    e.skill_level,
    e.division_name,

    COUNT(*)                    AS total_jobs,

    -- normalized metrics
    AVG(f.quantity)             AS avg_output,
    AVG(f.defect_rate)          AS avg_defect_rate,
    AVG(f.productivity)         AS avg_productivity,

    -- workload
    SUM(f.production_minutes)   AS total_minutes,

    -- efficiency
    SUM(f.quantity - f.defects) AS good_output,
    ROUND(
        SUM(f.defects)::numeric / NULLIF(SUM(f.quantity),0),
        4
    ) AS defect_ratio

FROM fact_production f
JOIN dim_employee e ON f.employee_id = e.employee_id

GROUP BY
    f.employee_id,
    e.skill_level,
    e.division_name;


-- ==========================================
-- 4. TIMESERIES VIEW
-- ==========================================
CREATE OR REPLACE VIEW vw_fact_production_timeseries AS
SELECT
    f.date_id,
    d.full_date,
    d.year,
    d.month,
    d.week_of_year,

    -- grouping keys
    f.product_id,
    f.workshop_id,

    -- aggregated signals
    SUM(f.quantity)     AS total_output,
    SUM(f.defects)      AS total_defects,
    AVG(f.productivity) AS avg_productivity,
    AVG(f.defect_rate)  AS avg_defect_rate

FROM fact_production f
JOIN dim_date d ON f.date_id = d.date_id

GROUP BY
    f.date_id,
    d.full_date,
    d.year,
    d.month,
    d.week_of_year,
    f.product_id,
    f.workshop_id;


-- ==========================================
-- 5. OPTIONAL: COMPATIBILITY VIEW
-- ==========================================
CREATE OR REPLACE VIEW production_overview AS
SELECT * FROM vw_fact_production_analytics;