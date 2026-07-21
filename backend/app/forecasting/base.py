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
    mape: float
    direction_accuracy: float  # Directional accuracy percentage (0.0 to 1.0)
    r2: float
    n_test: int
    warning: Optional[str] = None

    def confidence(self) -> float:
        """
        Heuristic confidence score based on Directional Accuracy, clipped to [0.5, 0.99].
        """
        return round(max(0.50, min(0.99, self.direction_accuracy)), 4)

    def confidence_label(self) -> str:
        """User-facing trust category derived from directional accuracy."""
        da_pct = self.direction_accuracy * 100 if self.direction_accuracy <= 1.0 else self.direction_accuracy
        if da_pct >= 65.0:
            return "High Confidence"
        elif da_pct >= 55.0:
            return "Moderate Confidence"
        else:
            return "Low Confidence"

    def star_rating(self) -> int:
        """Maps Directional Accuracy → 1–5 stars for the UI comparison page."""
        da_pct = self.direction_accuracy * 100 if self.direction_accuracy <= 1.0 else self.direction_accuracy
        if da_pct >= 65.0:
            return 5
        elif da_pct >= 60.0:
            return 4
        elif da_pct >= 55.0:
            return 3
        elif da_pct >= 50.0:
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
    def predict(
        self,
        horizon: int = 7,
        latest_row: Optional[pd.DataFrame] = None,
        latest_close: Optional[float] = None,
        full_df: Optional[pd.DataFrame] = None,
        technical_score: Optional[float] = None,
        technical_confidence: Optional[float] = None,
    ) -> list[float]:
        """
        Generate `horizon` future close price predictions.

        Args:
            horizon: Number of future trading days to forecast.
            latest_row: Optional latest single row from the full dataset.
            latest_close: Optional latest closing price.
            full_df: Optional complete historical DataFrame up to today.
            technical_score: Optional technical analysis rating score (-5 to +5).
            technical_confidence: Optional technical signal confidence percentage (0 to 100).

        Returns:
            List of predicted close prices, length == horizon.
        """
        ...

    def compute_technical_adjustment(
        self,
        predicted_price: float,
        last_close: float,
        technical_score: Optional[float] = None,
        technical_confidence: Optional[float] = None,
        bias_scale: float = 0.4,
        max_adjustment_pct: float = 0.02,
    ) -> float:
        """
        Calculates a blended technical adjustment value using:
            adjustment = technical_score * bias_scale * (technical_confidence / 100.0)
        Subject to guardrails (capping the adjustment magnitude).
        """
        if technical_score is None or technical_confidence is None:
            return 0.0

        # Convert confidence from percentage (e.g. 86) to fraction (e.g. 0.86)
        conf_fraction = technical_confidence / 100.0 if technical_confidence > 1.0 else technical_confidence

        # Calculate raw adjustment
        adjustment = float(technical_score) * bias_scale * conf_fraction

        # Guardrail: Cap adjustment at max_adjustment_pct (e.g., 2% of today's close price)
        max_adj = last_close * max_adjustment_pct

        # Clamp adjustment
        if abs(adjustment) > max_adj:
            import math
            adjustment = math.copysign(max_adj, adjustment)

        return round(adjustment, 4)

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
