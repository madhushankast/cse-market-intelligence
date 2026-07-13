# CSE Market Intelligence Platform: Comprehensive Project Report & Documentation

This document serves as the historical record and detailed technical documentation of the **CSE Market Intelligence Platform** built from scratch. It explains the project's milestones, architecture decisions, and solutions to key technical challenges.

---

## 📖 Executive Summary
The stock market is heavily influenced by both local and global macroeconomic factors and public interest signals. Standard stock dashboards fail to integrate these disparate datasets, making predictive analytics difficult.

This platform bridges that gap by establishing a daily time-series dataset that merges:
1. **Real-time stock data** from the Colombo Stock Exchange (CSE).
2. **Macroeconomic indicators** (Inflation, Exchange rates, Interest rates) from the Central Bank of Sri Lanka (CBSL).
3. **Public interest levels** from Google Trends.

---

## 📈 Milestones & Implementation History

### Milestone 1 & 2: Project Architecture & API Foundation
- **Goal**: Set up a clean, scalable monorepo structure with versioned endpoints, CORS configurations, and settings management.
- **Implementation**:
  - Configured the API using `pydantic-settings` to load environments from a [.env](file:///c:/Ongoing%20Projects/New%20folder/backend/.env) file.
  - Set up CORS middleware to allow cross-origin requests from the React frontend.
  - Structured the backend routing under versioned namespaces (`/api/v1/`), introducing a `/health` route to monitor app status.

### Milestone 3: Colombo Stock Exchange Data Ingestion Pipeline
- **Goal**: Connect the system to the Colombo Stock Exchange data sources.
- **Challenges Solved**:
  1. *Undocumented API Mappings*: The official `cse.lk` website relies on reverse-engineered REST queries. We implemented a two-step POST query client in [client.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/cse/client.py). The first query (`/api/companyInfoSummery`) resolves tickers into internal numerical stock IDs, and the second query (`/api/companyChartDataByStock`) fetches historical OHLCV data using those IDs.
  2. *Missing Open Prices*: The CSE chart endpoints return high, low, close, and volume, but leave open prices as `null`. We solved this in [parser.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/cse/parser.py) by estimating the day's open price as the close price of the previous trading day.
  3. *Failover Safety*: If the server is offline or the CSE API undergoes maintenance, the system catches the exception and falls back to loading local CSV backup archives from the raw data folders.

### Milestone 4: Database Storage & Persistence Layer
- **Goal**: Store ingested stock records locally to avoid repeated, slow external requests.
- **Implementation**:
  - Integrated SQLAlchemy ORM with a local SQLite engine (`cse.db`).
  - Defined the `StockPrice` model mapping columns like open, high, low, close, volume, and date.
  - Implemented an idempotent ingestion service in [ingestion_service.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/services/ingestion_service.py) that checks the database for existing records before inserting new rows to prevent duplicate date entries.
  - Refactored `GET /api/v1/stocks/{symbol}` to read directly from the database for fast loads (under 20ms).

### Milestone 5: Preprocessing & Technical Feature Engineering
- **Goal**: Clean raw data and compute indicators to prepare features for machine learning.
- **Implementation**:
  - Built a preprocessing pipeline combining a cleaner module (date-sorting, deduplication, and forward-filling) and an indicator builder.
  - Integrated the `ta` (Technical Analysis) library to compute advanced mathematical indices:
    - **Daily Return**: Percentage price change day-over-day.
    - **Simple Moving Averages (SMA)**: 20-day and 50-day rolling averages.
    - **Relative Strength Index (RSI)**: Momentum indicator (14-day window).
    - **MACD**: Moving Average Convergence Divergence trend indicator.
    - **Volatility**: 20-day standard deviation of daily returns.
  - Exposed these indicators via `GET /api/v1/analytics/stocks/{symbol}`.

### Milestone 6: Alternative Data Integration Layer
- **Goal**: Merge stock prices with CBSL indicators and Google Trends search scores.
- **Challenges Solved**:
  1. *Sampling Frequency Mismatches*: Stock prices are daily, Google Trends data is weekly (Sundays), and macroeconomic data is monthly. A standard left-join on exact dates returns `NaN` values for almost all trading days.
  2. *Alignment Solution*: We implemented a data alignment layer in [merger.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/integration/merger.py) using Pandas `pd.merge_asof(direction="backward")`. This aligns daily stock price rows with the *latest available preceding* weekly search trends and monthly inflation/rate data, creating a complete daily dataset.
  3. *Rate Limiting Failovers*: Querying Google Trends frequently via `pytrends` results in HTTP 429 (Too Many Requests). We built a service that catches rate-limiting exceptions and fails over to local CSV archives.
  4. *API Endpoint*: Exposed the combined daily dataset via `GET /api/v1/analytics/stocks/{symbol}/integrated`.

---

## 📊 Core Data Structures & Payload Examples

### 1. Ingestion Endpoint (`POST /api/v1/stocks/COMB/ingest`)
This downloads live stock history and stores it in the local database.
**Response**:
```json
{
  "symbol": "COMB",
  "records_added": 242
}
```

### 2. Analytics Feature Set (`GET /api/v1/analytics/stocks/COMB`)
Exposes technical indicators computed over the stored dataset.
**Response**:
```json
{
  "symbol": "COMB",
  "features": {
    "close": 203.0,
    "daily_return": -0.01096,
    "rsi": 33.94,
    "sma_20": 208.27,
    "sma_50": 206.83,
    "macd": -0.31,
    "volatility": 0.0088,
    "date": "2026-07-13"
  }
}
```

### 3. Integrated Timeseries Endpoint (`GET /api/v1/analytics/stocks/COMB/integrated`)
Exposes the time-aligned dataset matching stock close prices with inflation, exchange rates, and search interest.
**Response**:
```json
{
  "symbol": "COMB",
  "count": 242,
  "data": [
    {
      "date": "2025-07-14",
      "symbol": "COMB.N0000",
      "close": 168.0,
      "volume": 1981474,
      "inflation": 5.2,
      "usd_lkr": 295.0,
      "interest_rate": 8.5,
      "trend_score": 74.0
    },
    ...
    {
      "date": "2026-07-13",
      "symbol": "COMB.N0000",
      "close": 203.0,
      "volume": 274175,
      "inflation": 2.5,
      "usd_lkr": 295.5,
      "interest_rate": 7.25,
      "trend_score": 37.0
    }
  ]
}
```

---

## 🛠️ Technology Stack Summary

### Backend
- **FastAPI**: Lightweight ASGI web framework for REST routers.
- **SQLAlchemy ORM**: Database connection management.
- **Pandas & NumPy**: Data cleaning, imputation, and alignment.
- **ta**: Vectorized technical analysis calculations.
- **pytrends**: Interface for Google Trends queries.

### Storage
- **SQLite**: Local development database (`cse.db`).
- **CSV Archives**: Raw backups under `backend/data/raw/`.

### Frontend
- **React**: Single Page Application structure.
- **Vite**: Frontend build system.
- **Axios**: HTTP client configuration.

---

## 🔮 Future Roadmap

### Milestone 7: Analytics Engine
- Implement statistical analysis tools:
  - **Correlation Matrix**: Calculate correlation coefficients between stocks and alternative data features.
  - **Granger Causality**: Analyze whether movements in interest rates or search trends help predict stock price shifts.
  - **Lag Analysis**: Identify delayed relationships between macro factors and stock behavior.

### Milestone 8: Machine Learning Core
- Implement predictive models using our clean, integrated daily dataset:
  - **SARIMAX**: Time-series forecasting including seasonal indicators.
  - **XGBoost**: Tree-based regression for predicting daily returns.
  - **LSTM (RNN)**: Neural networks capturing long-term sequential dependencies.
