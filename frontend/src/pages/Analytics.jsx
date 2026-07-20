import { useState, useEffect, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";
import api from "../services/api";
import "./Analytics.css";

const SYMBOLS = ["COMB", "JKH", "DIST", "SAMP", "HNB"];
const VAR_LABELS = {
  usd_lkr: "USD / LKR",
  inflation: "Inflation",
  trend_score: "Google Trends"
};

// ── Shared NavBar ─────────────────────────────────────────────────────────────
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

function ratingClass(rating = "") {
  return rating.toLowerCase().replace(/\s+/g, "-");
}

function ScorePips({ score, max = 5 }) {
  const pips = [];
  for (let i = -max; i <= max; i++) {
    if (i === 0) continue;
    const active = score > 0 ? i > 0 && i <= score
                 : score < 0 ? i < 0 && i >= score
                 : false;
    const cls = active
      ? (score > 0 ? "score-pip active-positive" : "score-pip active-negative")
      : "score-pip";
    pips.push(<span key={i} className={cls} />);
  }
  return <div className="signal-score-pips">{pips}</div>;
}

function RsiGauge({ value }) {
  if (value == null) return null;
  const pct = Math.min(100, Math.max(0, value));

  let zoneLabel = "Neutral";
  if (pct < 30) zoneLabel = "Oversold";
  else if (pct >= 70) zoneLabel = "Overbought";
  else if (pct >= 50) zoneLabel = "Positive Momentum";

  return (
    <div className="rsi-gauge-card">
      <h3>RSI Momentum Gauge</h3>
      <div className="rsi-gauge-wrapper">
        <div className="rsi-gauge-track">
          <div
            className="rsi-gauge-pointer"
            style={{ left: `${pct}%` }}
            title={`RSI: ${value.toFixed(1)}`}
          />
        </div>
        <div className="rsi-gauge-labels">
          <span>0</span>
          <span>30</span>
          <span>50</span>
          <span>70</span>
          <span>100</span>
        </div>
        <div className="rsi-zone-labels">
          <span className="rsi-zone-label oversold">Oversold</span>
          <span className="rsi-zone-label neutral">Neutral</span>
          <span className="rsi-zone-label healthy">Healthy</span>
          <span className="rsi-zone-label overbought">Overbought</span>
        </div>
        <p className="rsi-current-label">
          Current RSI: <strong>{value.toFixed(1)}</strong> &mdash; {zoneLabel}
        </p>
      </div>
    </div>
  );
}

function TrendRow({ closes = [], direction = "" }) {
  if (!closes.length) return null;
  const minV = Math.min(...closes);
  const maxV = Math.max(...closes);
  const range = maxV - minV || 1;
  const MAX_H = 45;
  const MIN_H = 8;

  const dirClass = direction.toLowerCase().includes("rising") ? "rising"
    : direction.toLowerCase().includes("falling") ? "falling"
    : "sideways";

  return (
    <div className="trend-row-card">
      <h3>7-Day Price Trend</h3>
      <div className="trend-row-content">
        <div className="trend-closes">
          {closes.map((v, i) => {
            const h = MIN_H + ((v - minV) / range) * (MAX_H - MIN_H);
            const isUp = i > 0 && v >= closes[i - 1];
            return (
              <div key={i} className="trend-close-item">
                <div
                  className="trend-close-bar"
                  style={{
                    height: h,
                    background: isUp ? "#16c784" : "#ea3943",
                    opacity: 0.8 + (i / closes.length) * 0.2
                  }}
                  title={`Rs. ${v}`}
                />
                <span className="trend-close-val">{v}</span>
              </div>
            );
          })}
        </div>
        <div className="trend-status-container">
          <span className={`trend-direction-badge ${dirClass}`}>{direction}</span>
        </div>
      </div>
    </div>
  );
}

function IndicatorTile({ indicator, value, status, label }) {
  const statusClass = status?.toLowerCase().replace(/\s+/g, "-") || "neutral";
  const displayValue = value == null ? "—"
    : typeof value === "number" && value > 1000 ? value.toLocaleString()
    : typeof value === "number" ? value.toFixed(2)
    : value;

  return (
    <div className="indicator-tile">
      <div className="indicator-tile-header">
        <span className="indicator-tile-name">{indicator}</span>
        <span className={`indicator-status-badge ${statusClass}`}>{status}</span>
      </div>
      <span className="indicator-tile-value">{displayValue}</span>
      <span className="indicator-tile-desc">{label}</span>
    </div>
  );
}

function TechnicalSummary({ symbol, techData }) {
  if (!techData) return null;

  const rc = ratingClass(techData.rating);
  const volLabel = techData.volatility?.label || "";
  const volClass = volLabel.toLowerCase().startsWith("low") ? "low"
    : volLabel.toLowerCase().startsWith("high") ? "high"
    : "moderate";

  // Clean up bullet labels for Section C
  const cleanReasons = techData.reasons?.map(r => r.split(" — ")[0]) || [];
  const cleanWarnings = techData.warnings?.map(w => w.split(" — ")[0]) || [];

  return (
    <div className="analytics-section-group">
      {/* ── SECTION A: Overview Hero Band ── */}
      <div className="section-header">Overview</div>
      <div className="overview-hero-card">
        {/* Left Column: Price Card */}
        <div className={`overview-price-card ${rc}`}>
          <div className="price-card-header">
            <span className="symbol-label">{symbol}</span>
            <span className="price-label">
              {techData.current_price != null ? `Rs. ${techData.current_price.toFixed(2)}` : "—"}
            </span>
            <span className="as-of-label">As of {techData.as_of}</span>
          </div>

          <div className="outlook-rating-row">
            <span className={`signal-dot ${rc}`} />
            <span className={`signal-rating-text ${rc}`}>{techData.rating}</span>
          </div>

          <div className="confidence-block">
            <div className="confidence-metrics">
              <span>Confidence</span>
              <span>{techData.confidence}%</span>
            </div>
            <div className="confidence-track">
              <div className={`confidence-fill ${rc}`} style={{ width: `${techData.confidence}%` }} />
            </div>
          </div>

          <div className="pips-block">
            <ScorePips score={techData.score} max={5} />
            <span className="score-summary">Score: {techData.score > 0 ? "+" : ""}{techData.score} / {techData.score_max}</span>
          </div>

          <div className="meta-details-row">
            {techData.volatility?.label && (
              <div className="meta-item">
                <span className="meta-key">Volatility</span>
                <span className={`volatility-badge ${volClass}`}>{volClass}</span>
              </div>
            )}
            {techData.bollinger?.label && (
              <div className="meta-item">
                <span className="meta-key">Bollinger</span>
                <span className="meta-val">{techData.bollinger.label.split(" — ")[1] || techData.bollinger.label}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Indicator Grid */}
        <div className="overview-indicators-grid">
          {techData.signals?.map((sig) => (
            <IndicatorTile
              key={sig.indicator}
              indicator={sig.indicator}
              value={sig.value}
              status={sig.status}
              label={sig.label}
            />
          ))}
        </div>
      </div>

      {/* ── SECTION B: Momentum & Trend ── */}
      <div className="section-header">Momentum &amp; Trend</div>
      <div className="momentum-trend-grid">
        <RsiGauge value={techData.rsi_value} />
        <TrendRow closes={techData.recent_closes} direction={techData.trend_direction} />
      </div>

      {/* ── SECTION C: Signals (Bullet lists only + footnote disclaimer) ── */}
      <div className="section-header">Signals</div>
      <div className="signals-panel-card">
        <div className="signals-split-content">
          <div className="signals-col strengths">
            <h4>Supporting Strengths</h4>
            <ul>
              {cleanReasons.length > 0 ? cleanReasons.map((r, i) => (
                <li key={i} className="signal-bullet pos">
                  <span className="bullet-indicator">&#10003;</span>
                  {r}
                </li>
              )) : <li className="empty-bullet-item">No positive momentum triggers.</li>}
            </ul>
          </div>

          <div className="signals-col cautions">
            <h4>Risk &amp; Caution Flags</h4>
            <ul>
              {cleanWarnings.length > 0 ? cleanWarnings.map((w, i) => (
                <li key={i} className="signal-bullet neg">
                  <span className="bullet-indicator">!</span>
                  {w}
                </li>
              )) : <li className="empty-bullet-item">No risk warnings detected.</li>}
            </ul>
          </div>
        </div>

        <div className="footnote-disclaimer">
          Disclaimer: This summary is dynamically computed using a mathematical indicator scoring model for educational and informational purposes. It does not constitute investment advice. Market conditions can change rapidly — always conduct your own research before making investment decisions.
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
export default function Analytics() {
  const [symbol, setSymbol] = useState("COMB");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [correlation, setCorrelation] = useState(null);
  const [causality, setCausality] = useState([]);
  const [lagData, setLagData] = useState({});
  const [techData, setTechData] = useState(null);
  const [techLoading, setTechLoading] = useState(false);
  const [techError, setTechError] = useState("");

  const loadData = useCallback(async (sym) => {
    setLoading(true);
    setTechLoading(true);
    setError("");
    setTechError("");

    const [statsResult, techResult] = await Promise.allSettled([
      Promise.all([
        api.get(`/analytics/${sym}/correlation`),
        api.get(`/analytics/${sym}/causality`),
        api.get(`/analytics/${sym}/lag`)
      ]),
      api.get(`/analytics/${sym}/technical-summary`)
    ]);

    if (statsResult.status === "fulfilled") {
      const [corrRes, causRes, lagRes] = statsResult.value;
      setCorrelation(corrRes.data);
      setCausality(causRes.data);
      setLagData(lagRes.data);
    } else {
      console.error(statsResult.reason);
      setError("Failed to fetch analytics datasets. Ensure symbols are ingested.");
    }
    setLoading(false);

    if (techResult.status === "fulfilled") {
      setTechData(techResult.value.data);
    } else {
      console.error(techResult.reason);
      setTechError("Technical summary unavailable for this symbol.");
    }
    setTechLoading(false);
  }, []);

  useEffect(() => {
    loadData(symbol);
  }, [symbol, loadData]);

  const formatLabel = (val) => {
    if (VAR_LABELS[val]) return VAR_LABELS[val];
    return val.replace("_", " ").toUpperCase();
  };

  const getCellColor = (val) => {
    const abs = Math.abs(val);
    const alpha = abs * 0.85;
    return val >= 0
      ? `rgba(22, 199, 132, ${alpha})`
      : `rgba(234, 57, 67, ${alpha})`;
  };

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        <div className="analytics-page">

          {/* ── Page Header & Ticker Tabs ── */}
          <div className="analytics-page-title-row">
            <h2>Market Relationships &amp; Analytics</h2>
            <p className="subtitle">Statistical correlations, leading indicators, and technical signals</p>
            <div className="symbol-picker">
              {SYMBOLS.map((s) => (
                <button
                  key={s}
                  className={`symbol-btn ${symbol === s ? "active" : ""}`}
                  onClick={() => setSymbol(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* ── Section A, B, C ── */}
          {techLoading ? (
            <div className="fc-loading" style={{ padding: "2rem" }}>
              <div className="fc-spinner" />
              <p>Calculating technical signals for <strong>{symbol}</strong>…</p>
            </div>
          ) : techError ? (
            <div className="fc-error">
              <div>
                <strong>Technical Summary Unavailable</strong>
                <p>{techError}</p>
              </div>
            </div>
          ) : techData ? (
            <TechnicalSummary symbol={symbol} techData={techData} />
          ) : null}

          {/* ── SECTION D: Statistical Relationships ── */}
          <div className="section-header">Statistical Relationships</div>
          {loading ? (
            <div className="fc-loading">
              <div className="fc-spinner" />
              <p>Running statistical tests for <strong>{symbol}</strong>…</p>
            </div>
          ) : error ? (
            <div className="fc-error">
              <div>
                <strong>Analytics Unavailable</strong>
                <p>{error}</p>
              </div>
            </div>
          ) : (
            <div className="statistical-section-grid">
              {/* Feature Correlation Matrix (Full Width) */}
              <div className="correlation-matrix-card">
                <h3>Feature Correlation Matrix</h3>
                <p className="card-desc">Pearson linear correlation strength. Values near ±1 indicate strong relationships. Green = positive, Red = negative.</p>
                {correlation && correlation.columns && correlation.columns.length > 0 ? (
                  <div className="matrix-wrapper">
                    <table className="correlation-heatmap-table">
                      <thead>
                        <tr>
                          <th></th>
                          {correlation.columns.map((c) => (
                            <th key={c} className="heatmap-th-flat">
                              {formatLabel(c)}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {correlation.columns.map((rowCol) => (
                          <tr key={rowCol}>
                            <td className="heatmap-row-label">{formatLabel(rowCol)}</td>
                            {correlation.columns.map((colCol) => {
                              const match = correlation.pearson.find(
                                (p) => p.x === rowCol && p.y === colCol
                              );
                              const val = match ? match.value : 0.0;
                              return (
                                <td
                                  key={colCol}
                                  className="heatmap-cell expanded"
                                  style={{ backgroundColor: getCellColor(val) }}
                                  title={`${formatLabel(rowCol)} vs ${formatLabel(colCol)}: ${val}`}
                                >
                                  {val.toFixed(2)}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="no-data-hint">No correlation data available for {symbol}.</p>
                )}
              </div>

              {/* Causality and Trends side-by-side */}
              <div className="causality-trends-split-row">
                {/* Granger Causality */}
                <div className="analytics-card split-half">
                  <h3>Granger Causality &mdash; Leading Indicators</h3>
                  <p className="card-desc">Tests whether past values of alternative data help predict stock price returns.</p>
                  {causality && causality.length > 0 ? (
                    <div className="table-responsive">
                      <table className="causality-table">
                        <thead>
                          <tr>
                            <th>Indicator</th>
                            <th>Lag</th>
                            <th>p-value</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {causality.map((c) => (
                            <tr key={c.variable}>
                              <td className="variable-cell">{VAR_LABELS[c.variable] || c.variable}</td>
                              <td>{c.best_lag} days</td>
                              <td>{c.p_value.toFixed(4)}</td>
                              <td>
                                <span className={`causality-badge ${c.significant ? "sig" : "non-sig"}`}>
                                  {c.significant ? "Significant" : "Not Significant"}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="empty-state-container">
                      <p className="no-data-hint">No causality indicators for {symbol}.</p>
                    </div>
                  )}
                </div>

                {/* Cross Correlation / Lag */}
                <div className="analytics-card split-half">
                  <h3>Google Trends Lag Analysis</h3>
                  <p className="card-desc">Peak correlation at positive lags indicates search interest leads stock movement by L days.</p>
                  {lagData.trend_score && lagData.trend_score.length > 0 ? (
                    <div style={{ width: "100%", height: 230 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={lagData.trend_score} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                          <XAxis
                            dataKey="lag"
                            tick={{ fill: "#7a8fa6", fontSize: 10 }}
                            label={{ value: "Lag (days)", position: "insideBottom", offset: -2, fill: "#7a8fa6", fontSize: 10 }}
                          />
                          <YAxis
                            tick={{ fill: "#7a8fa6", fontSize: 10 }}
                            domain={[-1, 1]}
                            label={{ value: "Correlation", angle: -90, position: "insideLeft", fill: "#7a8fa6", fontSize: 10 }}
                          />
                          <Tooltip
                            contentStyle={{ background: "#111c2d", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "8px" }}
                            labelStyle={{ color: "#e2e8f0" }}
                            itemStyle={{ color: "#3b82f6" }}
                            formatter={(val) => [val.toFixed(3), "Correlation"]}
                          />
                          <ReferenceLine y={0} stroke="#3d4f63" strokeDasharray="3 3" />
                          <ReferenceLine x={0} stroke="#3d4f63" strokeDasharray="3 3" />
                          <Line
                            type="monotone"
                            dataKey="correlation"
                            name="Lag correlation"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            dot={{ r: 3, fill: "#3b82f6" }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="empty-state-container">
                      <p className="no-data-hint">No lag analytics data available.</p>
                    </div>
                  )}
                </div>
              </div>
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
