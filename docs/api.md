# REST API Specification

The API endpoints are served via FastAPI under the `/api/v1` route prefix.

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/v1/health` | Infrastructure and service health status |
| `GET`  | `/api/v1/stocks/{symbol}` | Fetch stored OHLCV stock records for a symbol |
| `POST` | `/api/v1/stocks/{symbol}/ingest` | Trigger real-time data ingestion for a symbol |
| `GET`  | `/api/v1/analytics/stocks/{symbol}` | Fetch technical indicator series (RSI, MACD, SMA) |
| `GET`  | `/api/v1/analytics/stocks/{symbol}/integrated` | Fetch unified daily stock + macroeconomic dataset |
| `GET`  | `/api/v1/forecasting/{symbol}` | Generate price forecasts over specified horizon |
| `GET`  | `/api/v1/explanations/{symbol}` | Fetch SHAP feature importance explainability metrics |

## Example Requests & Responses

### Health Check
`GET /api/v1/health`
```json
{
  "status": "healthy"
}
```

### Integrated Dataset Retrieval
`GET /api/v1/analytics/stocks/COMB/integrated`
```json
{
  "symbol": "COMB",
  "data": [
    {
      "date": "2024-01-15",
      "close": 92.5,
      "inflation": 5.2,
      "usd_lkr": 295.0,
      "rsi": 48.2
    }
  ]
}
```
