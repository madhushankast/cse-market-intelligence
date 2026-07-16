"""
BaseExplainer — abstract interface all explainers must implement.

Architecture principle:
    Every explainer (SHAP, permutation importance, LIME, etc.) returns
    a PredictionExplanation. The ExplanationService and API layer
    depend only on this interface, never on a concrete implementation.

    This means swapping the explanation method requires changing exactly
    one line in ExplanationService — nothing else in the codebase changes.
"""

from abc import ABC, abstractmethod
import pandas as pd
from app.explainability.schemas import PredictionExplanation


class BaseExplainer(ABC):
    """
    Abstract base class for all explainability implementations.

    Subclasses must implement `explain()` and return a PredictionExplanation.
    """

    @abstractmethod
    def explain(
        self,
        model,
        features: pd.DataFrame,
        prediction: float,
        symbol: str,
        confidence: float,
    ) -> PredictionExplanation:
        """
        Produce an explanation for a single model prediction.

        Args:
            model:      The trained model object (XGBRegressor, SARIMAX result, etc.)
            features:   Single-row DataFrame with the feature values used for this prediction.
            prediction: The scalar predicted value (e.g. next-day close price).
            symbol:     Stock ticker being explained.
            confidence: Heuristic confidence score (0–1) from the forecasting layer.

        Returns:
            PredictionExplanation — the standard explanation response schema.
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable name of this explainer, used in the response."""
        return self.__class__.__name__
