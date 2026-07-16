import sys
import os
import unittest
import pandas as pd
import numpy as np

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.explainability.schemas import PredictionExplanation, FeatureImpact
from app.explainability.explainers.shap_explainer import SHAPExplainer
from app.explainability.explainers.sarimax_explainer import SARIMAXExplainer
from app.explainability.explainers.permutation_explainer import PermutationExplainer
from app.explainability.explanation_service import ExplanationService

class DummyXGBRegressor:
    def __init__(self):
        # shap TreeExplainer needs specific structures
        self.base_score = 0.5
        self.objective = 'reg:squarederror'
    def predict(self, X):
        return np.array([170.0] * len(X))

class DummyXGBoostModel:
    name = "xgboost"
    def __init__(self):
        self._model = DummyXGBRegressor()
        # Mock tree explainer model values
        import xgboost as xgb
        # Create a simple toy model to satisfy shap TreeExplainer type requirements
        X = np.random.randn(10, 3)
        y = np.random.randn(10)
        self._model = xgb.XGBRegressor(n_estimators=2, max_depth=2)
        self._model.fit(X, y)
        self._feature_names = ["close", "rsi", "usd_lkr"]
        self.feature_importances_ = {"close": 0.6, "rsi": 0.3, "usd_lkr": 0.1}

class TestExplainability(unittest.TestCase):

    def test_shap_explainer_schema(self):
        model = DummyXGBoostModel()
        features = pd.DataFrame([[168.0, 45.0, 320.0]], columns=["close", "rsi", "usd_lkr"])
        
        explainer = SHAPExplainer()
        explanation = explainer.explain(
            model=model,
            features=features,
            prediction=170.0,
            symbol="COMB",
            confidence=0.9
        )
        
        self.assertEqual(explanation.symbol, "COMB")
        self.assertEqual(explanation.model, "xgboost")
        self.assertEqual(explanation.explanation_method, "shap")
        self.assertTrue(len(explanation.top_features) > 0)
        self.assertIsNotNone(explanation.baseline_value)

    def test_permutation_explainer_fallback(self):
        # Create a basic mock model with predict method
        class MockModel:
            name = "baseline"
            def predict(self, horizon=7):
                return [150.0] * horizon

        model = MockModel()
        features = pd.DataFrame([[150.0]], columns=["close"])
        explainer = PermutationExplainer()
        
        # Test fallback
        explanation = explainer.explain(
            model=model,
            features=features,
            prediction=150.0,
            symbol="COMB",
            confidence=0.8
        )
        self.assertTrue("fallback" in explanation.explanation_method)


if __name__ == "__main__":
    unittest.main()
