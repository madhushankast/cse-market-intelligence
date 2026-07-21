import { useEffect, useState, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import forecastService from "../services/forecastService";
import PredictionExplanationCard from "../components/explainability/PredictionExplanationCard";
import SectorStockSelector from "../components/SectorStockSelector";

const SYMBOLS = ["COMB", "JKH", "DIST", "SAMP", "HNB"];

const MODEL_COLORS = {
  baseline: { border: "#6b7280", bg: "rgba(107,114,128,0.12)", text: "#9ca3af", label: "Baseline" },
  sarimax:  { border: "#818cf8", bg: "rgba(129,140,248,0.12)", text: "#818cf8", label: "SARIMAX" },
  xgboost:  { border: "#16c784", bg: "rgba(22,199,132,0.12)", text: "#16c784", label: "XGBoost" },
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

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="fc-tooltip">
      <p className="fc-tooltip-label">{label}</p>
      {payload.map((p) => {
        const fmt = `LKR ${p.value != null ? p.value.toFixed(2) : "—"}`;
        return (
          <p key={p.dataKey} style={{ color: p.color }} className="fc-tooltip-row">
            {p.name}: <strong>{fmt}</strong>
          </p>
        );
      })}
    </div>
  );
}

function Stars({ rating }) {
  return (
    <span className="fc-stars">
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} className={i <= rating ? "star filled" : "star"}>★</span>
      ))}
    </span>
  );
}

function KpiCard({ label, value, sub, accent, badge, titleTooltip }) {
  return (
    <div className="fc-kpi-card" style={{ "--accent": accent }} title={titleTooltip}>
      <p className="fc-kpi-label" style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
        <span>{label}</span>
        {badge && <span className="kpi-badge" style={{ fontSize: "0.65rem", padding: "0.1rem 0.3rem", borderRadius: "4px", background: "rgba(59,130,246,0.15)", color: "#93c5fd", border: "1px solid rgba(59,130,246,0.3)", fontWeight: 600 }}>{badge}</span>}
      </p>
      <p className="fc-kpi-value">{value}</p>
      {sub && <p className="fc-kpi-sub">{sub}</p>}
    </div>
  );
}

export default function Forecast() {
  const [symbol, setSymbol]     = useState("COMB");
  const [data, setData]         = useState(null);
  const [history, setHistory]   = useState([]);
  const [backtest, setBacktest] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const load = useCallback(async (sym) => {
    setLoading(true);
    setError(null);
    setData(null);
    setHistory([]);
    setBacktest(null);
    try {
      const [pred, hist, btest] = await Promise.all([
        forecastService.getPredictions(sym, 30),
        forecastService.getPriceHistory(sym, 60),
        forecastService.getBacktest(sym, 100000).catch(() => null),
      ]);
      setData(pred);
      setHistory(hist.history || []);
      setBacktest(btest);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || "Failed to load forecast data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(symbol); }, [symbol, load]);

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

  const splitDate = data?.forecast_dates?.[0] ?? null;

  const bestKey  = data?.best_model ?? "";
  const bestInfo = MODEL_COLORS[bestKey] ?? MODEL_COLORS.baseline;
  const confidence = data?.confidence ?? null;

  const modelRows = data
    ? Object.entries(data.predictions).map(([k, v]) => ({ key: k, ...v }))
    : [];

  // Calculate dynamic y-axis range to clip extra empty spacing
  const prices = [
    ...history.map((h) => h.close),
    ...(data?.forecast_values || [])
  ].filter((p) => p != null && p > 0);

  const yMin = prices.length > 0 ? Math.floor(Math.min(...prices) * 0.96) : "auto";
  const yMax = prices.length > 0 ? Math.ceil(Math.max(...prices) * 1.04) : "auto";

  // Aggregate 30-day daily forecast into week-by-week summaries
  const weeklyOutlook = (() => {
    if (!data?.forecast_dates || !data?.forecast_values) return [];
    const dates = data.forecast_dates;
    const values = data.forecast_values;
    const weeks = [];

    for (let i = 0; i < dates.length; i += 5) {
      const weekDates = dates.slice(i, i + 5);
      const weekValues = values.slice(i, i + 5);
      if (weekDates.length === 0) continue;

      const startDate = weekDates[0];
      const endDate = weekDates[weekDates.length - 1];
      const prevPrice = i > 0 ? values[i - 1] : (data.current_price || weekValues[0]);
      const endPrice = weekValues[weekValues.length - 1];
      const minPrice = Math.min(...weekValues);
      const maxPrice = Math.max(...weekValues);
      const change = endPrice - prevPrice;
      const changePercent = prevPrice ? (change / prevPrice) * 100 : 0;

      weeks.push({
        weekNum: Math.floor(i / 5) + 1,
        startDate,
        endDate,
        endPrice,
        minPrice,
        maxPrice,
        change,
        changePercent,
        isUp: change >= 0,
      });
    }
    return weeks;
  })();

  const expectedReturn = data?.expected_return_pct ?? 0;
  const isPositive = expectedReturn >= 0;

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        <div className="fc-page">

          {/* Page title + symbol picker */}
          <div className="fc-page-header">
            <div>
              <h2 className="fc-title">Price Forecast & Technical Assistant</h2>
              <p className="fc-subtitle">30-Day return predictions, rule-based reasoning, and performance metrics</p>
            </div>
            <SectorStockSelector selectedSymbol={symbol} onSelect={(newSym) => setSymbol(newSym)} />
          </div>

          {/* Loading / Error */}
          {loading && (
            <div className="fc-loading">
              <div className="fc-spinner" />
              <p>Training models and generating forecasts for <strong>{symbol}</strong>…</p>
              <p className="fc-loading-hint">First run may take 15–30 seconds</p>
            </div>
          )}

          {error && !loading && (
            <div className="fc-error">
              <div>
                <strong>Forecast Unavailable</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {data && !loading && (
            <div className="fc-layout-container">
              {/* SECTION A: Overview Hero Row */}
              <div className="section-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>Overview & Action Signal</span>
                <Link to="/compare" className="fc-transparency-link">
                  See how this model is calculated &rarr;
                </Link>
              </div>

              <div className="fc-kpi-row-restructured">
                <KpiCard
                  label="Current Price"
                  value={`LKR ${data.current_price?.toFixed(2) ?? "—"}`}
                  sub="Last closing price"
                  accent="#3b82f6"
                />
                <KpiCard
                  label="30-Day Forecast Price"
                  value={data.expected_30d_price != null ? `LKR ${data.expected_30d_price.toFixed(2)}` : "—"}
                  sub={`Expected Return: ${isPositive ? "+" : ""}${expectedReturn.toFixed(2)}%`}
                  accent={isPositive ? "#16c784" : "#ea3943"}
                />
                <KpiCard
                  label="Action Signal"
                  value={data.signal || "HOLD"}
                  sub={`Model Confidence: ${data.confidence != null ? Math.round(data.confidence * 100) : 75}%`}
                  accent={data.signal === "BUY" ? "#16c784" : data.signal === "SELL" ? "#ea3943" : "#f59e0b"}
                />
                <KpiCard
                  label="Best Model"
                  value={bestInfo.label}
                  sub={`${data.data_points_used ?? "—"} trained data points`}
                  accent="#8b5cf6"
                />
              </div>

              {/* Technical Assistant Reasons & Risks Box */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", margin: "1rem 0" }}>
                <div style={{ background: "rgba(22,199,132,0.06)", border: "1px solid rgba(22,199,132,0.2)", borderRadius: "8px", padding: "1rem" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#16c784", fontSize: "0.95rem" }}>Key Supporting Reasons</h4>
                  {data.reasons && data.reasons.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "#cdd6f4", fontSize: "0.85rem", lineHeight: "1.6" }}>
                      {data.reasons.map((r, idx) => (
                        <li key={idx}>{r}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ margin: 0, color: "#9ca3af", fontSize: "0.85rem" }}>No immediate positive triggers</p>
                  )}
                </div>

                <div style={{ background: "rgba(234,57,67,0.06)", border: "1px solid rgba(234,57,67,0.2)", borderRadius: "8px", padding: "1rem" }}>
                  <h4 style={{ margin: "0 0 0.5rem 0", color: "#ea3943", fontSize: "0.95rem" }}>Risk & Caution Warnings</h4>
                  {data.risks && data.risks.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "#cdd6f4", fontSize: "0.85rem", lineHeight: "1.6" }}>
                      {data.risks.map((rk, idx) => (
                        <li key={idx}>{rk}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ margin: 0, color: "#9ca3af", fontSize: "0.85rem" }}>No severe warning signals</p>
                  )}
                </div>
              </div>



              <div className="fc-reconciliation-note" style={{ margin: "1rem 0", padding: "0.75rem 1rem", background: "rgba(59,130,246,0.05)", border: "1px solid rgba(59,130,246,0.15)", borderRadius: "6px", fontSize: "0.85rem", color: "#93c5fd" }}>
                ℹ️ <strong>Methodology Note:</strong> This statistical forecast is independent of the rule-based Technical Outlook on the Analytics page and may disagree with it.
              </div>

              {/* Warning banner */}
              {data.warning && (
                <div className="fc-warning-banner">
                  Warning: {data.warning}
                </div>
              )}

              {/* SECTION B: Forecast Chart */}
              <div className="section-header">Forecast Chart</div>
              <div className="fc-chart-card">
                <div className="fc-chart-header">
                  <div>
                    <h3>Historical Price + 30-Day Forecast</h3>
                    <p style={{ margin: 0, fontSize: "0.8rem", opacity: 0.6 }}>
                      Historical close price (LKR) with projected cumulative return
                    </p>
                  </div>
                  <div className="fc-chart-legend-inline">
                    <span className="legend-dot" style={{ background: "#3b82f6" }} /> Historical
                    <span className="legend-dot" style={{ background: "#16c784", marginLeft: "1rem" }} /> 30-Day Forecast
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={380}>
                  <ComposedChart data={chartData} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis
                      dataKey="date"
                      type="category"
                      tick={{ fill: "#7a8fa6", fontSize: 11 }}
                      tickLine={false}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      yAxisId="price"
                      orientation="left"
                      tick={{ fill: "#3b82f6", fontSize: 11 }}
                      tickLine={false}
                      axisLine={false}
                      domain={[yMin, yMax]}
                      tickFormatter={(v) => `${v.toFixed(0)}`}
                      label={{ value: "LKR", angle: -90, position: "insideLeft", fill: "#3b82f6", fontSize: 11, dx: -4 }}
                    />
                    <Tooltip content={<ChartTooltip />} />
                    {splitDate && (
                      <ReferenceLine
                        x={splitDate}
                        stroke="#16c784"
                        strokeDasharray="4 4"
                        yAxisId="price"
                        label={{ value: "Forecast Start", fill: "#16c784", fontSize: 11 }}
                      />
                    )}
                    <Line
                      yAxisId="price"
                      type="monotone"
                      dataKey="close"
                      name="Historical Price"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                    <Line
                      yAxisId="price"
                      type="monotone"
                      dataKey="forecast"
                      name="30D Forecast"
                      stroke="#16c784"
                      strokeWidth={2.5}
                      strokeDasharray="6 3"
                      dot={{ fill: "#16c784", r: 4 }}
                      connectNulls={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* SECTION D: 30-Day Price Outlook Week-by-Week */}
              <div className="section-header">30-Day Outlook (Weekly Summary)</div>
              {weeklyOutlook.length > 0 && (
                <div className="fc-weekly-list">
                  {weeklyOutlook.map((week) => (
                    <div key={week.weekNum} className="fc-weekly-row">
                      <div className="fc-weekly-row-left">
                        <span className="fc-week-badge">Week {week.weekNum}</span>
                        <span className="fc-week-dates">{week.startDate} &rarr; {week.endDate}</span>
                      </div>
                      <div className="fc-weekly-row-right">
                        <div className="fc-weekly-range">
                          <span>Min: <strong>LKR {week.minPrice.toFixed(2)}</strong></span>
                          <span>Max: <strong>LKR {week.maxPrice.toFixed(2)}</strong></span>
                        </div>
                        <div className="fc-weekly-main-price">
                          <span className="fc-weekly-price">LKR {week.endPrice.toFixed(2)}</span>
                          <span className={`fc-weekly-change ${week.isUp ? "gain" : "loss"}`}>
                            {week.change >= 0 ? "+" : ""}{week.change.toFixed(2)} ({week.changePercent >= 0 ? "+" : ""}{week.changePercent.toFixed(2)}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* SECTION E: Explainable AI (XAI) */}
              <div className="section-header">Explainable AI (XAI)</div>
              <PredictionExplanationCard symbol={symbol} horizon={30} />
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}
