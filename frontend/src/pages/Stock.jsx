import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import api from "../services/api";
import "../App.css";

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

function Stock() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/stocks/COMB")
      .then(response => {
        setData(response.data.data || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError("Failed to fetch stock prices");
        setLoading(false);
      });
  }, []);

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        <div className="stock-container">
          <div className="stock-header">
            <h2>COMB Stock Analytics</h2>
            <span className="badge secondary">Colombo Stock Exchange</span>
          </div>

          {loading ? (
            <div className="status-container">
              <div className="loader"></div>
              <p>Loading market data…</p>
            </div>
          ) : error ? (
            <div className="status-container error">
              <p className="error-text">{error}</p>
            </div>
          ) : data.length === 0 ? (
            <div className="status-container">
              <p>No historical data found for COMB.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Open</th>
                    <th>High</th>
                    <th>Low</th>
                    <th>Close</th>
                    <th>Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, index) => (
                    <tr key={index}>
                      <td>{item.date}</td>
                      <td>{item.open.toFixed(2)}</td>
                      <td>{item.high.toFixed(2)}</td>
                      <td>{item.low.toFixed(2)}</td>
                      <td className={item.close >= item.open ? "gain" : "loss"}>
                        {item.close.toFixed(2)}
                      </td>
                      <td>{item.volume.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
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

export default Stock;
