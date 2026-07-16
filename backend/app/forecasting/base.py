"""
Base abstract class for all forecast models.

Every model (Baseline, SARIMAX, XGBoost, and future Prophet) must
inherit from ForecastModel and implement the three core methods.
This enables uniform evaluation and easy model swapping.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class EvaluationResult:
    """Holds hold-out evaluation metrics for a trained model."""
    model_name: str
    rmse: float
    mae: float
    mape: float          # Mean Absolute Percentage Error (%)
    r2: float
    n_test: int
    warning: Optional[str] = None

    def confidence(self) -> float:
        """
        Heuristic confidence score: 1 - (MAPE / 100), clipped to [0.5, 0.99].
        Clearly a heuristic — not a probabilistic interval.
        """
        raw = 1.0 - (self.mape / 100.0)
        return round(max(0.50, min(0.99, raw)), 4)

    def star_rating(self) -> int:
        """Maps MAPE → 1–5 stars for the UI comparison page."""
        if self.mape < 1.0:
            return 5
        elif self.mape < 2.0:
            return 4
        elif self.mape < 4.0:
            return 3
        elif self.mape < 7.0:
            return 2
        else:
            return 1


class ForecastModel(ABC):
    """
    Abstract base class for all time-series forecast models.

    Subclasses must implement:
        train(train_df)   — fit the model on training data
        predict(horizon)  — return a list of future close price predictions
        evaluate(test_df) — score the model on a hold-out set
    """

    name: str = "ForecastModel"

    @abstractmethod
    def train(self, train_df: pd.DataFrame) -> None:
        """
        Fit the model on the training slice of the dataset.

        Args:
            train_df: DataFrame with feature columns + 'target' column.
        """
        ...

    @abstractmethod
    def predict(self, horizon: int = 7) -> list[float]:
        """
        Generate `horizon` future close price predictions.

        Args:
            horizon: Number of future trading days to forecast.

        Returns:
            List of predicted close prices, length == horizon.
        """
        ...

    @abstractmethod
    def evaluate(self, test_df: pd.DataFrame) -> EvaluationResult:
        """
        Score the already-trained model on the hold-out test set.

        Args:
            test_df: DataFrame with the same feature schema as train_df.

        Returns:
            EvaluationResult dataclass with RMSE, MAE, MAPE, R².
        """
        ...
