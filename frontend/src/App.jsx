import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "./services/api";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // API root doesn't have /api/v1 prefix, we fetch it by overriding the path or using full URL
    api.get("http://localhost:8000/")
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.log(error);
        setMessage("Failed to connect to backend server");
      });
  }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-icon">📊</span>
          <h1>CSE Market Intelligence</h1>
        </div>
      </header>

      <main className="app-main">
        <section className="welcome-hero">
          <div className="hero-content">
            <span className="badge">Milestone 9 — Forecasting Engine</span>
            <h2>Colombo Stock Exchange Intelligence Platform</h2>
            <p className="status-text">
              Backend Status: <span className="highlight-message">{message || "Connecting..."}</span>
            </p>
          </div>
        </section>

        <section className="dashboard-grid">
          <Link to="/stock" className="dashboard-card nav-card">
            <div className="card-icon">📈</div>
            <h3>Stock Analytics</h3>
            <p>View Colombo Stock Exchange prices, trends, and analytics tables.</p>
            <span className="card-action">Open Stock Data &rarr;</span>
          </Link>

          <Link to="/forecast" className="dashboard-card nav-card">
            <div className="card-icon">🔮</div>
            <h3>Price Forecast</h3>
            <p>Multi-model predictions: Baseline, SARIMAX, and XGBoost with 7-day outlook.</p>
            <span className="card-action">View Forecasts &rarr;</span>
          </Link>

          <Link to="/compare" className="dashboard-card nav-card">
            <div className="card-icon">🏆</div>
            <h3>Model Comparison</h3>
            <p>Compare RMSE, MAE, MAPE, and R² across models. Ranked with star ratings.</p>
            <span className="card-action">Compare Models &rarr;</span>
          </Link>

          <Link to="/system" className="dashboard-card nav-card">
            <div className="card-icon">⚙️</div>
            <h3>System Status</h3>
            <p>Manage background ETL pipelines, monitor data quality checks, and check run history.</p>
            <span className="card-action">Configure System &rarr;</span>
          </Link>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence. Built with FastAPI & React.</p>
      </footer>
    </div>
  );
}

export default App;
