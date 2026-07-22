# Forecasting & Explainability Machine Learning Pipeline

The platform incorporates modular machine learning models for market trend predictions and explainable AI insights, combining technical signals with macroeconomic inputs.

---

## Forecasting Architecture (`backend/app/forecasting/`)

The forecasting codebase constructs target matrices and feature variables using [`ForecastDataset`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/dataset.py). The model evaluation, prediction cache management, and trainer interfaces are coordinated by [`PredictionService`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/prediction_service.py) and [`ModelTrainer`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/forecasting/trainer.py).

### 1. Dataset Generation
- **Features Engineered**:
  - Daily OHLCV data from CSE.
  - Technical indicator series calculated by `IndicatorBuilder` (e.g. `RSI`, `MACD`, `SMAs`, `EMAs`, `Bollinger Bands`, volatility).
  - Macroeconomic indicators merged from alternative data pipelines (e.g. `ExchangeRate_USD_LKR`, `Inflation_CCPI`, `InterestRate_SDFR`, `InterestRate_SLFR`).
  - Google Search trend popularity scores (`trend_score`).
  - Date/calendar components (e.g. day of week, month of year).
- **Target Value**: Next-day close price or specific horizon forecasts (e.g., $Close_{t+7}$).

### 2. Available Models (`backend/app/forecasting/models/`)
The system trains three distinct algorithms to capture different patterns in stock movements:

1. **Baseline Model (`baseline.py`)**:
   - Acts as a naive statistical control model.
   - Leverages rolling averages and historical averages as fallbacks if series length is too brief.
2. **SARIMAX Model (`sarimax.py`)**:
   - Seasonal AutoRegressive Integrated Moving Average with eXogenous variables.
   - Captures linear autocorrelation and seasonality in pricing, incorporating key technical indicators as exogenous features.
3. **XGBoost Model (`xgboost.py`)**:
   - Gradient-boosted decision trees.
   - Non-linear machine learning model mapping historical lag prices, technical signals, macroeconomic features, and calendar indicators.

### 3. Model Evaluation (`evaluator.py`)
Calculates standard evaluation metrics to gauge accuracy, including:
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)
- **Directional Accuracy** (percentage of days where predicted price movement direction matches the actual direction)

---

## Explainable AI (`backend/app/explainability/`)

To build user trust and offer education, predictions are accompanied by feature attribution metrics calculated by [`ExplanationService`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/explainability/explanation_service.py).

- **XGBoost Model Attribution**: Uses **SHAP (SHapley Additive exPlanations)** to compute impact values, showing which variables (e.g., USD/LKR exchange rate or RSI score) drove the prediction up or down.
- **SARIMAX Model Attribution**: Standardizes and reports model parameter coefficients for exogenous variables.
- **Fallback Attribution**: Computes Permutation Feature Importance for other model configurations.

### Explanation Audit Trail
To audit model decisions over time, the system writes feature-level impact records to the `prediction_explanations` table via `PredictionExplanationLog` for every inference request, tracking:
- Model used and predicted value
- Input features and their calculated SHAP / coefficient impacts
- Feature rank by absolute impact
