-- ==============================================================================
-- CSE Market Intelligence Platform - Supabase DDL Migration Script
-- ==============================================================================

-- 1. Daily Equities OHLCV (Continuous Source of Truth for 26 Equities)
CREATE TABLE IF NOT EXISTS stock_prices (
    symbol VARCHAR(32) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2) NOT NULL,
    low NUMERIC(12, 2) NOT NULL,
    close NUMERIC(12, 2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_stock_prices PRIMARY KEY (symbol, date),
    CONSTRAINT uq_stock_price_symbol_date UNIQUE (symbol, date)
);

CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices(symbol, date);

-- 2. Daily ASPI Benchmark Index
CREATE TABLE IF NOT EXISTS aspi_index (
    date DATE PRIMARY KEY,
    close NUMERIC(12, 2) NOT NULL,
    high NUMERIC(12, 2),
    low NUMERIC(12, 2),
    change NUMERIC(12, 2),
    percentage NUMERIC(6, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_aspi_index_date ON aspi_index(date);

-- 3. Daily 30-Day Forward Forecast History & Predictions
CREATE TABLE IF NOT EXISTS forecast_predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    as_of_date DATE NOT NULL,
    current_price NUMERIC(12, 2) NOT NULL,
    price_p10 NUMERIC(12, 2) NOT NULL,
    price_p50 NUMERIC(12, 2) NOT NULL,
    price_p90 NUMERIC(12, 2) NOT NULL,
    expected_pct_change NUMERIC(6, 2) NOT NULL,
    target_returns JSONB NOT NULL DEFAULT '{}'::jsonb,
    cone_trajectory JSONB NOT NULL DEFAULT '[]'::jsonb,
    shap_drivers JSONB NOT NULL DEFAULT '[]'::jsonb,
    heuristic_signals JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_symbol_date_forecast UNIQUE (symbol, as_of_date)
);

CREATE INDEX IF NOT EXISTS idx_forecast_predictions_symbol_date ON forecast_predictions(symbol, as_of_date);

-- 4. Pipeline Execution & MLOps Audit Logs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    job_name VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'SUCCESS', 'FAILED', 'WARNING'
    records_ingested INT DEFAULT 0,
    models_retrained INT DEFAULT 0,
    duration_seconds NUMERIC(8, 2),
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_run_date ON pipeline_runs(run_date);
