BEGIN;

-- =====================================================
-- EMPLOYEE CUBES
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS cube_employee_daily;
CREATE MATERIALIZED VIEW cube_employee_daily AS
SELECT
    full_date,
    employee_id,
    division_name,
    skill_level,

    COUNT(*)                         AS total_runs,
    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(defect_rate)                 AS avg_defect_rate,
    AVG(productivity_index)          AS avg_productivity,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    full_date,
    employee_id,
    division_name,
    skill_level;


DROP MATERIALIZED VIEW IF EXISTS cube_employee_weekly;
CREATE MATERIALIZED VIEW cube_employee_weekly AS
SELECT
    year,
    week_of_year,
    employee_id,
    division_name,
    skill_level,

    COUNT(*)                         AS total_runs,
    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(defect_rate)                 AS avg_defect_rate,
    AVG(productivity_index)          AS avg_productivity,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    week_of_year,
    employee_id,
    division_name,
    skill_level;


DROP MATERIALIZED VIEW IF EXISTS cube_employee_monthly;
CREATE MATERIALIZED VIEW cube_employee_monthly AS
SELECT
    year,
    month,
    employee_id,
    division_name,
    skill_level,

    COUNT(*)                         AS total_runs,
    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(defect_rate)                 AS avg_defect_rate,
    AVG(productivity_index)          AS avg_productivity,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    month,
    employee_id,
    division_name,
    skill_level;


-- =====================================================
-- PRODUCT CUBES
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS cube_product_daily;
CREATE MATERIALIZED VIEW cube_product_daily AS
SELECT
    full_date,
    product_id,
    product_name,
    product_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    full_date,
    product_id,
    product_name,
    product_type;


DROP MATERIALIZED VIEW IF EXISTS cube_product_weekly;
CREATE MATERIALIZED VIEW cube_product_weekly AS
SELECT
    year,
    week_of_year,
    product_id,
    product_name,
    product_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    week_of_year,
    product_id,
    product_name,
    product_type;


DROP MATERIALIZED VIEW IF EXISTS cube_product_monthly;
CREATE MATERIALIZED VIEW cube_product_monthly AS
SELECT
    year,
    month,
    product_id,
    product_name,
    product_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    month,
    product_id,
    product_name,
    product_type;


-- =====================================================
-- WORKSHOP CUBES
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS cube_workshop_daily;
CREATE MATERIALIZED VIEW cube_workshop_daily AS
SELECT
    full_date,
    workshop_id,
    workshop_name,
    city,
    furnace_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    full_date,
    workshop_id,
    workshop_name,
    city,
    furnace_type;


DROP MATERIALIZED VIEW IF EXISTS cube_workshop_weekly;
CREATE MATERIALIZED VIEW cube_workshop_weekly AS
SELECT
    year,
    week_of_year,
    workshop_id,
    workshop_name,
    city,
    furnace_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    week_of_year,
    workshop_id,
    workshop_name,
    city,
    furnace_type;


DROP MATERIALIZED VIEW IF EXISTS cube_workshop_monthly;
CREATE MATERIALIZED VIEW cube_workshop_monthly AS
SELECT
    year,
    month,
    workshop_id,
    workshop_name,
    city,
    furnace_type,

    SUM(actual_quantity)             AS total_output,
    SUM(defects)                     AS total_defects,
    AVG(productivity_index)          AS avg_productivity,
    AVG(defect_rate)                 AS avg_defect_rate,
    SUM(good_output)                 AS good_output

FROM vw_fact_production_analytics
GROUP BY
    year,
    month,
    workshop_id,
    workshop_name,
    city,
    furnace_type;


-- =====================================================
-- FORECASTING CUBES
-- =====================================================

DROP MATERIALIZED VIEW IF EXISTS cube_forecast_daily;
CREATE MATERIALIZED VIEW cube_forecast_daily AS
SELECT
    full_date,

    SUM(actual_quantity) AS total_output,
    SUM(defects)         AS total_defects,

    AVG(productivity_index) AS avg_productivity,
    AVG(defect_rate)        AS avg_defect_rate

FROM vw_fact_production_analytics
GROUP BY full_date;


DROP MATERIALIZED VIEW IF EXISTS cube_forecast_weekly;
CREATE MATERIALIZED VIEW cube_forecast_weekly AS
SELECT
    year,
    week_of_year,

    SUM(actual_quantity) AS total_output,
    SUM(defects)         AS total_defects,

    AVG(productivity_index) AS avg_productivity,
    AVG(defect_rate)        AS avg_defect_rate

FROM vw_fact_production_analytics
GROUP BY
    year,
    week_of_year;


DROP MATERIALIZED VIEW IF EXISTS cube_forecast_monthly;
CREATE MATERIALIZED VIEW cube_forecast_monthly AS
SELECT
    year,
    month,

    SUM(actual_quantity) AS total_output,
    SUM(defects)         AS total_defects,

    AVG(productivity_index) AS avg_productivity,
    AVG(defect_rate)        AS avg_defect_rate

FROM vw_fact_production_analytics
GROUP BY
    year,
    month;

COMMIT;