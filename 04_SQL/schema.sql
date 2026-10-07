-- Schema definition for EV Intelligence Platform Data Warehouse (ev_intelligence_dw)

-- Create database if it does not exist
CREATE DATABASE IF NOT EXISTS ev_intelligence_dw;
USE ev_intelligence_dw;

-- Drop tables if they exist to support clean rebuild (ordered by dependency to respect foreign keys)
DROP TABLE IF EXISTS fact_stock_prices;
DROP TABLE IF EXISTS fact_company_financials;
DROP TABLE IF EXISTS fact_economic;
DROP TABLE IF EXISTS fact_ev_metrics;
DROP TABLE IF EXISTS dim_category;
DROP TABLE IF EXISTS dim_mode;
DROP TABLE IF EXISTS dim_powertrain;
DROP TABLE IF EXISTS dim_company;
DROP TABLE IF EXISTS dim_time;
DROP TABLE IF EXISTS dim_country;

-- -------------------------------------------------------------
-- Dimension Tables
-- -------------------------------------------------------------

-- Dimension: dim_country
CREATE TABLE dim_country (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dimension: dim_time
CREATE TABLE dim_time (
    time_id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL UNIQUE,
    quarter INT DEFAULT NULL,
    month INT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dimension: dim_company
CREATE TABLE dim_company (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dimension: dim_powertrain
CREATE TABLE dim_powertrain (
    powertrain_id INT AUTO_INCREMENT PRIMARY KEY,
    powertrain VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dimension: dim_mode
CREATE TABLE dim_mode (
    mode_id INT AUTO_INCREMENT PRIMARY KEY,
    mode VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dimension: dim_category
CREATE TABLE dim_category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Fact Tables
-- -------------------------------------------------------------

-- Fact: fact_ev_metrics (stores sales and stock data)
CREATE TABLE fact_ev_metrics (
    ev_id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    time_id INT NOT NULL,
    powertrain_id INT DEFAULT NULL,
    mode_id INT DEFAULT NULL,
    category_id INT DEFAULT NULL,
    parameter VARCHAR(100) NOT NULL,
    value DOUBLE DEFAULT NULL,
    unit VARCHAR(50) DEFAULT NULL,
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id) ON DELETE CASCADE,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id) ON DELETE CASCADE,
    FOREIGN KEY (powertrain_id) REFERENCES dim_powertrain(powertrain_id) ON DELETE SET NULL,
    FOREIGN KEY (mode_id) REFERENCES dim_mode(mode_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES dim_category(category_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fact: fact_economic (stores GDP, Population, Electricity, Crude Oil Prices)
CREATE TABLE fact_economic (
    economic_id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    time_id INT NOT NULL,
    gdp DOUBLE DEFAULT NULL,
    population DOUBLE DEFAULT NULL,
    access_to_electricity DOUBLE DEFAULT NULL,
    crude_oil_price DOUBLE DEFAULT NULL,
    FOREIGN KEY (country_id) REFERENCES dim_country(country_id) ON DELETE CASCADE,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fact: fact_company_financials (stores annual income statements per company)
CREATE TABLE fact_company_financials (
    financial_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    time_id INT NOT NULL,
    revenue DOUBLE DEFAULT NULL,
    gross_profit DOUBLE DEFAULT NULL,
    operating_income DOUBLE DEFAULT NULL,
    net_income DOUBLE DEFAULT NULL,
    ebitda DOUBLE DEFAULT NULL,
    basic_eps DOUBLE DEFAULT NULL,
    diluted_eps DOUBLE DEFAULT NULL,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id) ON DELETE CASCADE,
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fact: fact_stock_prices (stores daily stock price metrics)
CREATE TABLE fact_stock_prices (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    date DATE NOT NULL,
    open DOUBLE NOT NULL,
    high DOUBLE NOT NULL,
    low DOUBLE NOT NULL,
    close DOUBLE NOT NULL,
    adj_close DOUBLE NOT NULL,
    volume BIGINT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id) ON DELETE CASCADE,
    -- Composite index on company_id and date for fast timeseries queries
    UNIQUE KEY uq_company_date (company_id, date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
