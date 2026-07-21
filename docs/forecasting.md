# Forecasting & Explainability Machine Learning Pipeline

The platform incorporates modular machine learning models for market trend predictions and explainable AI insights.

## Forecasting Architecture (`backend/app/forecasting/`)
- **Dataset Generation**: Assembles daily historical price trends merged with macroeconomic indicators.
- **Model Suite**: Supports baseline ARIMA, Prophet, and statistical trend models with fallback handling for short time-series histories.
- **Evaluator**: Calculates standard accuracy metrics including MAE, RMSE, and MAPE across validation horizons.

## Explainable AI (`backend/app/explainability/`)
- Uses **SHAP (SHapley Additive exPlanations)** to break down feature contributions for price forecasts.
- Identifies how macro variables (e.g., USD/LKR exchange rate, inflation) and technical indicators (RSI, Moving Averages) drive model outputs.
