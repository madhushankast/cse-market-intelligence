"""
ExplanationVisualizer — generates structured chart data from a PredictionExplanation.

Returns JSON-serialisable dicts that React/Recharts renders client-side.
No matplotlib images are served over the API.

Charts produced:
    waterfall   — baseline → f1 → f2 → ... → predicted price (cumulative)
    bar_chart   — horizontal bars sorted by abs_impact, colour-coded by direction
"""

from app.explainability.schemas import (
    PredictionExplanation,
    VisualizationData,
    WaterfallPoint,
    BarChartPoint,
)


class ExplanationVisualizer:

    @staticmethod
    def build(explanation: PredictionExplanation) -> VisualizationData:
        """Generate both chart datasets from a PredictionExplanation."""
        waterfall = ExplanationVisualizer.waterfall_data(explanation)
        bar_chart = ExplanationVisualizer.bar_chart_data(explanation)
        return VisualizationData(waterfall=waterfall, bar_chart=bar_chart)

    @staticmethod
    def waterfall_data(explanation: PredictionExplanation) -> list[WaterfallPoint]:
        """
        Build waterfall chart points.

        Structure:
            Base value → Feature 1 → Feature 2 → ... → Predicted Price

        For SHAP:
            baseline_value is the SHAP expected_value (mean training output).
            Each step's value is the SHAP contribution in LKR.
            The sum should approximately equal the prediction.

        For non-SHAP:
            baseline_value defaults to prediction × 0.95 (a visual anchor).
            Contributions are proportional to abs_impact.
        """
        features = explanation.top_features
        baseline = explanation.baseline_value

        if baseline is None:
            # Construct a visual baseline such that baseline + sum(impacts) = prediction
            total_impact = sum(f.impact for f in features)
            baseline = explanation.prediction - total_impact

        points: list[WaterfallPoint] = []

        # Starting point
        points.append(WaterfallPoint(
            label="Base",
            value=round(baseline, 4),
            cumulative=round(baseline, 4),
            is_total=True,
            direction="total",
        ))

        # Feature contributions
        cumulative = baseline
        for feat in features:
            cumulative = round(cumulative + feat.impact, 4)
            points.append(WaterfallPoint(
                label=feat.feature,
                value=round(feat.impact, 4),
                cumulative=cumulative,
                is_total=False,
                direction=feat.direction,
            ))

        # Final predicted price endpoint
        points.append(WaterfallPoint(
            label="Predicted",
            value=round(explanation.prediction, 4),
            cumulative=round(explanation.prediction, 4),
            is_total=True,
            direction="total",
        ))

        return points

    @staticmethod
    def bar_chart_data(explanation: PredictionExplanation) -> list[BarChartPoint]:
        """
        Build horizontal bar chart data, sorted by abs_impact descending.
        """
        return [
            BarChartPoint(
                feature=f.feature,
                impact=f.impact,
                direction=f.direction,
            )
            for f in sorted(explanation.top_features, key=lambda x: x.abs_impact, reverse=True)
        ]
