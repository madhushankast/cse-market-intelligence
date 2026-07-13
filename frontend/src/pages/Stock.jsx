import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

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
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-icon">📊</span>
          <h1>CSE Market Intelligence</h1>
        </div>
        <Link to="/" className="back-btn">&larr; Back to Home</Link>
      </header>

      <main className="app-main">
        <div className="stock-container">
          <div className="stock-header">
            <h2>COMB Stock Analytics</h2>
            <span className="badge secondary">Colombo Stock Exchange</span>
          </div>

          {loading ? (
            <div className="status-container">
              <div className="loader"></div>
              <p>Loading market data...</p>
            </div>
          ) : error ? (
            <div className="status-container error">
              <p className="error-text">❌ {error}</p>
            </div>
          ) : data.length === 0 ? (
            <div className="status-container info">
              <p>No historical transactions found for COMB.</p>
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
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence. Built with FastAPI & React.</p>
      </footer>
    </div>
  );
}

export default Stock;
