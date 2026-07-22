# System Architecture

The **CSE Market Intelligence Platform** follows a decoupled, modular architecture designed for high scalability, cloud compatibility, and clear separation of concerns.

```text
┌────────────────────────────────────────────────────────┐
│                     DATA SOURCES                       │
│  ┌─────────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │   Yahoo Finance │ │   CBSL CSV    │ │Google Trends│ │
│  │ (YFinance Client)│ │   (Fallback)  │ │ (Fallback) │  │
│  └────────┬────────┘ └───────┬───────┘ └──────┬──────┘  │
└───────────┼──────────────────┼────────────────┼────────┘
            │                  │                │
            ▼                  │                │
┌────────────────────────┐     │                │
│   Ingestion Service    │     │                │
│ (CSE Client & Parser)  │     │                │
└───────────┬────────────┘     │                │
            │                  │                │
            ▼                  ▼                ▼
┌────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                      │
│        ┌─────────────────────────┐                     │
│        │   SQLite (cse.db)       │                     │
│        │   - stock_prices        │                     │
│        │   - alternative_data    │                     │
│        │   - forecast_results    │                     │
│        │   - job_logs            │                     │
│        │   - explanations        │                     │
│        └───────────┬─────────────┘                     │
│                    │                                   │
│                    ▼                                   │
│        ┌─────────────────────────┐                     │
│        │   Raw CSV Data Archives │                     │
│        │   - data/raw/cse/*.csv  │                     │
│        └───────────┬─────────────┘                     │
└────────────────────┼───────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────┐
│               DATA ENGINEERING & PIPELINE              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Preprocessing Pipeline                           │  │
│  │  - Cleaner (Deduplication, sorting, .ffill())     │  │
│  │  - Indicator Builder (Returns, SMAs, RSI, MACD)  │  │
│  └───────────────────────┬──────────────────────────┘  │
│                          │                             │
│                          ▼                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Data Merger Service                              │  │
│  │  - pd.merge_asof() alignment (Daily+Weekly+Month)│  │
│  └───────────────────────┬──────────────────────────┘  │
└──────────────────────────┼─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                    ANALYTICS & ML                      │
│  ┌────────────────────────┐  ┌──────────────────────┐  │
│  │ Statistical Correlation│  │ Forecasting Models   │  │
│  │ (Granger, Lag, Correlation)  │  │ (Baseline, SARIMAX,  │  │
│  │                        │  │  XGBoost)            │  │
│  └───────────┬────────────┘  └──────────┬───────────┘  │
│              │                          │              │
│              ▼                          ▼              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Explainability Engine (SHAP Attributions)         │  │
│  └───────────────────────┬──────────────────────────┘  │
└──────────────────────────┼─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       API LAYER                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ FastAPI REST Router (/api/v1/)                   │  │
│  └───────────────────────┬──────────────────────────┘  │
└──────────────────────────┼─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                     FRONTEND UI                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ React + Vite Client Dashboard                    │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## Component Overview

1. **Ingestion Layer ([`backend/app/data_sources/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/))**:
   - Decoupled interface wrappers for downloading stock indices and asset prices.
   - Core client: `YFinanceCSEClient` ([yfinance_client.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/cse/yfinance_client.py)) which handles API scraping from Yahoo Finance with fallback handling to local raw stock CSV records.
   - Extensible structures for Google Trends search values and Central Bank of Sri Lanka (CBSL) macroeconomic indicators.

2. **Storage Layer ([`backend/app/database/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/))**:
   - Schema declarations managed via SQLAlchemy ORM mapping SQLite structures for rapid querying.
   - Tables include: `stock_prices`, `alternative_data` (macro trends), `forecast_results`, `job_logs`, and `prediction_explanations`.

3. **Processing Layer ([`backend/app/preprocessing/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/preprocessing/))**:
   - Data cleaning: Deduplication, temporal sorting, and forward/backward filling handling.
   - Indicator construction: Building technical variables (SMAs, EMAs, RSI, MACD, Bollinger Bands, volatility, Average True Range).
   - Alignment: Merging datasets across diverse granularities (Daily, Weekly, Monthly) via robust pandas `merge_asof` operations.

4. **Analytics Layer ([`backend/app/analytics/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/analytics/))**:
   - Performs rule-based scoring (converting indicators into beginner-friendly market tendency signals).
   - Computes statistical correlation, Granger causality p-values, and Lead-Lag cross-correlations.
   - Features a rule-based backtesting engine to simulate trading strategies against historical prices.

5. **Machine Learning & Explainability ([`backend/app/forecasting/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/) & [`backend/app/explainability/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/explainability/))**:
   - Trains forecasting algorithms (Baseline, SARIMAX, and XGBoost) utilizing exogenous macroeconomic and technical indicators.
   - Explains XGBoost outputs using SHAP (SHapley Additive exPlanations) values to isolate feature impact.

6. **API Layer ([`backend/app/api/v1/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/))**:
   - Web router endpoints using FastAPI. Serves structured JSON data models supporting routing, data caching, background pipeline scheduler tasks, and validation.

7. **Frontend Dashboard ([`frontend/src/`](file:///c:/Ongoing%20Projects/New%20folder/frontend/src/))**:
   - React application initialized using Vite. Displays interactive Recharts plotting layouts, model evaluation comparisons, historical pricing overlays, and system execution logs.
