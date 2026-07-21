# System Architecture

The **CSE Market Intelligence Platform** follows a decoupled, modular architecture designed for high scalability, cloud compatibility, and clear separation of concerns.

```text
┌────────────────────────────────────────────────────────┐
│                     DATA SOURCES                       │
│  ┌─────────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │  CSE REST API   │ │   CBSL CSV    │ │Google Trends│ │
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
│               ┌────────────────────────┐               │
│               │   SQLite (cse.db)      │               │
│               │   - stock_prices       │               │
│               └──────────┬─────────────┘               │
│                          │                             │
│                          ▼                             │
│               ┌────────────────────────┐               │
│               │      Raw Archives      │               │
│               └──────────┬─────────────┘               │
└──────────────────────────┼─────────────────────────────┘
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

## Component Overview

1. **Ingestion Layer (`backend/app/data_sources/`)**: Decoupled interface wrappers for Colombo Stock Exchange API, CBSL macro indicators, and Google Trends search data.
2. **Storage Layer (`backend/app/database/`)**: Relational database schema abstraction using SQLAlchemy ORM.
3. **Processing Layer (`backend/app/preprocessing/`)**: Data cleaning, technical indicator calculation, and cross-frequency time alignment (`pd.merge_asof`).
4. **Analytics & ML Layer (`backend/app/analytics/`, `forecasting/`, `explainability/`)**: Statistical correlation engines, time-series forecasting, and SHAP explainers.
5. **API Layer (`backend/app/api/v1/`)**: FastAPI REST interface serving structured JSON payload responses to the dashboard.
6. **Frontend Dashboard (`frontend/src/`)**: Dynamic React dashboard with responsive visualizations.
