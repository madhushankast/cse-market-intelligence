# REST API & Serving Specification

## 1. Overview & Architecture

The serving layer of the platform is built on **FastAPI** (`api/main.py`), utilizing asynchronous I/O, Pydantic v2 data validation schemas, automated OpenAPI documentation (`/docs`), and CORS middleware supporting cross-origin clients (React Vite on Vercel or local terminal).

- **Base URL (Local)**: `http://localhost:8000`
- **Base URL (Cloud)**: `https://cse-market-intelligence-api.onrender.com`
- **Interactive Swagger UI**: `/docs`
- **OpenAPI Schema**: `/openapi.json`

---

## 2. Global Endpoints

### 2.1 Health & Readiness Probe
`GET /health`

Returns service health, system uptime, count of loaded LightGBM models, and count of active equity datasets.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "cse-market-intelligence-api",
  "version": "2.0.0",
  "uptime_seconds": 1420.5,
  "models_count": 26,
  "available_models": [
    "AAIC_N0000", "ACL_N0000", "AHUN_N0000", "CARG_N0000", "COMB_N0000",
    "DIAL_N0000", "DIST_N0000", "EXPO_N0000", "HAYL_N0000", "HEMA_N0000",
    "HNB_N0000", "JKH_N0000", "KGAL_N0000", "LIOC_N0000", "LOLC_N0000",
    "LWL_N0000", "MADU_N0000", "NDB_N0000", "ODEL_N0000", "OSEA_N0000",
    "RICH_N0000", "SAMP_N0000", "SEYB_N0000", "SLTL_N0000", "TKYO_N0000", "UML_N0000"
  ],
  "available_equities_count": 26
}
```

---

## 3. Quantitative Financial Endpoints (`/api/v1`)

### 3.1 List Active Equities
`GET /api/v1/stocks`

Scans the high-speed Parquet storage layer and returns all 26 tracked CSE blue-chip equities with their latest market close, date, volume, sector, and company metadata.

**Response `200 OK`**:
```json
{
  "status": "success",
  "count": 26,
  "data": [
    {
      "symbol": "JKH_N0000",
      "code": "JKH",
      "name": "John Keells Holdings PLC",
      "sector": "Diversified Financials / Conglomerates",
      "latest_close": 17.80,
      "latest_date": "2026-10-27",
      "latest_volume": 425100
    }
  ]
}
```

---

### 3.2 Multi-Quantile Forecast Generation (POST)
`POST /api/v1/predict`

Executes end-to-end inference for a target CSE equity: generates the 30-day forecast cone ($P_{10}, P_{50}, P_{90}$), computes exact TreeSHAP attributions, checks technical heuristic alignment cards, and returns recent historical bars for candlestick charting.

**Request Payload**:
```json
{
  "symbol": "JKH_N0000",
  "horizon_days": 30,
  "explain": true
}
```

**Response `200 OK`**:
```json
{
  "status": "success",
  "data": {
    "symbol": "JKH_N0000",
    "current_price": 17.80,
    "as_of_date": "2026-10-27",
    "horizon_days": 30,
    "target_returns": {
      "p10_log_return": -0.0537,
      "p50_log_return": 0.0188,
      "p90_log_return": 0.0334,
      "expected_pct_change": 1.90
    },
    "target_prices": {
      "price_p10": 16.87,
      "price_p50": 18.14,
      "price_p90": 18.40
    },
    "cone_trajectory": [
      {
        "step": 1,
        "date": "2026-10-28",
        "price_p10": 17.77,
        "price_p50": 17.81,
        "price_p90": 17.82
      },
      {
        "step": 30,
        "date": "2026-12-08",
        "price_p10": 16.87,
        "price_p50": 18.14,
        "price_p90": 18.40
      }
    ],
    "shap_explanation": {
      "base_value": 0.0092,
      "predicted_return": 0.0188,
      "top_positive_drivers": [
        {
          "feature": "parkinson_vol_20d",
          "value": 0.0184,
          "shap_impact": 0.0052,
          "shap_impact_pct": 0.52,
          "description": "20-day Parkinson Volatility",
          "direction": "positive"
        }
      ],
      "top_negative_drivers": [
        {
          "feature": "rsi_14",
          "value": 68.4,
          "shap_impact": -0.0028,
          "shap_impact_pct": -0.28,
          "description": "14-day Relative Strength Index",
          "direction": "negative"
        }
      ]
    },
    "indicator_heuristics": [
      {
        "indicator": "RSI (14-Day)",
        "value": "68.4 (Neutral-High)",
        "status": "Supporting",
        "signal": "Bullish",
        "explanation": "RSI maintains positive momentum without exceeding overbought 70."
      }
    ],
    "historical_series": [
      {
        "date": "2026-10-27",
        "open": 17.60,
        "high": 17.90,
        "low": 17.50,
        "close": 17.80,
        "volume": 425100
      }
    ]
  }
}
```

---

### 3.3 Multi-Quantile Forecast Generation (GET)
`GET /api/v1/predict/{symbol}?horizon_days=30&explain=true`

Convenience GET endpoint providing identical output to the POST method. Ideal for browser-based inspection and lightweight client integrations.

---

### 3.4 Purged Cross-Validation Benchmark Report
`GET /api/v1/benchmarks`

Retrieves the empirical walk-forward benchmark tournament results across all 26 equities from `reports/cv_benchmark_summary.csv`.

**Response `200 OK`**:
```json
{
  "status": "success",
  "count": 26,
  "data": [
    {
      "symbol": "JKH_N0000",
      "n_folds": 5,
      "total_test_samples": 300,
      "lgb_dir_acc": 61.2,
      "naive_dir_acc": 50.0,
      "prophet_dir_acc": 54.3,
      "dir_acc_edge_vs_naive": 11.2,
      "lgb_rmse": 0.0742,
      "naive_rmse": 0.0988,
      "prophet_rmse": 0.0912,
      "lgb_mae": 0.0551,
      "naive_mae": 0.0764,
      "prophet_mae": 0.0701,
      "lgb_coverage_80": 81.3
    }
  ]
}
```

---

### 3.5 Standalone TreeSHAP Attribution
`GET /api/v1/explain/{symbol}?top_k=5`

Returns standalone Layer 1 Shapley value attributions for the given equity.

---

## 4. Error Handling & Status Codes

All errors return standard JSON payloads with explicit diagnostic information:

| HTTP Status | Description | Example Condition |
| :--- | :--- | :--- |
| `200 OK` | Request succeeded | Forecast generated or records retrieved. |
| `404 Not Found` | Asset or model not found | Requesting unknown ticker symbol `XYZ_N0000`. |
| `422 Unprocessable Entity`| Schema validation error | Passing `horizon_days=200` (must be between 5 and 90). |
| `500 Internal Error` | Server computation error | Feature pipeline failure or missing storage artifacts. |
