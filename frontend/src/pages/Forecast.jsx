import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import forecastService from "../services/forecastService";
import PredictionExplanationCard from "../components/explainability/PredictionExplanationCard";

// ── Symbols available in the picker ─────────────────────────────────────────
const SYMBOLS = ["COMB", "JKH", "DIST", "SAMP", "HNB"];

// ── Small helper: model badge colours ───────────────────────────────────────
const MODEL_COLORS = {
  baseline: { border: "#6b7280", bg: "rgba(107,114,128,0.12)", text: "#9ca3af", label: "Baseline" },
  sarimax:  { border: "#818cf8", bg: "rgba(129,140,248,0.12)", text: "#818cf8", label: "SARIMAX" },
  xgboost:  { border: "#34d399", bg: "rgba(52,211,153,0.12)", text: "#34d399", label: "XGBoost" },
};

// ── Custom tooltip for the chart ─────────────────────────────────────────────
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="fc-tooltip">
      <p className="fc-tooltip-label">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }} className="fc-tooltip-row">
          {p.name}: <strong>{p.value != null ? p.value.toFixed(2) : "—"}</strong>
        </p>
      ))}
    </div>
  );
}

// ── Star rating display ───────────────────────────────────────────────────────
function Stars({ rating }) {
  return (
    <span className="fc-stars">
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} className={i <= rating ? "star filled" : "star"}>★</span>
      ))}
    </span>
  );
}

// ── KPI card ─────────────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, accent }) {
  return (
    <div className="fc-kpi-card" style={{ "--accent": accent }}>
      <p className="fc-kpi-label">{label}</p>
      <p className="fc-kpi-value">{value}</p>
      {sub && <p className="fc-kpi-sub">{sub}</p>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
export default function Forecast() {
  const [symbol, setSymbol]     = useState("COMB");
  const [data, setData]         = useState(null);
  const [history, setHistory]   = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const load = useCallback(async (sym) => {
    setLoading(true);
    setError(null);
    setData(null);
    setHistory([]);
    try {
      const [pred, hist] = await Promise.all([
        forecastService.getPredictions(sym, 7),
        forecastService.getPriceHistory(sym, 60),
      ]);
      setData(pred);
      setHistory(hist.history || []);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load forecast data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(symbol); }, [symbol, load]);

  // ── Build chart data ─────────────────────────────────────────────────────
  const chartData = (() => {
    const historicalPoints = history.map((h) => ({
      date:  h.date,
      close: h.close,
      forecast: null,
    }));

    if (!data) return historicalPoints;

    const forecastPoints = (data.forecast_dates || []).map((d, i) => ({
      date:     d,
      close:    null,
      forecast: data.forecast_values?.[i] ?? null,
    }));

    return [...historicalPoints, ...forecastPoints];
  })();

  // First forecast date (dividing line)
  const splitDate = data?.forecast_dates?.[0] ?? null;

  // ── Best model info ──────────────────────────────────────────────────────
  const bestKey  = data?.best_model ?? "";
  const bestInfo = MODEL_COLORS[bestKey] ?? MODEL_COLORS.baseline;
  const bestPred = data?.predictions?.[bestKey];
  const confidence = data?.confidence ?? null;

  // ── Per-model comparison rows ────────────────────────────────────────────
  const modelRows = data
    ? Object.entries(data.predictions).map(([k, v]) => ({ key: k, ...v }))
    : [];

  return (
    <div className="app-container">
      {/* ── Header ── */}
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-icon">📊</span>
          <h1>CSE Market Intelligence</h1>
        </div>
        <Link to="/" className="back-btn">← Back to Home</Link>
      </header>

      <main className="app-main">
        <div className="fc-page">

          {/* ── Page title + symbol picker ── */}
          <div className="fc-page-header">
            <div>
              <h2 className="fc-title">Price Forecast</h2>
              <p className="fc-subtitle">Multi-model next-day predictions with 7-day outlook</p>
            </div>
            <div className="fc-symbol-picker">
              {SYMBOLS.map((s) => (
                <button
                  key={s}
                  className={`fc-symbol-btn ${symbol === s ? "active" : ""}`}
                  onClick={() => setSymbol(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* ── Loading / Error ── */}
          {loading && (
            <div className="fc-loading">
              <div className="fc-spinner" />
              <p>Training models and generating forecasts for <strong>{symbol}</strong>…</p>
              <p className="fc-loading-hint">First run may take 15–30 seconds</p>
            </div>
          )}

          {error && !loading && (
            <div className="fc-error">
              <span>⚠️</span>
              <div>
                <strong>Forecast unavailable</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {data && !loading && (
            <>
              {/* ── KPI cards ── */}
              <div className="fc-kpi-row">
                <KpiCard
                  label="Current Price"
                  value={`LKR ${data.current_price?.toFixed(2) ?? "—"}`}
                  sub="Last close"
                  accent="#60a5fa"
                />
                <KpiCard
                  label="Best Prediction (Next Day)"
                  value={`LKR ${data.best_prediction?.toFixed(2) ?? "—"}`}
                  sub={`Model: ${bestInfo.label}`}
                  accent={bestInfo.border}
                />
                <KpiCard
                  label="Confidence"
                  value={confidence ? `${(confidence * 100).toFixed(1)}%` : "—"}
                  sub="Based on hold-out MAPE"
                  accent="#f59e0b"
                />
                <KpiCard
                  label="Data Points"
                  value={data.data_points_used ?? "—"}
                  sub={`${data.n_features} features`}
                  accent="#a78bfa"
                />
              </div>

              {/* ── Warning banner ── */}
              {data.warning && (
                <div className="fc-warning-banner">
                  ⚠️ {data.warning}
                </div>
              )}

              {/* ── Chart ── */}
              <div className="fc-chart-card">
                <div className="fc-chart-header">
                  <h3>Historical Price + 7-Day Forecast</h3>
                  <div className="fc-chart-legend-inline">
                    <span className="legend-dot" style={{ background: "#60a5fa" }} /> Historical
                    <span className="legend-dot" style={{ background: "#f97316", marginLeft: "1rem" }} /> Forecast
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={340}>
                  <ComposedChart data={chartData} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: "#9ca3af", fontSize: 11 }}
                      tickLine={false}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tick={{ fill: "#9ca3af", fontSize: 11 }}
                      tickLine={false}
                      axisLine={false}
                      domain={["auto", "auto"]}
                      tickFormatter={(v) => `${v.toFixed(0)}`}
                    />
                    <Tooltip content={<ChartTooltip />} />
                    {splitDate && (
                      <ReferenceLine
                        x={splitDate}
                        stroke="#f97316"
                        strokeDasharray="4 4"
                        label={{ value: "Forecast Start", fill: "#f97316", fontSize: 11 }}
                      />
                    )}
                    <Line
                      type="monotone"
                      dataKey="close"
                      name="Historical"
                      stroke="#60a5fa"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      name="Forecast"
                      stroke="#f97316"
                      strokeWidth={2.5}
                      strokeDasharray="6 3"
                      dot={{ fill: "#f97316", r: 4 }}
                      connectNulls={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* ── Model comparison mini-table ── */}
              <div className="fc-model-table-card">
                <h3>Model Comparison</h3>
                <div className="fc-model-grid">
                  {modelRows.map((m) => {
                    const info  = MODEL_COLORS[m.key] ?? MODEL_COLORS.baseline;
                    const isBest = m.key === bestKey;
                    return (
                      <div
                        key={m.key}
                        className={`fc-model-row ${isBest ? "best" : ""}`}
                        style={{ "--model-color": info.border }}
                      >
                        <div className="fc-model-row-left">
                          <span className="fc-model-dot" style={{ background: info.border }} />
                          <span className="fc-model-name">{info.label}</span>
                          {isBest && <span className="fc-best-badge">Best</span>}
                        </div>
                        <div className="fc-model-row-right">
                          <div className="fc-model-stat">
                            <span className="fc-stat-label">Next Day</span>
                            <span className="fc-stat-value" style={{ color: info.text }}>
                              {m.next_day_value != null ? `LKR ${m.next_day_value.toFixed(2)}` : "—"}
                            </span>
                          </div>
                          <div className="fc-model-stat">
                            <span className="fc-stat-label">MAPE</span>
                            <span className="fc-stat-value">{m.mape != null ? `${m.mape.toFixed(2)}%` : "—"}</span>
                          </div>
                          <div className="fc-model-stat">
                            <span className="fc-stat-label">RMSE</span>
                            <span className="fc-stat-value">{m.rmse != null ? m.rmse.toFixed(2) : "—"}</span>
                          </div>
                          <Stars rating={m.star_rating ?? 0} />
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="fc-footnote">
                  Models are ranked by MAPE on a 20% hold-out test set.
                  Confidence is a heuristic derived from 1 − MAPE/100.
                </p>
              </div>

              {/* ── 7-day table ── */}
              {data.forecast_dates?.length > 0 && (
                <div className="fc-forecast-table-card">
                  <h3>7-Day Price Outlook — {bestInfo.label}</h3>
                  <div className="fc-forecast-dates">
                    {data.forecast_dates.map((d, i) => (
                      <div key={d} className="fc-forecast-date-cell">
                        <span className="fc-date-label">{d}</span>
                        <span className="fc-date-value" style={{ color: bestInfo.border }}>
                          {data.forecast_values?.[i] != null
                            ? `LKR ${data.forecast_values[i].toFixed(2)}`
                            : "—"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Explanation card ── */}
              <PredictionExplanationCard symbol={symbol} />
            </>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>© {new Date().getFullYear()} CSE Market Intelligence. Built with FastAPI & React.</p>
      </footer>
    </div>
  );
}
