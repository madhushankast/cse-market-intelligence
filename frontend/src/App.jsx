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
            <span className="badge">Milestone 1 Complete</span>
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
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence. Built with FastAPI & React.</p>
      </footer>
    </div>
  );
}

export default App;
