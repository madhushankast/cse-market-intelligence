"""
Explainability schemas — the stable API contract for all explanation methods.

Version history:
    Part 1: FeatureImpact, PredictionExplanation (basic)
    Part 2: + VisualizationData (waterfall + bar chart), + generated_at timestamp
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class FeatureImpact(BaseModel):
    """Single feature's contribution to a prediction."""
    feature:    str   = Field(..., description="Human-readable feature name")
    impact:     float = Field(..., description="Signed impact in output units (LKR for SHAP; scaled for others)")
    abs_impact: float = Field(..., description="Absolute magnitude of impact")
    direction:  str   = Field(..., description="'positive' (raises price) or 'negative' (lowers price)")


class WaterfallPoint(BaseModel):
    """Single step in a waterfall chart (base → f1 → f2 → ... → prediction)."""
    label:      str   = Field(..., description="Feature name or 'Base' / 'Prediction'")
    value:      float = Field(..., description="SHAP value or cumulative offset for this step")
    cumulative: float = Field(..., description="Running total after adding this feature's impact")
    is_total:   bool  = Field(False, description="True for the 'Base' and 'Prediction' endpoints")
    direction:  str   = Field(..., description="'positive', 'negative', or 'total'")


class BarChartPoint(BaseModel):
    """Single bar in the horizontal feature importance chart."""
    feature:   str   = Field(..., description="Feature name")
    impact:    float = Field(..., description="Signed impact value")
    direction: str   = Field(..., description="'positive' or 'negative'")


class VisualizationData(BaseModel):
    """
    Structured chart data returned alongside the explanation.
    React renders these with Recharts — no server-side image generation.
    """
    waterfall: list[WaterfallPoint] = Field(
        default_factory=list,
        description="Waterfall chart: baseline → features → prediction"
    )
    bar_chart: list[BarChartPoint] = Field(
        default_factory=list,
        description="Horizontal bar chart sorted by abs_impact descending"
    )


class PredictionExplanation(BaseModel):
    """
    Standard explanation response returned by every explainer.
    All consumers depend on this shape — never on a specific explainer's internals.
    """
    symbol:             str
    prediction:         float
    model:              str
    confidence:         float
    top_features:       list[FeatureImpact]
    explanation_method: str = Field(
        ...,
        description="'shap' | 'sarimax_coefficients' | 'permutation_importance' | 'permutation_importance_fallback'"
    )
    baseline_value: Optional[float] = Field(
        None,
        description="SHAP expected_value (average model output over training set). None for non-SHAP methods."
    )
    visualization_data: Optional[VisualizationData] = Field(
        None,
        description="Chart-ready data. Populated when ?include_viz=true is passed to the API."
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp when this explanation was generated"
    )
    warning: Optional[str] = None
