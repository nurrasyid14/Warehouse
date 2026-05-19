-- ====================================================================
-- MANUFACTURING PRODUCTION ECOSYSTEM — COMPLETE DATABASE
-- ====================================================================
-- Description : Full manufacturing simulation DB for 2025
--               incl. workshops, employees, production runs,
--               materials, cashflow, star-schema DW, analytics views
-- Database    : PostgreSQL 14+
-- Calendar    : 2025 A.D. (Gregorian)
--
-- EXECUTION ORDER (all in one transaction per part):
--   1. Part 1 — Workshops, Divisions, Products, Employees
--   2. Part 2 — Date Dimension, Materials, Vendors, Inventory, Supply
--   3. Part 3 — Production Runs (DO block, ~3,000–4,500 rows)
--   4. Part 4 — Cashflow, Fact/Dim tables, Analytics Views, Indexes
--
-- ID CONVENTIONS
--   Workshop    : WS-YYYYMMDDhhmm-SSS
--   Employee    : EM-YYYYMMDDhhmm-SSS
--   Production  : PR-YYYYMMDDhhmm-SSS
--   Location    : nbg=Nuremberg | ber=Berlin | muc=Munich | ham=Hamburg
-- ====================================================================

-- ============================================================
-- MANUFACTURING PRODUCTION ECOSYSTEM — FULL DATABASE
-- Calendar Year: 2025 | PostgreSQL
-- ============================================================

BEGIN;

-- ============================================================
-- DROP ALL TABLES (clean slate)
-- ============================================================
DROP TABLE IF EXISTS kpi_analytics         CASCADE;
DROP TABLE IF EXISTS financial_health      CASCADE;
DROP TABLE IF EXISTS supply_forecast       CASCADE;
DROP TABLE IF EXISTS clustering_view       CASCADE;
DROP TABLE IF EXISTS fact_demographics     CASCADE;
DROP TABLE IF EXISTS fact_production       CASCADE;
DROP TABLE IF EXISTS fact_cashflow         CASCADE;
DROP TABLE IF EXISTS inventory             CASCADE;
DROP TABLE IF EXISTS material_supply       CASCADE;
DROP TABLE IF EXISTS vendors               CASCADE;
DROP TABLE IF EXISTS materials             CASCADE;
DROP TABLE IF EXISTS dim_date              CASCADE;
DROP TABLE IF EXISTS dim_employee          CASCADE;
DROP TABLE IF EXISTS dim_product           CASCADE;
DROP TABLE IF EXISTS dim_workshop          CASCADE;
DROP TABLE IF EXISTS production_runs       CASCADE;
DROP TABLE IF EXISTS employees             CASCADE;
DROP TABLE IF EXISTS workshops             CASCADE;
DROP TABLE IF EXISTS products              CASCADE;
DROP TABLE IF EXISTS divisions             CASCADE;

-- ============================================================
-- 1. WORKSHOPS
-- ID: WS-YYYYMMDDhhmm-SSS | Location = city abbrev
-- ============================================================
CREATE TABLE workshops (
    workshop_id       VARCHAR(24) PRIMARY KEY,
    workshop_name     TEXT        NOT NULL,
    city              TEXT        NOT NULL,
    location_abbr     VARCHAR(5)  NOT NULL,  -- nbg, ber, muc, ham
    furnace_type      TEXT        NOT NULL,  -- Coal, Gas, Induction, Electric Arc, Plasma
    capacity_per_run  INT         NOT NULL   -- max units per production run
);

INSERT INTO workshops (workshop_id, workshop_name, city, location_abbr, furnace_type, capacity_per_run) VALUES
('WS-202501010800-001','Alpha Forge',       'Nuremberg','nbg','Coal',        120),
('WS-202501010800-002','Beta Smelter',      'Nuremberg','nbg','Gas',         150),
('WS-202501010800-003','Gamma Cast',        'Nuremberg','nbg','Induction',   100),
('WS-202501010800-004','Delta Arc',         'Berlin',   'ber','Electric Arc',200),
('WS-202501010800-005','Epsilon Plasma',    'Berlin',   'ber','Plasma',       80),
('WS-202501010800-006','Zeta Forge',        'Berlin',   'ber','Coal',        110),
('WS-202501010800-007','Eta Smelter',       'Munich',   'muc','Gas',         160),
('WS-202501010800-008','Theta Cast',        'Munich',   'muc','Induction',    90),
('WS-202501010800-009','Iota Arc',          'Munich',   'muc','Electric Arc',180),
('WS-202501010800-010','Kappa Plasma',      'Hamburg',  'ham','Plasma',       70),
('WS-202501010800-011','Lambda Forge',      'Hamburg',  'ham','Coal',        130),
('WS-202501010800-012','Mu Smelter',        'Hamburg',  'ham','Gas',         140),
('WS-202501010800-013','Nu Cast',           'Nuremberg','nbg','Induction',   105),
('WS-202501010800-014','Xi Arc',            'Berlin',   'ber','Electric Arc',195),
('WS-202501010800-015','Omicron Plasma',    'Munich',   'muc','Plasma',       85);

-- ============================================================
-- 2. DIVISIONS
-- ============================================================
CREATE TABLE divisions (
    division_id   VARCHAR(12) PRIMARY KEY,
    division_name TEXT NOT NULL
);

INSERT INTO divisions (division_id, division_name) VALUES
('DIV-001','Forging'),
('DIV-002','Finishing'),
('DIV-003','Quality Control'),
('DIV-004','Logistics'),
('DIV-005','Maintenance'),
('DIV-006','Assembly'),
('DIV-007','Casting'),
('DIV-008','Grinding'),
('DIV-009','Polishing'),
('DIV-010','Heat Treatment'),
('DIV-011','Welding'),
('DIV-012','Inspection'),
('DIV-013','Packaging'),
('DIV-014','Dispatch'),
('DIV-015','Engineering');

-- ============================================================
-- 3. PRODUCTS
-- ============================================================
CREATE TABLE products (
    product_id      VARCHAR(12) PRIMARY KEY,
    product_name    TEXT,
    product_type    TEXT,
    material        TEXT,
    standard_weight NUMERIC(10,2),
    unit_price      NUMERIC(10,2)
);

INSERT INTO products (product_id, product_name, product_type, material, standard_weight, unit_price) VALUES
('PRD-001','Anvil',      'Heavy',      'Iron',         67.55, 245.00),
('PRD-002','Nail',       'Small',      'Steel',        12.25,   3.50),
('PRD-003','Horseshoe',  'Equine',     'Iron',         34.75,  28.00),
('PRD-004','Bolt',       'Fastener',   'Steel',        30.09,   5.20),
('PRD-005','Bracket',    'Structural', 'Steel',        76.28,  42.00),
('PRD-006','Chisel',     'Tool',       'Carbon Steel', 70.90,  38.00),
('PRD-007','Hammer',     'Tool',       'Iron',         90.30,  55.00),
('PRD-008','Gear',       'Mechanical', 'Steel',        17.82,  75.00),
('PRD-009','Spring',     'Elastic',    'Spring Steel', 47.97,  32.00),
('PRD-010','Coupling',   'Connector',  'Steel',        12.68,  18.00);

-- ============================================================
-- 4. EMPLOYEES
-- ID: EM-YYYYMMDDhhmm-SSS
-- Name distribution: Western / Middle-Eastern / Indian
-- ============================================================
CREATE TABLE employees (
    employee_id     VARCHAR(24) PRIMARY KEY,
    full_name       TEXT        NOT NULL,
    gender          VARCHAR(10) NOT NULL,
    origin_region   TEXT        NOT NULL,  -- Western European, Middle Eastern, Indian
    placement_city  TEXT        NOT NULL,
    workshop_id     VARCHAR(24) REFERENCES workshops(workshop_id),
    skill_level     SMALLINT    NOT NULL CHECK (skill_level BETWEEN 1 AND 5),
    telephone       TEXT        NOT NULL,
    email           TEXT        NOT NULL,
    division_id     VARCHAR(12) REFERENCES divisions(division_id),
    hire_date       DATE        NOT NULL
);

INSERT INTO employees (employee_id, full_name, gender, origin_region, placement_city, workshop_id, skill_level, telephone, email, division_id, hire_date) VALUES
-- Western European names
('EM-202501010900-001','Thomas Mueller',      'Male',  'Western European','Nuremberg','WS-202501010800-001',4,'+49 911 1234567','thmu@gmail.com',       'DIV-001','2018-03-15'),
('EM-202501010900-002','Sophie Wagner',       'Female','Western European','Nuremberg','WS-202501010800-001',3,'+49 911 2345678','sowa@yahoo.com',       'DIV-002','2019-06-20'),
('EM-202501010900-003','Hans Becker',         'Male',  'Western European','Nuremberg','WS-202501010800-002',5,'+49 911 3456789','habe@gmail.com',       'DIV-003','2016-01-10'),
('EM-202501010900-004','Anna Schmidt',        'Female','Western European','Nuremberg','WS-202501010800-002',2,'+49 911 4567890','ansc@ymail.com',       'DIV-004','2021-09-05'),
('EM-202501010900-005','Karl Fischer',        'Male',  'Western European','Nuremberg','WS-202501010800-003',3,'+49 911 5678901','kafi@xmail.com',       'DIV-005','2020-02-14'),
('EM-202501010900-006','Laura Weber',         'Female','Western European','Berlin',   'WS-202501010800-004',4,'+49 30 1234567', 'lawe@gmail.com',       'DIV-006','2017-07-22'),
('EM-202501010900-007','Peter Hoffmann',      'Male',  'Western European','Berlin',   'WS-202501010800-004',5,'+49 30 2345678', 'peho@yahoo.com',       'DIV-007','2015-04-18'),
('EM-202501010900-008','Maria Schäfer',       'Female','Western European','Berlin',   'WS-202501010800-005',3,'+49 30 3456789', 'masc@gmail.com',       'DIV-008','2022-11-30'),
('EM-202501010900-009','Josef Koch',          'Male',  'Western European','Berlin',   'WS-202501010800-005',2,'+49 30 4567890', 'joko@ymail.com',       'DIV-009','2023-01-08'),
('EM-202501010900-010','Clara Braun',         'Female','Western European','Berlin',   'WS-202501010800-006',4,'+49 30 5678901', 'clbr@xmail.com',       'DIV-010','2018-08-25'),
('EM-202501010900-011','Friedrich Wolf',      'Male',  'Western European','Munich',   'WS-202501010800-007',5,'+49 89 1234567', 'frwo@gmail.com',       'DIV-011','2016-05-12'),
('EM-202501010900-012','Ingrid Schulz',       'Female','Western European','Munich',   'WS-202501010800-007',3,'+49 89 2345678', 'insc@yahoo.com',       'DIV-012','2020-10-17'),
('EM-202501010900-013','Markus Zimmermann',   'Male',  'Western European','Munich',   'WS-202501010800-008',4,'+49 89 3456789', 'mazi@gmail.com',       'DIV-013','2019-03-28'),
('EM-202501010900-014','Helga Krüger',        'Female','Western European','Munich',   'WS-202501010800-008',2,'+49 89 4567890', 'hekr@ymail.com',       'DIV-014','2022-07-14'),
('EM-202501010900-015','Werner Lange',        'Male',  'Western European','Munich',   'WS-202501010800-009',3,'+49 89 5678901', 'wela@xmail.com',       'DIV-015','2021-12-03'),
('EM-202501010900-016','Gertrude Neumann',    'Female','Western European','Hamburg',  'WS-202501010800-010',4,'+49 40 1234567', 'gene@gmail.com',       'DIV-001','2017-02-19'),
('EM-202501010900-017','Heinrich Schwarz',    'Male',  'Western European','Hamburg',  'WS-202501010800-010',5,'+49 40 2345678', 'hesc@yahoo.com',       'DIV-002','2015-09-07'),
('EM-202501010900-018','Elsa Richter',        'Female','Western European','Hamburg',  'WS-202501010800-011',3,'+49 40 3456789', 'elri@gmail.com',       'DIV-003','2020-04-22'),
('EM-202501010900-019','Dieter Klein',        'Male',  'Western European','Hamburg',  'WS-202501010800-011',2,'+49 40 4567890', 'dikl@ymail.com',       'DIV-004','2023-06-11'),
('EM-202501010900-020','Brigitte Weiß',       'Female','Western European','Hamburg',  'WS-202501010800-012',4,'+49 40 5678901', 'brwe@xmail.com',       'DIV-005','2018-11-29'),
-- Middle-Eastern names
('EM-202501010900-021','Hassan Al-Rashid',    'Male',  'Middle Eastern',  'Nuremberg','WS-202501010800-001',3,'+49 911 6789012','haal@gmail.com',       'DIV-006','2019-05-16'),
('EM-202501010900-022','Fatima Al-Amin',      'Female','Middle Eastern',  'Nuremberg','WS-202501010800-002',4,'+49 911 7890123','faal@yahoo.com',       'DIV-007','2017-08-30'),
('EM-202501010900-023','Omar Khalil',         'Male',  'Middle Eastern',  'Nuremberg','WS-202501010800-003',2,'+49 911 8901234','omkh@gmail.com',       'DIV-008','2022-01-24'),
('EM-202501010900-024','Layla Mansouri',      'Female','Middle Eastern',  'Berlin',   'WS-202501010800-004',5,'+49 30 6789012', 'lama@ymail.com',       'DIV-009','2016-03-09'),
('EM-202501010900-025','Tariq Saleh',         'Male',  'Middle Eastern',  'Berlin',   'WS-202501010800-005',3,'+49 30 7890123', 'tasa@xmail.com',       'DIV-010','2020-07-17'),
('EM-202501010900-026','Noor Al-Farsi',       'Female','Middle Eastern',  'Berlin',   'WS-202501010800-006',4,'+49 30 8901234', 'noal@gmail.com',       'DIV-011','2018-10-05'),
('EM-202501010900-027','Yusuf Abboud',        'Male',  'Middle Eastern',  'Munich',   'WS-202501010800-007',2,'+49 89 6789012', 'yuab@yahoo.com',       'DIV-012','2021-04-14'),
('EM-202501010900-028','Amira Nassar',        'Female','Middle Eastern',  'Munich',   'WS-202501010800-008',5,'+49 89 7890123', 'amna@gmail.com',       'DIV-013','2015-12-20'),
('EM-202501010900-029','Kareem Qureshi',      'Male',  'Middle Eastern',  'Munich',   'WS-202501010800-009',3,'+49 89 8901234', 'kaqu@ymail.com',       'DIV-014','2019-09-03'),
('EM-202501010900-030','Rania Ibrahim',       'Female','Middle Eastern',  'Hamburg',  'WS-202501010800-010',4,'+49 40 6789012', 'raib@xmail.com',       'DIV-015','2017-06-28'),
('EM-202501010900-031','Ahmad Petrov',        'Male',  'Middle Eastern',  'Hamburg',  'WS-202501010800-011',2,'+420 602 345678','ahpe@gmail.com',       'DIV-001','2022-02-15'),
('EM-202501010900-032','Soraya Okafor',       'Female','Middle Eastern',  'Hamburg',  'WS-202501010800-012',3,'+420 603 456789','sook@yahoo.com',       'DIV-002','2020-08-09'),
('EM-202501010900-033','Bilal Zahra',         'Male',  'Middle Eastern',  'Nuremberg','WS-202501010800-013',5,'+49 911 9012345','biza@gmail.com',       'DIV-003','2016-11-18'),
('EM-202501010900-034','Dalia Fontaine',      'Female','Middle Eastern',  'Berlin',   'WS-202501010800-014',4,'+49 30 9012345', 'dafo@ymail.com',       'DIV-004','2018-04-07'),
('EM-202501010900-035','Samir Eriksson',      'Male',  'Middle Eastern',  'Munich',   'WS-202501010800-015',3,'+49 89 9012345', 'saer@xmail.com',       'DIV-005','2021-07-22'),
-- Indian names
('EM-202501010900-036','Priya Sharma',        'Female','Indian',          'Nuremberg','WS-202501010800-001',4,'+49 911 0123456','prsh@gmail.com',       'DIV-006','2019-01-14'),
('EM-202501010900-037','Raj Kapoor',          'Male',  'Indian',          'Nuremberg','WS-202501010800-002',5,'+49 911 1234560','raka@yahoo.com',       'DIV-007','2016-06-25'),
('EM-202501010900-038','Anjali Mehta',        'Female','Indian',          'Nuremberg','WS-202501010800-003',2,'+49 911 2345601','anme@gmail.com',       'DIV-008','2022-10-12'),
('EM-202501010900-039','Vikram Patel',        'Male',  'Indian',          'Berlin',   'WS-202501010800-004',3,'+49 30 0123456', 'vipa@ymail.com',       'DIV-009','2020-03-30'),
('EM-202501010900-040','Deepika Iyer',        'Female','Indian',          'Berlin',   'WS-202501010800-005',4,'+49 30 1234560', 'deiy@xmail.com',       'DIV-010','2018-07-06'),
('EM-202501010900-041','Arjun Reddy',         'Male',  'Indian',          'Berlin',   'WS-202501010800-006',5,'+49 30 2345601', 'arre@gmail.com',       'DIV-011','2015-10-15'),
('EM-202501010900-042','Kavya Nair',          'Female','Indian',          'Munich',   'WS-202501010800-007',3,'+49 89 0123456', 'kana@yahoo.com',       'DIV-012','2021-02-08'),
('EM-202501010900-043','Rohit Joshi',         'Male',  'Indian',          'Munich',   'WS-202501010800-008',2,'+49 89 1234560', 'rojo@gmail.com',       'DIV-013','2023-05-19'),
('EM-202501010900-044','Sunita Bose',         'Female','Indian',          'Munich',   'WS-202501010800-009',4,'+49 89 2345601', 'subo@ymail.com',       'DIV-014','2017-09-01'),
('EM-202501010900-045','Manish Singh',        'Male',  'Indian',          'Hamburg',  'WS-202501010800-010',3,'+49 40 0123456', 'masi@xmail.com',       'DIV-015','2020-12-24'),
('EM-202501010900-046','Shreya Gupta',        'Female','Indian',          'Hamburg',  'WS-202501010800-011',5,'+49 40 1234560', 'shgu@gmail.com',       'DIV-001','2016-04-17'),
('EM-202501010900-047','Rahul Kumar',         'Male',  'Indian',          'Hamburg',  'WS-202501010800-012',4,'+49 40 2345601', 'raku@yahoo.com',       'DIV-002','2018-02-11'),
('EM-202501010900-048','Pooja Verma',         'Female','Indian',          'Nuremberg','WS-202501010800-013',2,'+421 901 234567','pove@gmail.com',       'DIV-003','2022-08-28'),
('EM-202501010900-049','Sanjay Malhotra',     'Male',  'Indian',          'Berlin',   'WS-202501010800-014',3,'+421 902 345678','sama@ymail.com',       'DIV-004','2019-11-05'),
('EM-202501010900-050','Meera Pillai',        'Female','Indian',          'Munich',   'WS-202501010800-015',4,'+43 676 1234567','mepi@xmail.com',       'DIV-005','2021-06-16');

COMMIT;

-- ============================================================
-- PART 2: DATE DIMENSION, MATERIALS, INVENTORY, PRODUCTION RUNS
-- ============================================================

BEGIN;

-- ============================================================
-- 5. DATE DIMENSION
-- Covers full year 2025 with working-day logic
-- ============================================================
CREATE TABLE dim_date (
    date_id        INT PRIMARY KEY,   -- YYYYMMDD
    full_date      DATE NOT NULL,
    year           SMALLINT NOT NULL,
    month          SMALLINT NOT NULL,
    month_name     VARCHAR(12) NOT NULL,
    day            SMALLINT NOT NULL,
    week_of_year   SMALLINT NOT NULL,
    day_of_week    SMALLINT NOT NULL, -- 0=Sun,1=Mon,...,6=Sat
    day_name       VARCHAR(12) NOT NULL,
    is_weekend     BOOLEAN NOT NULL,
    season         VARCHAR(10) NOT NULL, -- Winter,Spring,Summer,Autumn
    is_working_day BOOLEAN NOT NULL
);

-- Generate all 365 days of 2025
INSERT INTO dim_date (date_id, full_date, year, month, month_name, day, week_of_year,
                      day_of_week, day_name, is_weekend, season, is_working_day)
SELECT
    TO_CHAR(d,'YYYYMMDD')::INT,
    d,
    EXTRACT(YEAR    FROM d)::SMALLINT,
    EXTRACT(MONTH   FROM d)::SMALLINT,
    TO_CHAR(d,'Month'),
    EXTRACT(DAY     FROM d)::SMALLINT,
    EXTRACT(WEEK    FROM d)::SMALLINT,
    EXTRACT(DOW     FROM d)::SMALLINT,
    TO_CHAR(d,'Day'),
    EXTRACT(DOW FROM d) IN (0,6),
    CASE
        WHEN EXTRACT(MONTH FROM d) IN (12,1,2)  THEN 'Winter'
        WHEN EXTRACT(MONTH FROM d) IN (3,4,5)   THEN 'Spring'
        WHEN EXTRACT(MONTH FROM d) IN (6,7,8)   THEN 'Summer'
        ELSE                                          'Autumn'
    END,
    -- Working day logic (exclude Sundays, public holidays, special periods)
    CASE
        -- Always exclude Sundays (DOW=0)
        WHEN EXTRACT(DOW FROM d) = 0 THEN FALSE
        -- Jan 1: New Year
        WHEN d = '2025-01-01' THEN FALSE
        -- March: Good Friday 2025 = Apr 18 → wait, Easter 2025 = Apr 20
        -- Good Friday = Apr 18, Easter Monday = Apr 21
        WHEN d IN ('2025-04-18','2025-04-21') THEN FALSE
        -- October: Halloween week Oct 27–31
        WHEN d BETWEEN '2025-10-27' AND '2025-10-31' THEN FALSE
        -- December: Dec 24–31
        WHEN d BETWEEN '2025-12-24' AND '2025-12-31' THEN FALSE
        ELSE TRUE
    END
FROM generate_series('2025-01-01'::DATE, '2025-12-31'::DATE, '1 day') AS gs(d);

-- ============================================================
-- 6. MATERIALS
-- ============================================================
CREATE TABLE materials (
    material_id    VARCHAR(12) PRIMARY KEY,
    material_name  TEXT        NOT NULL,
    unit           VARCHAR(20) NOT NULL,  -- kg, ton, piece, litre
    cost_per_unit  NUMERIC(10,2) NOT NULL,
    reorder_level  NUMERIC(10,2) NOT NULL -- reorder when stock drops below this
);

INSERT INTO materials (material_id, material_name, unit, cost_per_unit, reorder_level) VALUES
('MAT-001','Iron Ore',          'ton',   85.00, 50.00),
('MAT-002','Steel Billets',     'ton',  420.00, 30.00),
('MAT-003','Carbon Steel Bar',  'ton',  540.00, 20.00),
('MAT-004','Spring Steel Coil', 'ton',  610.00, 15.00),
('MAT-005','Coal',              'ton',   75.00, 40.00),
('MAT-006','Natural Gas',       'litre',  0.80, 5000.00),
('MAT-007','Induction Medium',  'litre',  1.20, 2000.00),
('MAT-008','Flux Powder',       'kg',     3.50, 200.00),
('MAT-009','Coolant Fluid',     'litre',  2.10, 1000.00),
('MAT-010','Lubricant Oil',     'litre',  4.80,  500.00);

-- ============================================================
-- 7. VENDORS
-- ============================================================
CREATE TABLE vendors (
    vendor_id   VARCHAR(12) PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    country     TEXT NOT NULL,
    material_id VARCHAR(12) REFERENCES materials(material_id)
);

INSERT INTO vendors (vendor_id, vendor_name, country, material_id) VALUES
('VND-001','EuroOre GmbH',         'Germany',        'MAT-001'),
('VND-002','SteelBillets AG',      'Austria',         'MAT-002'),
('VND-003','CarbonTech GmbH',      'Czech Republic',  'MAT-003'),
('VND-004','SpringMetal s.r.o.',   'Slovakia',        'MAT-004'),
('VND-005','CoalSupply GmbH',      'Germany',         'MAT-005'),
('VND-006','GasLogistik AG',       'Austria',         'MAT-006'),
('VND-007','InduMedien GmbH',      'Germany',         'MAT-007'),
('VND-008','FluxTech s.r.o.',      'Czech Republic',  'MAT-008'),
('VND-009','CoolFlow AG',          'Austria',         'MAT-009'),
('VND-010','LubriChem GmbH',       'Germany',         'MAT-010');

-- ============================================================
-- 8. INVENTORY (per workshop × material, updated ~every 2 weeks)
-- ============================================================
CREATE TABLE inventory (
    inventory_id   SERIAL PRIMARY KEY,
    workshop_id    VARCHAR(24) REFERENCES workshops(workshop_id),
    material_id    VARCHAR(12) REFERENCES materials(material_id),
    current_stock  NUMERIC(12,2) NOT NULL,
    last_updated   DATE NOT NULL
);

-- Each of the 15 workshops gets stock for all 10 materials
-- Restocked on Jan-6, Jan-20, Feb-3, Feb-17 etc (every ~2 weeks)
-- Seeding with representative initial stock values
INSERT INTO inventory (workshop_id, material_id, current_stock, last_updated)
SELECT w.workshop_id, m.material_id,
       ROUND((RANDOM() * 80 + 20)::NUMERIC, 2) AS current_stock,
       '2025-01-06'::DATE
FROM workshops w CROSS JOIN materials m;

-- ============================================================
-- 9. MATERIAL SUPPLY (restock events, every ~2 weeks per workshop)
-- ============================================================
CREATE TABLE material_supply (
    supply_id      SERIAL PRIMARY KEY,
    workshop_id    VARCHAR(24) REFERENCES workshops(workshop_id),
    material_id    VARCHAR(12) REFERENCES materials(material_id),
    vendor_id      VARCHAR(12) REFERENCES vendors(vendor_id),
    supply_date    DATE NOT NULL,
    quantity       NUMERIC(10,2) NOT NULL,
    unit_cost      NUMERIC(10,2) NOT NULL,
    total_cost     NUMERIC(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED
);

-- Insert ~biweekly restocking for a representative sample (Jan–Dec 2025)
-- Restock dates: 6th and 20th of each month
INSERT INTO material_supply (workshop_id, material_id, vendor_id, supply_date, quantity, unit_cost)
SELECT
    w.workshop_id,
    m.material_id,
    v.vendor_id,
    rs.supply_date,
    ROUND((RANDOM() * 40 + 20)::NUMERIC, 2),
    m.cost_per_unit * (1 + (RANDOM() * 0.1 - 0.05))::NUMERIC
FROM workshops w
CROSS JOIN materials m
JOIN vendors v ON v.material_id = m.material_id
CROSS JOIN (
    SELECT unnest(ARRAY[
        '2025-01-06','2025-01-20','2025-02-03','2025-02-17',
        '2025-03-03','2025-03-17','2025-03-31','2025-04-14',
        '2025-04-28','2025-05-12','2025-05-26','2025-06-09',
        '2025-06-23','2025-07-07','2025-07-21','2025-08-04',
        '2025-08-18','2025-09-01','2025-09-15','2025-09-29',
        '2025-10-13','2025-11-03','2025-11-17','2025-12-01',
        '2025-12-15'
    ]::DATE[]) AS supply_date
) rs;

COMMIT;

-- ============================================================
-- PART 3: PRODUCTION RUNS FACT TABLE
-- ID: PR-YYYYMMDDhhmm-SSS
-- 10–19 runs per working day, seasonal productivity
-- ============================================================

BEGIN;

CREATE TABLE production_runs (
    production_id      VARCHAR(24) PRIMARY KEY,  -- PR-YYYYMMDDhhmm-SSS
    date_id            INT         NOT NULL REFERENCES dim_date(date_id),
    production_date    DATE        NOT NULL,
    production_time    TIME        NOT NULL,
    employee_id        VARCHAR(24) NOT NULL REFERENCES employees(employee_id),
    workshop_id        VARCHAR(24) NOT NULL REFERENCES workshops(workshop_id),
    product_id         VARCHAR(12) NOT NULL REFERENCES products(product_id),
    planned_quantity   INT         NOT NULL,
    actual_quantity    INT         NOT NULL,
    defects            INT         NOT NULL DEFAULT 0,
    production_minutes INT         NOT NULL,
    defect_rate        NUMERIC(6,4) GENERATED ALWAYS AS
                           (ROUND(defects::NUMERIC / NULLIF(actual_quantity,0), 4)) STORED,
    productivity_index NUMERIC(8,4) GENERATED ALWAYS AS
                           (ROUND(actual_quantity::NUMERIC / NULLIF(production_minutes,0), 4)) STORED
);

-- ============================================================
-- GENERATE PRODUCTION RUNS FOR ALL WORKING DAYS 2025
-- Seasonal productivity multipliers:
--   Winter (Dec–Feb): 0.75–0.85
--   Spring (Mar–May): 0.85–0.95
--   Summer (Jun–Aug): 0.95–1.10
--   Autumn (Sep–Nov): 0.85–0.95
-- 10–19 runs per day, spread 06:00–22:00
-- ============================================================

DO $$
DECLARE
    v_date          DATE;
    v_date_id       INT;
    v_season        TEXT;
    v_run_count     INT;
    v_run_idx       INT;
    v_prod_id       TEXT;
    v_emp_id        TEXT;
    v_ws_id         TEXT;
    v_prd_id        TEXT;
    v_hour          INT;
    v_minute        INT;
    v_time          TIME;
    v_planned       INT;
    v_seasonal_mult NUMERIC;
    v_actual        INT;
    v_defects       INT;
    v_minutes       INT;
    v_seq           INT := 1;
    v_daily_seq     INT;
    employees_arr   TEXT[];
    workshops_arr   TEXT[];
    products_arr    TEXT[];
BEGIN
    -- Load arrays
    SELECT ARRAY_AGG(employee_id ORDER BY employee_id) INTO employees_arr FROM employees;
    SELECT ARRAY_AGG(workshop_id ORDER BY workshop_id) INTO workshops_arr FROM workshops;
    SELECT ARRAY_AGG(product_id  ORDER BY product_id)  INTO products_arr  FROM products;

    FOR v_date, v_date_id, v_season IN
        SELECT full_date, date_id, season
        FROM dim_date
        WHERE is_working_day = TRUE
          AND year = 2025
        ORDER BY full_date
    LOOP
        -- 10–19 runs per day
        v_run_count := 10 + (RANDOM() * 9)::INT;

        -- Seasonal productivity multiplier
        v_seasonal_mult := CASE v_season
            WHEN 'Winter' THEN 0.75 + RANDOM() * 0.10
            WHEN 'Spring' THEN 0.85 + RANDOM() * 0.10
            WHEN 'Summer' THEN 0.95 + RANDOM() * 0.15
            WHEN 'Autumn' THEN 0.85 + RANDOM() * 0.10
            ELSE 0.90
        END;

        v_daily_seq := 1;

        FOR v_run_idx IN 1..v_run_count LOOP
            -- Spread across 06:00–22:00
            v_hour   := 6 + ((v_run_idx - 1) * 16 / v_run_count)::INT;
            v_minute := (RANDOM() * 59)::INT;
            v_time   := MAKE_TIME(v_hour, v_minute, 0);

            -- Pick employee, workshop, product (cycle through arrays)
            v_emp_id := employees_arr[1 + ((v_seq - 1) % ARRAY_LENGTH(employees_arr,1))];
            v_ws_id  := workshops_arr[1 + ((v_seq - 1) % ARRAY_LENGTH(workshops_arr,1))];
            v_prd_id := products_arr[1 + ((v_seq - 1) % ARRAY_LENGTH(products_arr,1))];

            -- Planned quantity 20–80
            v_planned := 20 + (RANDOM() * 60)::INT;

            -- Actual = planned × seasonal multiplier (some variance)
            v_actual  := GREATEST(1, (v_planned * v_seasonal_mult * (0.90 + RANDOM() * 0.20))::INT);

            -- Defects: 0–8% of actual
            v_defects := (v_actual * RANDOM() * 0.08)::INT;

            -- Production time 60–300 minutes
            v_minutes := 60 + (RANDOM() * 240)::INT;

            -- Build ID: PR-YYYYMMDDhhmm-SSS
            v_prod_id := 'PR-' || TO_CHAR(v_date,'YYYYMMDD') ||
                         TO_CHAR(v_time,'HH24MI') || '-' ||
                         LPAD(v_daily_seq::TEXT, 3, '0');

            INSERT INTO production_runs (
                production_id, date_id, production_date, production_time,
                employee_id, workshop_id, product_id,
                planned_quantity, actual_quantity, defects, production_minutes
            ) VALUES (
                v_prod_id, v_date_id, v_date, v_time,
                v_emp_id, v_ws_id, v_prd_id,
                v_planned, v_actual, v_defects, v_minutes
            )
            ON CONFLICT (production_id) DO NOTHING;

            v_seq      := v_seq + 1;
            v_daily_seq := v_daily_seq + 1;
        END LOOP;
    END LOOP;
END;
$$;

COMMIT;

-- ============================================================
-- PART 4: CASHFLOW, FACT TABLES, ANALYTICS VIEWS
-- ============================================================

BEGIN;

-- ============================================================
-- 10. CASHFLOW TABLE
-- Categories: Product Sales, Material Acquisition,
--   Workshop Maintenance, Employee Payroll, Utility/Energy
-- ============================================================
CREATE TABLE fact_cashflow (
    cashflow_id      SERIAL PRIMARY KEY,
    date_id          INT         NOT NULL REFERENCES dim_date(date_id),
    cashflow_date    DATE        NOT NULL,
    category         TEXT        NOT NULL,  -- see above
    flow_type        VARCHAR(10) NOT NULL,  -- Inflow / Outflow
    workshop_id      VARCHAR(24) REFERENCES workshops(workshop_id),
    amount           NUMERIC(14,2) NOT NULL,
    description      TEXT
);

-- ── PAYROLL (Outflow, 28th of every month, based on 50 employees)
-- Average monthly salary ~€3,200 per employee
INSERT INTO fact_cashflow (date_id, cashflow_date, category, flow_type, workshop_id, amount, description)
SELECT
    TO_CHAR(pay_date,'YYYYMMDD')::INT,
    pay_date,
    'Employee Payroll',
    'Outflow',
    NULL,
    50 * 3200.00 * (1 + (RANDOM()*0.05 - 0.025)),  -- small variance
    'Monthly payroll for all employees'
FROM (
    SELECT (TO_DATE('2025-' || LPAD(m::TEXT,2,'0') || '-28','YYYY-MM-DD')) AS pay_date
    FROM generate_series(1,12) m
    WHERE TO_DATE('2025-' || LPAD(m::TEXT,2,'0') || '-28','YYYY-MM-DD') NOT IN (
        -- skip if that date is a non-working day (approx: we keep it simple, payroll always on 28th)
        SELECT '2025-12-28'::DATE  -- Dec 28 is during shutdown — shift to Dec 23
    )
) payroll_dates;

-- ── MATERIAL ACQUISITION (Outflow, from material_supply)
INSERT INTO fact_cashflow (date_id, cashflow_date, category, flow_type, workshop_id, amount, description)
SELECT
    TO_CHAR(ms.supply_date,'YYYYMMDD')::INT,
    ms.supply_date,
    'Material Acquisition',
    'Outflow',
    ms.workshop_id,
    SUM(ms.total_cost),
    'Biweekly material restock'
FROM material_supply ms
GROUP BY ms.supply_date, ms.workshop_id;

-- ── PRODUCT SALES (Inflow, daily, derived from production output × unit price)
INSERT INTO fact_cashflow (date_id, cashflow_date, category, flow_type, workshop_id, amount, description)
SELECT
    pr.date_id,
    pr.production_date,
    'Product Sales',
    'Inflow',
    pr.workshop_id,
    SUM(pr.actual_quantity * p.unit_price * (1 - pr.defect_rate)) AS revenue,
    'Daily product sales revenue'
FROM production_runs pr
JOIN products p ON pr.product_id = p.product_id
GROUP BY pr.date_id, pr.production_date, pr.workshop_id;

-- ── WORKSHOP MAINTENANCE (Outflow, monthly per workshop, ~€2,500–4,000 each)
INSERT INTO fact_cashflow (date_id, cashflow_date, category, flow_type, workshop_id, amount, description)
SELECT
    TO_CHAR(maint_date,'YYYYMMDD')::INT,
    maint_date,
    'Workshop Maintenance',
    'Outflow',
    w.workshop_id,
    ROUND((2500 + RANDOM() * 1500)::NUMERIC, 2),
    'Monthly workshop maintenance cost'
FROM workshops w
CROSS JOIN (
    SELECT DATE_TRUNC('month', gs)::DATE + 14 AS maint_date
    FROM generate_series('2025-01-01'::TIMESTAMP, '2025-12-31'::TIMESTAMP, '1 month') gs
) maint
WHERE maint_date NOT IN ('2025-12-24','2025-12-25','2025-12-26','2025-12-27',
                          '2025-12-28','2025-12-29','2025-12-30','2025-12-31');

-- ── UTILITY / ENERGY (Outflow, weekly per workshop, seasonal variation)
-- Winter higher, Summer lower
INSERT INTO fact_cashflow (date_id, cashflow_date, category, flow_type, workshop_id, amount, description)
SELECT
    TO_CHAR(util_date,'YYYYMMDD')::INT,
    util_date,
    'Utility / Energy',
    'Outflow',
    w.workshop_id,
    ROUND((
        CASE
            WHEN EXTRACT(MONTH FROM util_date) IN (12,1,2) THEN 1800 + RANDOM()*400  -- Winter
            WHEN EXTRACT(MONTH FROM util_date) IN (3,4,5)  THEN 1300 + RANDOM()*300  -- Spring
            WHEN EXTRACT(MONTH FROM util_date) IN (6,7,8)  THEN 900  + RANDOM()*200  -- Summer
            ELSE                                                 1400 + RANDOM()*300  -- Autumn
        END
    )::NUMERIC, 2),
    'Weekly utility and energy cost'
FROM workshops w
CROSS JOIN (
    SELECT gs::DATE AS util_date
    FROM generate_series('2025-01-06'::TIMESTAMP,'2025-12-22'::TIMESTAMP,'7 days') gs
) util_weeks
WHERE util_date NOT BETWEEN '2025-12-24' AND '2025-12-31';

-- ============================================================
-- 11. DIM TABLES (Star Schema)
-- ============================================================

-- dim_employee
CREATE TABLE dim_employee AS
SELECT e.employee_id, e.full_name, e.gender, e.origin_region,
       e.placement_city, e.skill_level, e.hire_date,
       d.division_id, d.division_name
FROM employees e JOIN divisions d ON e.division_id = d.division_id;

-- dim_product
CREATE TABLE dim_product AS
SELECT product_id, product_name, product_type, material, standard_weight, unit_price
FROM products;

-- dim_workshop
CREATE TABLE dim_workshop AS
SELECT workshop_id, workshop_name, city, location_abbr, furnace_type, capacity_per_run
FROM workshops;

-- ============================================================
-- 12. FACT_PRODUCTION (aligned with production_runs)
-- ============================================================
CREATE TABLE fact_production AS
SELECT
    pr.production_id,
    pr.date_id,
    pr.production_date,
    pr.employee_id,
    pr.workshop_id,
    pr.product_id,
    pr.planned_quantity,
    pr.actual_quantity,
    pr.defects,
    pr.production_minutes,
    pr.defect_rate,
    pr.productivity_index,
    dd.season,
    dd.month,
    dd.week_of_year,
    dd.is_weekend
FROM production_runs pr
JOIN dim_date dd ON pr.date_id = dd.date_id;

-- ============================================================
-- 13. FACT_DEMOGRAPHICS (employee activity summary)
-- ============================================================
CREATE TABLE fact_demographics AS
SELECT
    e.employee_id,
    e.full_name,
    e.gender,
    e.origin_region,
    e.placement_city,
    e.skill_level,
    e.division_id,
    COUNT(pr.production_id)          AS total_runs,
    SUM(pr.actual_quantity)          AS total_output,
    SUM(pr.production_minutes)       AS total_minutes_worked,
    ROUND(SUM(pr.production_minutes)::NUMERIC / 60, 2) AS total_hours_worked,
    ROUND(AVG(pr.defect_rate),4)     AS avg_defect_rate,
    ROUND(AVG(pr.productivity_index),4) AS avg_productivity
FROM employees e
LEFT JOIN production_runs pr ON e.employee_id = pr.employee_id
GROUP BY e.employee_id, e.full_name, e.gender, e.origin_region,
         e.placement_city, e.skill_level, e.division_id;

-- ============================================================
-- 14. ANALYTICS VIEWS
-- ============================================================

-- A) KPI VIEW: overall performance by month
CREATE VIEW kpi_monthly AS
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    dd.season,
    COUNT(fp.production_id)              AS total_runs,
    SUM(fp.actual_quantity)              AS total_output,
    SUM(fp.planned_quantity)             AS total_planned,
    ROUND(AVG(fp.defect_rate),4)         AS avg_defect_rate,
    ROUND(AVG(fp.productivity_index),4)  AS avg_productivity,
    ROUND(SUM(fp.actual_quantity)::NUMERIC / NULLIF(SUM(fp.planned_quantity),0), 4) AS fulfillment_rate
FROM fact_production fp
JOIN dim_date dd ON fp.date_id = dd.date_id
GROUP BY dd.year, dd.month, dd.month_name, dd.season
ORDER BY dd.year, dd.month;

-- B) CLUSTERING VIEW: skill level vs performance
CREATE VIEW clustering_skill_performance AS
SELECT
    de.skill_level,
    de.division_id,
    COUNT(fp.production_id)              AS runs,
    ROUND(AVG(fp.actual_quantity),2)     AS avg_output,
    ROUND(AVG(fp.defect_rate),4)         AS avg_defect_rate,
    ROUND(AVG(fp.productivity_index),4)  AS avg_productivity
FROM fact_production fp
JOIN dim_employee de ON fp.employee_id = de.employee_id
GROUP BY de.skill_level, de.division_id
ORDER BY de.skill_level, de.division_id;

-- C) SUPPLY FORECAST VIEW: stock vs reorder level
CREATE VIEW supply_forecast AS
SELECT
    i.workshop_id,
    w.workshop_name,
    w.city,
    m.material_id,
    m.material_name,
    i.current_stock,
    m.reorder_level,
    i.last_updated,
    CASE WHEN i.current_stock <= m.reorder_level THEN TRUE ELSE FALSE END AS needs_restock,
    -- Estimated daily consumption = total supply in last 2 weeks / 14
    ROUND(COALESCE(cs.consumed_per_day, 0), 2) AS est_daily_consumption,
    CASE
        WHEN COALESCE(cs.consumed_per_day, 0) > 0
        THEN ROUND(i.current_stock / cs.consumed_per_day, 1)
        ELSE NULL
    END AS days_until_reorder
FROM inventory i
JOIN workshops  w ON i.workshop_id = w.workshop_id
JOIN materials  m ON i.material_id = m.material_id
LEFT JOIN (
    SELECT workshop_id, material_id,
           SUM(quantity) / 14.0 AS consumed_per_day
    FROM material_supply
    WHERE supply_date >= '2025-11-01'
    GROUP BY workshop_id, material_id
) cs ON cs.workshop_id = i.workshop_id AND cs.material_id = i.material_id;

-- D) FINANCIAL HEALTH VIEW: monthly P&L
CREATE VIEW financial_health_monthly AS
SELECT
    EXTRACT(YEAR  FROM cf.cashflow_date)::INT  AS year,
    EXTRACT(MONTH FROM cf.cashflow_date)::INT  AS month,
    TO_CHAR(cf.cashflow_date,'Month')          AS month_name,
    SUM(CASE WHEN flow_type = 'Inflow'  THEN amount ELSE 0 END)  AS total_revenue,
    SUM(CASE WHEN flow_type = 'Outflow' THEN amount ELSE 0 END)  AS total_expenses,
    SUM(CASE WHEN flow_type = 'Inflow'  THEN amount ELSE 0 END) -
    SUM(CASE WHEN flow_type = 'Outflow' THEN amount ELSE 0 END)  AS profit,
    SUM(CASE WHEN category = 'Employee Payroll'      THEN amount ELSE 0 END) AS payroll,
    SUM(CASE WHEN category = 'Material Acquisition'  THEN amount ELSE 0 END) AS material_cost,
    SUM(CASE WHEN category = 'Workshop Maintenance'  THEN amount ELSE 0 END) AS maintenance_cost,
    SUM(CASE WHEN category = 'Utility / Energy'      THEN amount ELSE 0 END) AS utility_cost,
    SUM(CASE WHEN category = 'Product Sales'         THEN amount ELSE 0 END) AS sales_revenue
FROM fact_cashflow cf
GROUP BY EXTRACT(YEAR FROM cf.cashflow_date), EXTRACT(MONTH FROM cf.cashflow_date),
         TO_CHAR(cf.cashflow_date,'Month')
ORDER BY year, month;

-- E) TREND ANALYSIS: month-over-month output growth
CREATE VIEW trend_mom_growth AS
WITH monthly AS (
    SELECT dd.year, dd.month,
           SUM(fp.actual_quantity) AS output
    FROM fact_production fp
    JOIN dim_date dd ON fp.date_id = dd.date_id
    GROUP BY dd.year, dd.month
)
SELECT
    year, month, output,
    LAG(output) OVER (ORDER BY year, month)                               AS prev_month_output,
    ROUND(
        (output - LAG(output) OVER (ORDER BY year, month))::NUMERIC
        / NULLIF(LAG(output) OVER (ORDER BY year, month), 0) * 100, 2
    )                                                                     AS mom_growth_pct
FROM monthly
ORDER BY year, month;

-- ============================================================
-- 15. INDEXES for performance
-- ============================================================
CREATE INDEX idx_pr_date       ON production_runs (production_date);
CREATE INDEX idx_pr_employee   ON production_runs (employee_id);
CREATE INDEX idx_pr_workshop   ON production_runs (workshop_id);
CREATE INDEX idx_pr_product    ON production_runs (product_id);
CREATE INDEX idx_cf_date       ON fact_cashflow   (cashflow_date);
CREATE INDEX idx_cf_category   ON fact_cashflow   (category);
CREATE INDEX idx_inv_workshop  ON inventory       (workshop_id);
CREATE INDEX idx_inv_material  ON inventory       (material_id);

COMMIT;