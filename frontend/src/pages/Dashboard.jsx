import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../services/api";
import MarketMomentumCard from "../components/MarketMomentumCard";
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
            {/* Standardized Page Header Row */}
            <div className="dashboard-header-row">
              <div>
                <h2>CSE Market Intelligence</h2>
                <p className="subtitle">Colombo Stock Exchange Analytics &amp; Forecasting</p>
              </div>
              <div className="live-status-pill">
                <span className="live-dot" />
                <span>Live</span>
              </div>
            </div>

            {/* Primary Above-the-Fold Widget: 4-Factor Market Momentum Sentiment */}
            <MarketMomentumCard
              aspiValue={data?.market?.aspi_benchmark}
              aspiChange={data?.market?.aspi_change}
              stocks={data?.market?.stocks}
              fullMarketBreadth={data?.market?.full_market_breadth}
              marketTurnover={data?.market?.market_turnover}
              concentration={data?.market?.concentration}
              snpValue={data?.market?.snp_benchmark}
              snpChange={data?.market?.snp_change}
            />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}
