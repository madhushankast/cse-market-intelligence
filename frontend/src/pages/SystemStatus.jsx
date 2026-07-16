import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import "../App.css";

function SystemStatus() {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState("");

  const fetchStatusAndLogs = () => {
    api.get("/system/status")
      .then(response => {
        setStatus(response.data);
      })
      .catch(err => {
        console.error("Error fetching system status:", err);
        setError("Failed to fetch system status metrics.");
      });

    api.get("/system/pipelines/logs")
      .then(response => {
        setLogs(response.data);
      })
      .catch(err => {
        console.error("Error fetching pipeline logs:", err);
      });
  };

  useEffect(() => {
    fetchStatusAndLogs();
    
    // Refresh status and logs every 7 seconds
    const interval = setInterval(fetchStatusAndLogs, 7000);
    return () => clearInterval(interval);
  }, []);

  const triggerPipeline = () => {
    setTriggering(true);
    setError("");
    api.post("/system/pipelines/run")
      .then(() => {
        setTimeout(fetchStatusAndLogs, 1000);
      })
      .catch(err => {
        console.error("Error triggering pipeline:", err);
        setError("Failed to trigger pipeline execution.");
      })
      .finally(() => {
        setTimeout(() => setTriggering(false), 2000);
      });
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-section">
          <span className="logo-icon">⚙️</span>
          <h1>System Control & Pipelines</h1>
        </div>
        <nav className="nav-links">
          <Link to="/" className="back-link">&larr; Back to Welcome</Link>
          <Link to="/stock" className="back-link">📈 Stock Analytics</Link>
        </nav>
      </header>

      <main className="app-main">
        {error && <div className="error-banner">{error}</div>}

        <section className="status-hero-grid">
          <div className="metric-card bg-gradient-purple">
            <span className="metric-icon">🟢</span>
            <h3>System Status</h3>
            <p className="metric-value capitalize">{status ? status.pipeline : "Connecting..."}</p>
            <p className="metric-subtitle">Overall Platform Health</p>
          </div>

          <div className="metric-card bg-gradient-blue">
            <span className="metric-icon">📂</span>
            <h3>Total Stock Symbols</h3>
            <p className="metric-value">{status ? status.stocks : "..."}</p>
            <p className="metric-subtitle">Colombo Stock Exchange</p>
          </div>

          <div className="metric-card bg-gradient-green">
            <span className="metric-icon">📊</span>
            <h3>Total Price Records</h3>
            <p className="metric-value">{status ? status.records.toLocaleString() : "..."}</p>
            <p className="metric-subtitle">Stored Datapoints</p>
          </div>

          <div className="metric-card bg-gradient-dark">
            <span className="metric-icon">⏰</span>
            <h3>Last Pipeline Run</h3>
            <p className="metric-value font-small">{status ? status.last_pipeline_time : "..."}</p>
            <p className="metric-subtitle">Status: <span className="highlight-status">{status ? status.last_pipeline : "..."}</span></p>
          </div>
        </section>

        <section className="control-panel">
          <div className="panel-header">
            <h2>Data Pipeline Orchestration</h2>
            <button 
              className={`action-btn ${triggering ? "btn-loading" : ""}`}
              onClick={triggerPipeline}
              disabled={triggering || (status && status.last_pipeline === "Running")}
            >
              {triggering || (status && status.last_pipeline === "Running") ? (
                <>
                  <span className="spinner"></span>
                  Orchestrator Running...
                </>
              ) : (
                "Trigger Daily ETL Pipeline"
              )}
            </button>
          </div>
          <p className="panel-desc">
            Executes the ETL process sequentially: fetches stock prices from the CSE, validates structure, processes indicators, parses CB macroeconomic metrics, joins Google Trends, and writes records to the storage layers.
          </p>
        </section>

        <section className="logs-panel">
          <h2>Execution Log History</h2>
          <div className="table-responsive">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Pipeline</th>
                  <th>Started At</th>
                  <th>Finished At</th>
                  <th>Status</th>
                  <th>Records Processed</th>
                  <th>Error / Failure Context</th>
                </tr>
              </thead>
              <tbody>
                {logs.length > 0 ? (
                  logs.map((log) => (
                    <tr key={log.id} className={`log-row-${log.status.toLowerCase()}`}>
                      <td className="font-mono">#{log.id}</td>
                      <td><strong>{log.pipeline}</strong></td>
                      <td className="date-cell">{log.started_at}</td>
                      <td className="date-cell">{log.finished_at || "-"}</td>
                      <td>
                        <span className={`status-badge badge-${log.status.toLowerCase()}`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="num-cell">{log.rows_processed}</td>
                      <td className="error-cell" title={log.error_message}>
                        {log.error_message ? (
                          <span className="error-text">⚠️ {log.error_message}</span>
                        ) : (
                          <span className="success-text">None</span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="empty-table">No pipeline execution logs recorded yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence. Automated ETL & Monitoring.</p>
      </footer>
    </div>
  );
}

export default SystemStatus;
