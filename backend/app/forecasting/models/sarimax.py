import warnings
import numpy as np
import pandas as pd
from typing import Optional

from app.forecasting.base import ForecastModel, EvaluationResult
from app.forecasting.evaluator import ModelEvaluator


class SARIMAXModel(ForecastModel):
    """
    Wraps statsmodels SARIMAX to predict Close(t+30) using
    historical prices and technical indicators as exogenous features.
    """

    name = "sarimax"

    # Exogenous technical indicators to use
    EXOG_COLS = ["rsi", "macd", "sma_20", "sma_50", "volatility"]

    def __init__(self):
        self._model_fit = None
        self._train_target: Optional[pd.Series] = None
        self._train_exog:  Optional[pd.DataFrame] = None
        self._exog_cols_used: list[str] = []
        self._warning: Optional[str] = None
        self._last_close = 0.0

    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Fit SARIMAX on the training target Close(t+30)."""
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        # Use Close(t+30) target as the endogenous variable
        target = train_df["target"].reset_index(drop=True)
        exog  = self._extract_exog(train_df)

        self._train_target = target
        self._train_exog  = exog
        self._exog_cols_used = list(exog.columns) if exog is not None else []
        self._last_close = float(train_df["close"].iloc[-1])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Since target is absolute price (non-stationary), use order=(1, 1, 1)
            model = SARIMAX(
                endog=target,
                exog=exog,
                order=(1, 1, 1),
                seasonal_order=(0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            self._model_fit = model.fit(disp=False, maxiter=200)

    def predict(
        self,
        horizon: int = 30,
        latest_row: Optional[pd.DataFrame] = None,
        latest_close: Optional[float] = None,
        full_df: Optional[pd.DataFrame] = None,
        technical_score: Optional[float] = None,
        technical_confidence: Optional[float] = None,
    ) -> list[float]:
        """Forecast the 30-day close price and return a projected trajectory."""
        if self._model_fit is None:
            raise RuntimeError("SARIMAXModel must be trained before calling predict().")

        steps = 1
        exog_future = None
        last_close = self._last_close

        if full_df is not None:
            from app.forecasting.dataset import ForecastDataset
            dataset = ForecastDataset(full_df)
            
            clean_df = dataset.df
            target = clean_df["target"].reset_index(drop=True)
            exog = self._extract_exog(clean_df)
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._model_fit = self._model_fit.apply(endog=target, exog=exog)
            
            last_close = float(full_df["close"].iloc[-1])
            
            # The remaining rows not in clean_df (usually last 30 rows)
            last_horizon = full_df.iloc[-horizon:]
            exog_future = self._extract_exog(last_horizon)
            if self._exog_cols_used and exog_future is not None:
                exog_future = exog_future[self._exog_cols_used]
            steps = horizon
        else:
            if latest_close is not None:
                last_close = latest_close
            if self._exog_cols_used:
                if latest_row is not None:
                    exog_future = latest_row[self._exog_cols_used]
                else:
                    last_exog = self._train_exog.iloc[[-1]]
                    exog_future = pd.concat([last_exog], ignore_index=True)
            steps = 1

        # Get forecast of the target Close(t+30)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            forecast_res = self._model_fit.get_forecast(steps=steps, exog=exog_future)
            mean = forecast_res.predicted_mean
            conf = forecast_res.conf_int()

        pred_val = float(mean.iloc[-1])
        lower_val = float(conf.iloc[-1, 0])
        upper_val = float(conf.iloc[-1, 1])

        # Fallbacks for extreme/implausible predictions
        if np.isnan(pred_val) or pred_val <= 0:
            pred_val = last_close
        if np.isnan(lower_val) or lower_val <= 0:
            lower_val = pred_val * 0.9
        if np.isnan(upper_val) or upper_val <= 0:
            upper_val = pred_val * 1.1

        # Apply post-processing technical signal adjustment
        adjustment = self.compute_technical_adjustment(
            predicted_price=pred_val,
            last_close=last_close,
            technical_score=technical_score,
            technical_confidence=technical_confidence,
        )
        adjusted_pred_val = pred_val + adjustment
        adjusted_lower_val = lower_val + adjustment
        adjusted_upper_val = upper_val + adjustment

        # Project a linear path from current close to predicted 30-day close
        prices = [
            round(last_close + (i + 1) * (adjusted_pred_val - last_close) / horizon, 4)
            for i in range(horizon)
        ]

        self.last_confidence_intervals = [
            (
                round(last_close + (i + 1) * (adjusted_lower_val - last_close) / horizon, 4),
                round(last_close + (i + 1) * (adjusted_upper_val - last_close) / horizon, 4),
            )
            for i in range(horizon)
        ]

        return prices

    # ------------------------------------------------------------------
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """One-step-ahead predictions on the test set."""
        if self._model_fit is None:
            raise RuntimeError("SARIMAXModel must be trained before calling evaluate().")

        y_true = test_df["target"].values
        test_target = test_df["target"].reset_index(drop=True)
        test_exog  = self._extract_exog(test_df)

        try:
            full_target = pd.concat([self._train_target, test_target], ignore_index=True)
            full_exog  = (
                pd.concat([self._train_exog, test_exog], ignore_index=True)
                if test_exog is not None else None
            )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                new_fit = self._model_fit.apply(
                    endog=full_target,
                    exog=full_exog,
                )

            n_train = len(self._train_target)
            preds = new_fit.fittedvalues[n_train:]
            y_pred = np.array(preds[:len(y_true)])

        except Exception as e:
            self._warning = f"SARIMAX evaluation fallback used: {str(e)[:80]}"
            fitted = self._model_fit.fittedvalues
            last_val = float(fitted.iloc[-1])
            y_pred = np.full_like(y_true, last_val)

        return ModelEvaluator.compute(
            model_name=self.name,
            y_true=y_true,
            y_pred=y_pred,
            y_base=test_df["close"].values,
            warning=self._warning,
        )

    # ------------------------------------------------------------------
    def _extract_exog(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Extract available exogenous columns, return None if none exist."""
        available = [c for c in self.EXOG_COLS if c in df.columns and df[c].notna().any()]
        if not available:
            return None
        exog = df[available].copy().reset_index(drop=True)
        exog = exog.ffill().bfill()
        return exog

