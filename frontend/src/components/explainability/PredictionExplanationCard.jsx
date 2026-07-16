import { useEffect, useState, useCallback } from "react";
import api from "../../services/api";
import FeatureImportanceChart from "./FeatureImportanceChart";
import WaterfallChart from "./WaterfallChart";
import ExplanationTable from "./ExplanationTable";
import ModelBadge from "./ModelBadge";
import "./PredictionExplanationCard.css";

export default function PredictionExplanationCard({ symbol, onLoad }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState("chart"); // "chart" | "waterfall" | "table"

  const fetchExplanation = useCallback(async (sym) => {
    if (!sym) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const resp = await api.get(`/predictions/${sym}/explanation?include_viz=true`);
      setData(resp.data);
      onLoad?.(resp.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load explanation");
    } finally {
      setLoading(false);
    }
  }, [onLoad]);

  useEffect(() => {
    fetchExplanation(symbol);
  }, [symbol, fetchExplanation]);

  return (
    <div className="xai-card" id={`xai-card-${symbol}`}>
      {/* Header */}
      <div className="xai-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div className="xai-title-row" style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span className="xai-icon">🧠</span>
          <div>
            <h3 className="xai-title" style={{ margin: 0, fontSize: "1.1rem" }}>Explainable AI (XAI)</h3>
            {data && <p className="xai-subtitle" style={{ margin: 0 }}>Explaining prediction drivers for {data.symbol}</p>}
          </div>
        </div>
        {data && <ModelBadge model={data.model} method={data.explanation_method} />}
      </div>

      {/* Loading */}
      {loading && (
        <div className="xai-loading" style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "2rem 0" }}>
          <div className="xai-spinner" />
          <span>Generating real-time model explanations...</span>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="xai-error">
          <span>⚠️</span>
          <div>
            <strong>Explanation failed</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Content */}
      {data && !loading && (
        <>
          {/* KPI Strip */}
          <div className="xai-kpi-strip">
            <div className="xai-kpi">
              <span className="xai-kpi-label">Predicted Close</span>
              <span className="xai-kpi-val">LKR {data.prediction.toFixed(2)}</span>
            </div>
            <div className="xai-kpi">
              <span className="xai-kpi-label">Confidence</span>
              <span className="xai-kpi-val">{(data.confidence * 100).toFixed(1)}%</span>
            </div>
            {data.baseline_value !== null && (
              <div className="xai-kpi">
                <span className="xai-kpi-label">Base Value (Expected)</span>
                <span className="xai-kpi-val">LKR {data.baseline_value.toFixed(2)}</span>
              </div>
            )}
          </div>

          {/* Warnings */}
          {data.warning && (
            <div className="xai-warning">
              {data.warning}
            </div>
          )}

          {/* Interactive view modes */}
          <div className="cmp-metric-tabs" style={{ alignSelf: "flex-start", marginBottom: "0.5rem" }}>
            <button className={`cmp-tab ${viewMode === "chart" ? "active" : ""}`} onClick={() => setViewMode("chart")}>
              Impact Chart
            </button>
            {data.visualization_data?.waterfall && (
              <button className={`cmp-tab ${viewMode === "waterfall" ? "active" : ""}`} onClick={() => setViewMode("waterfall")}>
                Waterfall Chart
              </button>
            )}
            <button className={`cmp-tab ${viewMode === "table" ? "active" : ""}`} onClick={() => setViewMode("table")}>
              Metrics Table
            </button>
          </div>

          {/* Visual representations */}
          {viewMode === "chart" && (
            <FeatureImportanceChart data={data.visualization_data?.bar_chart || []} />
          )}

          {viewMode === "waterfall" && (
            <WaterfallChart data={data.visualization_data?.waterfall || []} />
          )}

          {viewMode === "table" && (
            <ExplanationTable features={data.top_features || []} />
          )}

          {/* Footnote */}
          <p className="xai-footnote">
            {data.explanation_method === "shap" && (
              "SHAP (SHapley Additive exPlanations) values show each feature's marginal contribution to this specific prediction (in LKR) relative to the training baseline."
            )}
            {data.explanation_method === "sarimax_coefficients" && (
              "SARIMAX feature impact shows the exogenous parameter coefficients scaled by current daily values."
            )}
            {data.explanation_method.startsWith("permutation") && (
              "Permutation Importance measures prediction degradation (in LKR) when feature values are randomly shuffled."
            )}
            <span style={{ display: "block", marginTop: "0.25rem", opacity: 0.7 }}>
              Generated at: {new Date(data.generated_at).toLocaleString()}
            </span>
          </p>
        </>
      )}
    </div>
  );
}
