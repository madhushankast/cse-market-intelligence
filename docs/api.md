# REST API Specification

The Colombo Stock Exchange (CSE) Market Intelligence Platform serves its REST endpoints via FastAPI. All endpoints are prefixed under the `/api/v1` namespace.

---

## Endpoint Index

### 1. Health Router
Endpoints checking deployment, service, and database connectivity.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/health`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/health.py) | Verifies backend connectivity and returns service status |

### 2. Stocks Ingestion & Status Router
Endpoints managing Colombo Stock Exchange data ingestion and freshness.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/stocks/{symbol}`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Retrieve stored OHLCV price history for a symbol |
| `GET`  | [`/api/v1/stocks/{symbol}/status`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Retrieve historical date ranges and record freshness details |
| `POST` | [`/api/v1/stocks/{symbol}/ingest`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Run historical ingestion (last 2 years) for a specific symbol |
| `POST` | [`/api/v1/stocks/ingest/all`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Trigger full ingestion for all symbols tracked in the platform |
| `POST` | [`/api/v1/stocks/refresh`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Append missing data (incremental daily refresh) for tracked symbols |
| `GET`  | [`/api/v1/stocks/data-status`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/stocks.py) | Check database row counts and csv storage dates for all symbols |

### 3. Data Analytics Router
Endpoints serving technical indicator analyses, Granger causality, and pricing signals.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/analytics/stocks/{symbol}`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Get technical indicators (RSI, MACD, SMAs, Bollinger Bands) |
| `GET`  | [`/api/v1/analytics/stocks/{symbol}/integrated`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Get unified historical data merged with CBSL & Trends indicators |
| `GET`  | [`/api/v1/analytics/{symbol}/correlation`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Get correlation coefficients between stock returns and macro variables |
| `GET`  | [`/api/v1/analytics/{symbol}/causality`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Get Granger causality p-values for macro variables driving prices |
| `GET`  | [`/api/v1/analytics/{symbol}/lag`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Fetch cross-correlation values at lag shifts for lead-lag dynamics |
| `GET`  | [`/api/v1/analytics/{symbol}/technical-summary`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Generate plain-language tendency descriptions from indicator scores |
| `GET`  | [`/api/v1/analytics/stocks/{symbol}/backtest`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/analytics.py) | Backtest a rule-based indicator strategy against historical returns |

### 4. Forecasting & ML Router
Endpoints running prediction algorithms (Baseline, SARIMAX, XGBoost) and cache clearance.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/forecast/{symbol}`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/forecasting.py) | Fetch 7-day ahead price forecasts, confidence intervals, and metrics |
| `POST` | [`/api/v1/forecast/cache/clear`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/forecasting.py) | Evict cached predictions to trigger full retraining of ML models |

### 5. Prediction Analysis & Explainability Router
Endpoints providing comparative model evaluation and AI explainability (SHAP).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/predictions/{symbol}`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/predictions.py) | Multi-model predictions, best model selection, and metrics |
| `GET`  | [`/api/v1/predictions/{symbol}/compare`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/predictions.py) | Compare RMSE, MAE, MAPE, and R² metrics side-by-side |
| `GET`  | [`/api/v1/predictions/{symbol}/history`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/predictions.py) | Retrieve historical stock prices optimized for chart rendering overlays |
| `GET`  | [`/api/v1/predictions/{symbol}/explanation`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/explanations.py) | Retrieve SHAP feature impacts or model parameter coefficients |

### 6. System Administration & Pipeline Router
Endpoints auditing task execution logs and running update cycles.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/system/status`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/system.py) | Audit database counts and last pipeline update status |
| `GET`  | [`/api/v1/system/pipelines/logs`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/system.py) | Retrieve execution log logs from database audits |
| `POST` | [`/api/v1/system/pipelines/run`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/system.py) | Trigger the main update pipeline in a background task executor |

### 7. Core Dashboard Router
Endpoints serving aggregate widgets for the frontend dashboard main page.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | [`/api/v1/dashboard`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/dashboard.py) | Fetch top stocks, economic summaries, ASPI benchmarks, and pipeline status |

---

## Example Responses

### Health Verification
`GET /api/v1/health`
```json
{
  "status": "healthy"
}
```

### Integrated Macro Dataset
`GET /api/v1/analytics/stocks/COMB/integrated`
```json
{
  "symbol": "COMB",
  "data": [
    {
      "date": "2026-07-20",
      "close": 94.8,
      "Inflation_CCPI": 4.8,
      "ExchangeRate_USD_LKR": 298.5,
      "rsi": 52.4,
      "trend_score": 75.0
    }
  ]
}
```
