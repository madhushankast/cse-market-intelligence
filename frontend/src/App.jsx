import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "./services/api";
import "./App.css";

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

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.get("http://localhost:8000/")
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(() => {
        setMessage("Unable to connect to backend");
      });
  }, []);

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        <section className="welcome-hero">
          <div className="hero-content">
            <span className="badge">Colombo Stock Exchange &mdash; Market Intelligence Platform</span>
            <h2>Data-Driven CSE Analytics &amp; Forecasting</h2>
            <p className="status-text">
              Backend:{" "}
              <span className="highlight-message">{message || "Connecting…"}</span>
            </p>
          </div>
        </section>

        <section className="dashboard-grid">
          <Link to="/stock" className="dashboard-card nav-card card">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#3b82f6" }}>
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <h3>Stock Analytics</h3>
            <p>View OHLCV price history, market trends, and analytics tables for CSE securities.</p>
            <span className="card-action">Open Stock Data &rarr;</span>
          </Link>

          <Link to="/forecast" className="dashboard-card nav-card card">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#16c784" }}>
                <line x1="12" y1="20" x2="12" y2="10"/>
                <line x1="18" y1="20" x2="18" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="16"/>
              </svg>
            </div>
            <h3>Price Forecast</h3>
            <p>Multi-model predictions: Baseline, SARIMAX, and XGBoost with 30-day price outlook.</p>
            <span className="card-action">View Forecasts &rarr;</span>
          </Link>

          <Link to="/compare" className="dashboard-card nav-card card">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#8b5cf6" }}>
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="3" y1="15" x2="21" y2="15"/>
                <line x1="9" y1="3" x2="9" y2="21"/>
              </svg>
            </div>
            <h3>Model Comparison</h3>
            <p>Compare RMSE, MAE, Accuracy, and R² across models. Ranked with star ratings.</p>
            <span className="card-action">Compare Models &rarr;</span>
          </Link>

          <Link to="/system" className="dashboard-card nav-card card">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#f59e0b" }}>
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>
              </svg>
            </div>
            <h3>System Status</h3>
            <p>Manage background ETL pipelines, monitor data quality checks, and review run history.</p>
            <span className="card-action">Configure System &rarr;</span>
          </Link>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}

export default App;
