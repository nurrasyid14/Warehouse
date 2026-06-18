-- ==========================================
-- 1. STRUCTURE VIEW
-- ==========================================

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

    -- TIME
    f.date_id,
    d.full_date,
    d.year,
    d.month,
    d.day,
    d.week_of_year,
    d.day_of_week,
    d.is_weekend,
    d.season,

    -- EMPLOYEE
    f.employee_id,
    e.skill_level,
    e.division_name,
    e.gender,
    e.placement_city,

    -- PRODUCT
    f.product_id,
    p.product_name,
    p.product_type,
    p.material,
    p.standard_weight,

    -- WORKSHOP
    f.workshop_id,
    w.workshop_name,
    w.city,
    w.location_abbr,
    w.furnace_type,
    w.capacity_per_run,

    -- FACT MEASURES
    f.planned_quantity,
    f.actual_quantity,
    f.defects,
    f.production_minutes,
    f.defect_rate,
    f.productivity_index,

    -- DERIVED METRICS
    (f.actual_quantity - f.defects) AS good_output,

    ROUND(
        f.actual_quantity::NUMERIC /
        NULLIF(f.planned_quantity, 0),
        4
    ) AS achievement_rate,

    CASE
        WHEN f.defects > 0 THEN 1
        ELSE 0
    END AS has_defect

FROM fact_production f
JOIN dim_date d
    ON f.date_id = d.date_id
JOIN dim_employee e
    ON f.employee_id = e.employee_id
JOIN dim_product p
    ON f.product_id = p.product_id
JOIN dim_workshop w
    ON f.workshop_id = w.workshop_id;


-- ==========================================
-- 3. CLUSTERING VIEW
-- ==========================================

CREATE OR REPLACE VIEW vw_employee_clustering AS
SELECT

    f.employee_id,

    e.skill_level,
    e.division_name,
    e.gender,

    COUNT(*) AS total_jobs,

    AVG(f.actual_quantity) AS avg_output,

    AVG(f.defect_rate) AS avg_defect_rate,

    AVG(f.productivity_index) AS avg_productivity,

    SUM(f.production_minutes) AS total_minutes,

    SUM(
        f.actual_quantity - f.defects
    ) AS good_output,

    ROUND(
        SUM(f.defects)::NUMERIC /
        NULLIF(SUM(f.actual_quantity), 0),
        4
    ) AS defect_ratio,

    ROUND(
        SUM(f.actual_quantity)::NUMERIC /
        NULLIF(SUM(f.planned_quantity), 0),
        4
    ) AS achievement_ratio

FROM fact_production f
JOIN dim_employee e
    ON f.employee_id = e.employee_id

GROUP BY
    f.employee_id,
    e.skill_level,
    e.division_name,
    e.gender;


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

    f.product_id,
    f.workshop_id,

    SUM(f.actual_quantity) AS total_output,

    SUM(f.defects) AS total_defects,

    AVG(f.productivity_index) AS avg_productivity,

    AVG(f.defect_rate) AS avg_defect_rate,

    SUM(
        f.actual_quantity - f.defects
    ) AS good_output

FROM fact_production f
JOIN dim_date d
    ON f.date_id = d.date_id

GROUP BY
    f.date_id,
    d.full_date,
    d.year,
    d.month,
    d.week_of_year,
    f.product_id,
    f.workshop_id;


-- ==========================================
-- 5. FORECASTING VIEW
-- ==========================================

CREATE OR REPLACE VIEW vw_production_forecast_base AS
SELECT

    d.full_date,

    f.product_id,

    f.workshop_id,

    SUM(f.actual_quantity) AS total_output,

    SUM(f.defects) AS total_defects,

    AVG(f.productivity_index) AS productivity,

    AVG(f.defect_rate) AS defect_rate

FROM fact_production f
JOIN dim_date d
    ON f.date_id = d.date_id

GROUP BY
    d.full_date,
    f.product_id,
    f.workshop_id;


-- ==========================================
-- 6. COMPATIBILITY VIEW
-- ==========================================

CREATE OR REPLACE VIEW production_overview AS
SELECT *
FROM vw_fact_production_analytics;