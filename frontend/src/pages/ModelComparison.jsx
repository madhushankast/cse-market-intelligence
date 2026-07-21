import { useEffect, useState, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import forecastService from "../services/forecastService";
import SectorStockSelector from "../components/SectorStockSelector";

const SYMBOLS = ["COMB", "JKH", "DIST", "SAMP", "HNB"];

const MODEL_META = {
  baseline: { label: "Baseline",  color: "#6b7280", description: "Naive persistence — moving average prediction" },
  sarimax:  { label: "SARIMAX",   color: "#818cf8", description: "Time-series model with technical exogenous variables" },
  xgboost:  { label: "XGBoost",   color: "#16c784", description: "Gradient-boosted trees on technical + lag features" },
};

function NavBar() {
  const location = useLocation();
  const links = [
    { to: "/", label: "Dashboard" },
    { to: "/analytics", label: "Analytics" },
    { to: "/forecast", label: "Forecasting" },
    { to: "/compare", label: "Models" },
    { to: "/system", label: "System" },
  ];
  return (
    <header className="app-header">
      <div className="logo-section">
        <svg className="logo-svg-icon" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="14" width="4" height="12" rx="1" fill="#16c784"/>
          <rect x="8" y="8" width="4" height="18" rx="1" fill="#3b82f6"/>
          <rect x="14" y="4" width="4" height="22" rx="1" fill="#16c784"/>
          <rect x="20" y="10" width="4" height="16" rx="1" fill="#ea3943"/>
        </svg>
        <Link to="/" style={{ textDecoration: "none" }}>
          <h1>CSE Market Intelligence</h1>
        </Link>
      </div>
      <nav className="header-nav">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className={`nav-link${location.pathname === l.to ? " active" : ""}`}
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}

function Stars({ rating, color }) {
  return (
    <span className="fc-stars">
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={i <= rating ? "star filled" : "star"}
          style={i <= rating ? { color } : {}}
        >
          ★
        </span>
      ))}
    </span>
  );
}

function FeatureImportanceBar({ name, value, maxVal }) {
  const pct = maxVal > 0 ? (value / maxVal) * 100 : 0;
  return (
    <div className="fi-row">
      <span className="fi-name">{name}</span>
      <div className="fi-bar-wrap">
        <div className="fi-bar" style={{ width: `${pct}%` }} />
      </div>
      <span className="fi-val">{(value * 100).toFixed(2)}%</span>
    </div>
  );
}

export default function ModelComparison() {
  const [symbol, setSymbol]   = useState("COMB");
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [metric, setMetric]   = useState("rmse");

  const load = useCallback(async (sym) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await forecastService.getModelComparison(sym);
      setData(result);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load comparison data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(symbol); }, [symbol, load]);

  const barData = data?.comparison?.map((m) => ({
    name:  MODEL_META[m.model]?.label ?? m.model,
    value: m[metric] ?? 0,
    model: m.model,
  })) ?? [];

  const featureImportances = data?.feature_importances ?? {};
  const sortedFeatures = Object.entries(featureImportances)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);
  const maxFi = sortedFeatures[0]?.[1] ?? 1;

  const METRICS = [
    { key: "rmse", label: "RMSE", hint: "Root Mean Squared Error — lower is better" },
    { key: "mae",  label: "MAE",  hint: "Mean Absolute Error — lower is better" },
    { key: "mape", label: "MAPE", hint: "Mean Absolute Percentage Error — lower is better" },
    { key: "direction_accuracy", label: "Accuracy", hint: "Directional Sign Accuracy — higher is better" },
    { key: "r2",   label: "R²",   hint: "Coefficient of Determination — higher is better" },
  ];

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        <div className="fc-page">

          {/* Page header */}
          <div className="fc-page-header">
            <div>
              <h2 className="fc-title">Model Performance Comparison</h2>
              <p className="fc-subtitle">Evaluate Baseline, SARIMAX and XGBoost on hold-out test data</p>
            </div>
            <SectorStockSelector selectedSymbol={symbol} onSelect={(newSym) => setSymbol(newSym)} />
          </div>

          {/* Loading / Error */}
          {loading && (
            <div className="fc-loading">
              <div className="fc-spinner" />
              <p>Training and evaluating models for <strong>{symbol}</strong>…</p>
              <p className="fc-loading-hint">First run may take 15–30 seconds</p>
            </div>
          )}
          {error && !loading && (
            <div className="fc-error">
              <div><strong>Comparison Unavailable</strong><p>{error}</p></div>
            </div>
          )}

          {data && !loading && (
            <>
              {/* Info strip */}
              <div className="cmp-info-strip">
                <span>Train rows: <strong>{data.n_train}</strong></span>
                <span>Test rows: <strong>{data.n_test}</strong></span>
                <span>Best model: <strong style={{ color: MODEL_META[data.best_model]?.color }}>{MODEL_META[data.best_model]?.label}</strong></span>
              </div>

              {/* Model cards */}
              <div className="cmp-model-cards">
                {data.comparison.map((m, idx) => {
                  const meta  = MODEL_META[m.model] ?? { label: m.model, color: "#fff", description: "" };
                  const isBest = m.model === data.best_model;
                  return (
                    <div
                      key={m.model}
                      className={`cmp-model-card ${isBest ? "best" : ""}`}
                      style={{ "--card-color": meta.color }}
                    >
                      {isBest && <div className="cmp-best-ribbon">Best Model</div>}
                      <div className="cmp-card-header">
                        <span className="cmp-rank">#{idx + 1}</span>
                        <h3 style={{ color: meta.color }}>{meta.label}</h3>
                        <Stars rating={m.star_rating} color={meta.color} />
                      </div>
                      <p className="cmp-card-desc">{meta.description}</p>
                      <div className="cmp-metrics-grid">
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">RMSE</span>
                          <span className="cmp-metric-val" style={{ color: meta.color }}>
                            {m.rmse?.toFixed(4) ?? "—"}
                          </span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">MAE</span>
                          <span className="cmp-metric-val">{m.mae?.toFixed(4) ?? "—"}</span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">Accuracy</span>
                          <span className="cmp-metric-val">{m.direction_accuracy != null ? `${(m.direction_accuracy * 100).toFixed(1)}%` : "—"}</span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">MAPE</span>
                          <span className="cmp-metric-val">{m.mape != null ? `${m.mape.toFixed(2)}%` : "—"}</span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">R²</span>
                          <span className="cmp-metric-val">{m.r2?.toFixed(4) ?? "—"}</span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">Confidence</span>
                          <span className="cmp-metric-val">{m.confidence != null ? `${(m.confidence * 100).toFixed(1)}%` : "—"}</span>
                        </div>
                        <div className="cmp-metric">
                          <span className="cmp-metric-label">Test Rows</span>
                          <span className="cmp-metric-val">{m.n_test ?? "—"}</span>
                        </div>
                      </div>
                      {m.warning && <p className="cmp-warning">{m.warning}</p>}
                    </div>
                  );
                })}
              </div>

              {/* Metric selector + Bar chart */}
              <div className="fc-chart-card">
                <div className="fc-chart-header">
                  <h3>Visual Comparison</h3>
                  <div className="cmp-metric-tabs">
                    {METRICS.map((mt) => (
                      <button
                        key={mt.key}
                        title={mt.hint}
                        className={`cmp-tab ${metric === mt.key ? "active" : ""}`}
                        onClick={() => setMetric(mt.key)}
                      >
                        {mt.label}
                      </button>
                    ))}
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={barData} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="name" tick={{ fill: "#7a8fa6", fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#7a8fa6", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: "#111c2d", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px" }}
                      labelStyle={{ color: "#e2e8f0" }}
                      itemStyle={{ color: "#94a3b8" }}
                      formatter={(v) => [parseFloat(v).toFixed(4), metric.toUpperCase()]}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {barData.map((entry) => (
                        <Cell key={entry.model} fill={MODEL_META[entry.model]?.color ?? "#3b82f6"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <p className="fc-footnote" style={{ textAlign: "center" }}>
                  {METRICS.find((m) => m.key === metric)?.hint}
                </p>
              </div>

              {/* Full metrics table */}
              <div className="fc-model-table-card">
                <h3>Full Metrics Table</h3>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Model</th>
                        <th>RMSE ↓</th>
                        <th>MAE ↓</th>
                        <th>Accuracy ↑</th>
                        <th>R² ↑</th>
                        <th>Confidence</th>
                        <th>Rating</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.comparison.map((m) => {
                        const meta  = MODEL_META[m.model] ?? { label: m.model, color: "#fff" };
                        const isBest = m.model === data.best_model;
                        return (
                          <tr key={m.model} className={isBest ? "best-row" : ""}>
                            <td>
                              <span style={{ color: meta.color, fontWeight: 600 }}>
                                {meta.label}
                              </span>
                              {isBest && <span className="fc-best-badge" style={{ marginLeft: 8 }}>Best</span>}
                            </td>
                            <td>{m.rmse?.toFixed(4) ?? "—"}</td>
                            <td>{m.mae?.toFixed(4) ?? "—"}</td>
                            <td>{m.direction_accuracy != null ? `${(m.direction_accuracy * 100).toFixed(2)}%` : "—"}</td>
                            <td>{m.r2?.toFixed(4) ?? "—"}</td>
                            <td>{m.confidence != null ? `${(m.confidence * 100).toFixed(1)}%` : "—"}</td>
                            <td><Stars rating={m.star_rating} color={meta.color} /></td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* XGBoost Feature Importance */}
              {sortedFeatures.length > 0 && (
                <div className="fc-model-table-card">
                  <h3>XGBoost Feature Importance <span className="fc-footnote">(top 10)</span></h3>
                  <div className="fi-list">
                    {sortedFeatures.map(([name, val]) => (
                      <FeatureImportanceBar key={name} name={name} value={val} maxVal={maxFi} />
                    ))}
                  </div>
                  <p className="fc-footnote">
                    Feature importance as fraction of total gain. Powers SHAP explainability analysis.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}
