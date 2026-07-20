import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../services/api";
import "./Dashboard.css";

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

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await api.get("/dashboard");
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to connect to backend server. Re-check server status.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        {loading ? (
          <div className="fc-loading">
            <div className="fc-spinner" />
            <p>Loading market intelligence data…</p>
          </div>
        ) : error ? (
          <div className="fc-error">
            <div>
              <strong>Service Offline</strong>
              <p>{error}</p>
              <button className="btn-secondary" onClick={fetchDashboardData} style={{ marginTop: "0.75rem" }}>
                Retry Connection
              </button>
            </div>
          </div>
        ) : (
          <div className="dashboard-page">
            <section className="welcome-hero">
              <div className="hero-content">
                <span className="badge">CSE Market Intelligence Platform</span>
                <h2>Colombo Stock Exchange Analytics &amp; Forecasting</h2>
                <p className="status-text">
                  Pipeline Status:{" "}
                  <span className={`status-pill ${data.pipeline?.status === "healthy" ? "healthy" : "unhealthy"}`}>
                    {data.pipeline?.status === "healthy" ? "Operational" : "Degraded"}
                  </span>
                </p>
              </div>
            </section>

            {/* KPI Grid */}
            <div className="kpi-grid">
              <div className="db-card kpi">
                <span className="card-label">ASPI Index</span>
                <span className="card-value">{data.market?.aspi_benchmark?.toLocaleString() ?? "N/A"}</span>
                <span className="card-sub-gain">+{data.market?.aspi_change}%</span>
                {data.market?.aspi_note && (
                  <span className="card-sub" style={{ fontSize: "0.7rem", opacity: 0.55, marginTop: "0.2rem" }}>
                    {data.market.aspi_note}
                  </span>
                )}
              </div>

              <div className="db-card kpi">
                <span className="card-label">Total Data Points</span>
                <span className="card-value">{data.market?.total_records?.toLocaleString() ?? "N/A"}</span>
                <span className="card-sub">Historical OHLCV records</span>
              </div>

              <div className="db-card kpi">
                <span className="card-label">Tracked Tickers</span>
                <span className="card-value">{data.market?.unique_symbols ?? "N/A"}</span>
                <span className="card-sub">Active CSE symbols</span>
              </div>

              <div className="db-card kpi">
                <span className="card-label">Last Ingestion</span>
                <span className="card-value" style={{ fontSize: "1.4rem" }}>{data.pipeline?.last_run ?? "N/A"}</span>
                <span className="card-sub">ETL pipeline timestamp</span>
              </div>
            </div>

            <div className="dashboard-split-grid">
              {/* Left: Top Stocks */}
              <div className="db-card split-section">
                <h3>CSE Top Securities</h3>
                <div className="table-responsive">
                  <table className="stocks-summary-table">
                    <thead>
                      <tr>
                        <th>Symbol</th>
                        <th>Close (LKR)</th>
                        <th>Change</th>
                        <th>Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.market?.stocks?.map((s) => {
                        const isGain = s.change_pct >= 0;
                        return (
                          <tr key={s.symbol}>
                            <td className="symbol-cell">
                              <Link to={`/stock?symbol=${s.symbol}`}>{s.symbol}</Link>
                            </td>
                            <td>Rs. {s.close.toFixed(2)}</td>
                            <td className={isGain ? "gain" : "loss"}>
                              {isGain ? "▲" : "▼"} {Math.abs(s.change_pct).toFixed(2)}%
                            </td>
                            <td>{s.volume.toLocaleString()}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Right: Forecast + Status */}
              <div className="split-right-col">
                <div className="db-card forecast-summary-card">
                  <h3>30-Day Forecast (COMB)</h3>
                  {data.forecast ? (
                    <div className="forecast-detail-inline">
                      <div className="forecast-metric-block">
                        <span className="forecast-metric-label">Predicted Close</span>
                        <span className="forecast-metric-value">Rs. {data.forecast.prediction}</span>
                      </div>
                      <div className="forecast-metric-block">
                        <span className="forecast-metric-label">Best Model</span>
                        <span className="forecast-metric-badge">{data.forecast.model}</span>
                      </div>
                      <div className="forecast-metric-block">
                        <span className="forecast-metric-label">Confidence</span>
                        <span className="forecast-metric-value">{(data.forecast.confidence * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  ) : (
                    <p className="no-data-hint">No active predictions. Run forecasting first.</p>
                  )}
                  <Link to="/forecast" className="btn-primary-card">Open Forecasting Outlook &rarr;</Link>
                </div>

                <div className="db-card status-summary-card">
                  <h3>System &amp; Data Pipeline</h3>
                  <div className="status-row">
                    <span>Database Records:</span>
                    <strong>{data.market?.total_records?.toLocaleString() ?? "N/A"}</strong>
                  </div>
                  <div className="status-row">
                    <span>Tracked Tickers:</span>
                    <strong>{data.market?.unique_symbols ?? "N/A"}</strong>
                  </div>
                  <div className="status-row">
                    <span>Last Ingestion:</span>
                    <span>{data.pipeline?.last_run ?? "N/A"}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}
