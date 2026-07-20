import { useEffect, useState, useCallback } from "react";
import api from "../../services/api";
import FeatureImportanceChart from "./FeatureImportanceChart";
import WaterfallChart from "./WaterfallChart";
import ExplanationTable from "./ExplanationTable";
import ModelBadge from "./ModelBadge";
import "./PredictionExplanationCard.css";

export default function PredictionExplanationCard({ symbol, horizon = 30, onLoad }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState("chart"); // "chart" | "waterfall" | "table"

  const fetchExplanation = useCallback(async (sym, hor) => {
    if (!sym) return;
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const resp = await api.get(`/predictions/${sym}/explanation?include_viz=true&horizon=${hor}`);
      setData(resp.data);
      onLoad?.(resp.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load explanation");
    } finally {
      setLoading(false);
    }
  }, [onLoad]);

  useEffect(() => {
    fetchExplanation(symbol, horizon);
  }, [symbol, horizon, fetchExplanation]);

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
              <span className="xai-kpi-label">Predicted Price</span>
              <span className="xai-kpi-val" style={{ color: "#4caf50" }}>
                LKR {data.prediction?.toFixed(2) ?? "—"}
              </span>
            </div>
            <div className="xai-kpi">
              <span className="xai-kpi-label">Confidence</span>
              <span className="xai-kpi-val">{data.confidence_label || "Medium"} ({(data.confidence * 100).toFixed(0)}%)</span>
            </div>
            {data.baseline_value !== null && (
              <div className="xai-kpi">
                <span className="xai-kpi-label">Base Price</span>
                <span className="xai-kpi-val">LKR {data.baseline_value?.toFixed(2) ?? "—"}</span>
              </div>
            )}
          </div>

          {/* Model Reasoning & Drivers */}
          <div className="xai-drivers-section" style={{ marginTop: "1rem", marginBottom: "1.5rem", padding: "1.2rem", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border-color)", borderRadius: "8px" }}>
            <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", color: "var(--accent-color, #3b82f6)", fontWeight: 600 }}>Model Reasoning & Drivers</h4>
            <p className="xai-reasoning" style={{ margin: "0 0 1.2rem 0", fontSize: "0.9rem", lineHeight: "1.4", opacity: 0.9 }}>
              <strong>Confidence ({data.confidence_label}):</strong> {data.confidence_reason}
            </p>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
              <div style={{ width: "100%" }}>
                <h5 style={{ margin: "0 0 0.6rem 0", fontSize: "0.85rem", color: "var(--gain, #16c784)", display: "flex", alignItems: "center", gap: "0.25rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.02em" }}>
                  <span>✓</span> Supporting Factors
                </h5>
                <ul style={{ margin: 0, paddingLeft: "0", listStyle: "none", fontSize: "0.85rem", display: "flex", flexDirection: "column", gap: "0.5rem", color: "var(--text-primary)" }}>
                  {data.factors?.filter(f => f.impact > 0).slice(0, 4).map((f, i) => (
                    <li key={i} style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.02)", paddingBottom: "0.25rem" }}>
                      <span style={{ color: "var(--text-secondary)" }}>{f.feature}</span>
                      <strong style={{ color: "var(--gain)" }}>+{f.impact.toFixed(3)} LKR</strong>
                    </li>
                  ))}
                  {(!data.factors || data.factors.filter(f => f.impact > 0).length === 0) && <span style={{ opacity: 0.5 }}>None</span>}
                </ul>
              </div>
              
              <div style={{ width: "100%" }}>
                <h5 style={{ margin: "0 0 0.6rem 0", fontSize: "0.85rem", color: "var(--loss, #ea3943)", display: "flex", alignItems: "center", gap: "0.25rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.02em" }}>
                  <span>↓</span> Reducing Factors
                </h5>
                <ul style={{ margin: 0, paddingLeft: "0", listStyle: "none", fontSize: "0.85rem", display: "flex", flexDirection: "column", gap: "0.5rem", color: "var(--text-primary)" }}>
                  {data.factors?.filter(f => f.impact < 0).slice(0, 4).map((f, i) => (
                    <li key={i} style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.02)", paddingBottom: "0.25rem" }}>
                      <span style={{ color: "var(--text-secondary)" }}>{f.feature}</span>
                      <strong style={{ color: "var(--loss)" }}>{f.impact.toFixed(3)} LKR</strong>
                    </li>
                  ))}
                  {(!data.factors || data.factors.filter(f => f.impact < 0).length === 0) && <span style={{ opacity: 0.5 }}>None</span>}
                </ul>
              </div>
            </div>
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
              "SHAP (SHapley Additive exPlanations) values show each feature's marginal contribution to this specific prediction (in return percentage points) relative to the training baseline."
            )}
            {data.explanation_method === "sarimax_coefficients" && (
              "SARIMAX feature impact shows the exogenous parameter coefficients scaled by current daily values."
            )}
            {data.explanation_method.startsWith("permutation") && (
              "Permutation Importance measures prediction degradation (in return percentage points) when feature values are randomly shuffled."
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
