# CSE Market Intelligence Platform: Comprehensive System Overview

Welcome to the **Colombo Stock Exchange (CSE) Market Intelligence Platform**. This document provides an end-to-end technical explanation of the entire system architecture, data models, pipelines, analytics engines, forecasting modules, API routes, and user interface.

---

## 1. Directory & Codebase Layout

The workspace is organized as a decoupled monorepo:

*   **[`backend/app/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/)**: FastAPI Python backend containing core business logic.
    *   **[`api/v1/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/api/v1/)**: Web routers exposing JSON endpoints.
    *   **[`database/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/)**: SQLAlchemy models and SQLite connection pooling.
    *   **[`data_sources/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/)**: Ingestion clients (CSE API, local CSV fallback, Yahoo Finance client).
    *   **[`pipelines/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/pipelines/)**: Orchestration code for daily weekday updates.
    *   **[`preprocessing/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/preprocessing/)**: Data cleaner and technical indicator calculations.
    *   **[`analytics/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/analytics/)**: Rule-based signal scoring, backtesting, Granger causality, and lag correlation.
    *   **[`forecasting/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/)**: Machine learning trainers, dataset generators, and predictions.
    *   **[`explainability/`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/explainability/)**: SHAP value calculation and prediction audit trails.
*   **[`frontend/src/`](file:///c:/Ongoing%20Projects/New%20folder/frontend/src/)**: React-Vite client application.
    *   **[`components/`](file:///c:/Ongoing%20Projects/New%20folder/frontend/src/components/)**: Reusable UI cards, gauges, charts, and tables.
    *   **[`pages/`](file:///c:/Ongoing%20Projects/New%20folder/frontend/src/pages/)**: Pages representing research dashboards, analytical plots, forecasting tools, model comparisons, and system administration logs.

---

## 2. Decoupled Data Ingestion & Storage

The system utilizes an abstract service architecture to aggregate stock history, macroeconomic indicators, and alternative metrics.

```text
  Live Ingestion           CSV Fallbacks           Synthetic Fallback
 ┌──────────────┐         ┌──────────────┐         ┌─────────────────┐
 │   CSE API    ├────────►│  Local CSVs  ├────────►│  Geometric BM   │
 └──────────────┘         └──────────────┘         └─────────────────┘
```

1. **Colombo Stock Exchange Ingestion**: Coordinated by `CSEService` ([service.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/data_sources/cse/service.py)), it tries the live CSE API endpoint first. If offline, it loads records from `backend/data/raw/cse/*.csv`, and uses Geometric Brownian Motion (GBM) as a final simulation fallback.
2. **Database Persistence**: SQLite (`cse.db`) stores relational schemas mapped via SQLAlchemy. The models are declared in `models.py` ([models.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/models.py)):
    *   `stock_prices`: Daily stock price histories.
    *   `alternative_data`: Inflation (CCPI), USD/LKR exchange rates, interest rates (SDFR, SLFR), and search trends.
    *   `forecast_results`: Cached prediction outputs and confidence intervals.
    *   `job_logs`: Execution status, processing volumes, and failure logs for auditing.
    *   `prediction_explanations`: Audit logs storing feature impact ranks and SHAP weights.

---

## 3. Data Processing & Analytics Core

Once stock prices are saved, they go through data cleaning, indicator expansion, and statistical evaluation:

1. **Preprocessing**: Mapped in `preprocessing/` ([pipeline.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/preprocessing/pipeline.py)), it sorts datasets, forward-fills gaps, and generates technical indicators (RSI, MACD, SMAs, EMAs, Bollinger Bands, ATR) via `IndicatorBuilder`.
2. **Technical Signals**: `TechnicalSignalEngine` ([technical_signal.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/analytics/technical_signal.py)) scores these indicators to assign plain-language sentiments (`Bullish`, `Bearish`, etc.) and confidence values, with duplicates filtered out in transition ranges.
3. **Statistical Analytics**:
    *   *Correlation*: Measures linear relationships between stock returns and macro variables.
    *   *Granger Causality*: Evaluates if past macroeconomic indicators help predict stock returns.
    *   *Lead-Lag Correlation*: Measures lead-lag offsets to spot early economic warnings.
    *   *Backtesting*: Models virtual trade actions based on RSI cross-over rules.

---

## 4. Machine Learning Forecasting Suite

The forecasting framework trains three models to forecast price series up to 30 days ahead:

```text
 ┌───────────────────────┐
 │    ForecastDataset    │  --- Generates X features & y targets
 └──────────┬────────────┘
            │
            ├────────► Baseline Model (Rolling averages naive control)
            ├────────► SARIMAX Model  (Exogenous linear time-series)
            └────────► XGBoost Model  (Non-linear Gradient Boosted Trees)
```

*   **Baseline Model** ([baseline.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/models/baseline.py)): Standard baseline mean predictor.
*   **SARIMAX Model** ([sarimax.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/models/sarimax.py)): Evaluates seasonal terms using technical features as exogenous variables.
*   **XGBoost Model** ([xgboost.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/models/xgboost.py)): Trained on lag values, technical momentum indicators, calendar features, and economic variables.
*   **Explainable AI**: Features from the model run are evaluated via the `ExplanationService` ([explanation_service.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/explainability/explanation_service.py)). Attributions are computed using **SHAP (SHapley Additive exPlanations)** for XGBoost or standard regression coefficients for SARIMAX.

---

## 5. Web Interface & Dashboard API

*   **FastAPI Routing Layer**: All endpoints are cleanly separated under `api/v1/` routers, including metadata statuses, data refetch controllers, and explanation retrievers. Detailed specifications can be reviewed in the [REST API Guide](file:///c:/Ongoing%20Projects/New%20folder/docs/api.md).
*   **React Frontend Dashboard**: Visualized using clean modern UI themes. Features:
    *   **Overview Panel**: Composite market index indicators, trading volumes, and breadth gauges.
    *   **Analytics Tab**: Technical summary logs, backtest strategies, lead-lag offsets, and causality indexes.
    *   **Forecasting View**: Dynamic multi-step prediction curves plotted alongside confidence boundaries.
    *   **Explainability Graph**: SHAP value horizontal bar charts visualizing feature importance.
    *   **System Status logs**: Real-time pipeline health check auditing.
