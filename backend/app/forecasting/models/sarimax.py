"""
SARIMAX Model — Seasonal AutoRegressive Integrated Moving Average with
eXogenous variables.

Why SARIMAX for CSE?
    - Stock markets exhibit weekly seasonality (5 trading days)
    - Macroeconomic variables (USD/LKR, inflation, Google Trends) can be
      fed as exogenous regressors to capture market-external drivers
    - Provides interpretable coefficients — academically valuable

Order selection:
    (p,d,q)     = (1,1,1) — standard for non-stationary financial series
    (P,D,Q,s)   = (1,1,0,5) — weekly seasonal component (5 trading days)

Exogenous variables (if available):
    - usd_lkr       (exchange rate)
    - inflation      (CPI)
    - trend_score    (Google Trends interest)
"""

import warnings
import numpy as np
import pandas as pd
from typing import Optional

from app.forecasting.base import ForecastModel, EvaluationResult
from app.forecasting.evaluator import ModelEvaluator


class SARIMAXModel(ForecastModel):
    """
    Wraps statsmodels SARIMAX with sensible defaults for weekly-seasonal
    CSE stock data and optional macro exogenous variables.
    """

    name = "sarimax"

    # SARIMAX orders — (p,d,q)(P,D,Q,s)
    ORDER         = (1, 1, 1)
    SEASONAL_ORDER = (1, 1, 0, 5)

    EXOG_COLS = ["usd_lkr", "inflation", "trend_score"]

    def __init__(self):
        self._model_fit = None
        self._train_close: Optional[pd.Series] = None
        self._train_exog:  Optional[pd.DataFrame] = None
        self._exog_cols_used: list[str] = []
        self._warning: Optional[str] = None

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Fit SARIMAX on the training slice."""
        # Lazy import — only resolve statsmodels when the model is used
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        close = train_df["close"].reset_index(drop=True)
        exog  = self._extract_exog(train_df)

        self._train_close = close
        self._train_exog  = exog
        self._exog_cols_used = list(exog.columns) if exog is not None else []

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = SARIMAX(
                endog=close,
                exog=exog,
                order=self.ORDER,
                seasonal_order=self.SEASONAL_ORDER,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            self._model_fit = model.fit(disp=False, maxiter=200)

    # ------------------------------------------------------------------
    def predict(self, horizon: int = 7) -> list[float]:
        """Forecast `horizon` steps ahead using the fitted SARIMAX model."""
        if self._model_fit is None:
            raise RuntimeError("SARIMAXModel must be trained before calling predict().")

        # For exogenous future values we use the last known value (forward-fill)
        exog_future = None
        if self._exog_cols_used:
            last_exog = self._train_exog.iloc[[-1]]
            exog_future = pd.concat(
                [last_exog] * horizon, ignore_index=True
            )

        forecast = self._model_fit.forecast(steps=horizon, exog=exog_future)
        return [round(float(v), 4) for v in forecast]

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """One-step-ahead predictions on the test set via in-sample forecast."""
        if self._model_fit is None:
            raise RuntimeError("SARIMAXModel must be trained before calling evaluate().")

        from statsmodels.tsa.statespace.sarimax import SARIMAX

        y_true = test_df["target"].values
        test_close = test_df["close"].reset_index(drop=True)
        test_exog  = self._extract_exog(test_df)

        try:
            # Append test data to the fitted model for out-of-sample evaluation
            full_close = pd.concat([self._train_close, test_close], ignore_index=True)
            full_exog  = (
                pd.concat([self._train_exog, test_exog], ignore_index=True)
                if test_exog is not None else None
            )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Re-apply using apply() to extend without re-fitting
                new_fit = self._model_fit.apply(
                    endog=full_close,
                    exog=full_exog,
                )

            n_train = len(self._train_close)
            preds = new_fit.fittedvalues[n_train:]
            y_pred = np.array(preds[:len(y_true)])

        except Exception as e:
            self._warning = f"SARIMAX evaluation fallback used: {str(e)[:80]}"
            # Fallback: use one-step in-sample predictions on training tail
            fitted = self._model_fit.fittedvalues
            last_val = float(fitted.iloc[-1])
            y_pred = np.full_like(y_true, last_val)

        return ModelEvaluator.compute(
            model_name=self.name,
            y_true=y_true,
            y_pred=y_pred,
            warning=self._warning,
        )

    # ------------------------------------------------------------------
    def _extract_exog(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract available exogenous columns, return None if none exist."""
        available = [c for c in self.EXOG_COLS if c in df.columns and df[c].notna().any()]
        if not available:
            return None
        exog = df[available].copy().reset_index(drop=True)
        # Forward-fill + backward-fill to handle monthly macro data gaps
        exog = exog.ffill().bfill()
        return exog
