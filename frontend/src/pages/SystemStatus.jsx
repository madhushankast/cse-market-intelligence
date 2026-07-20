import { useState, useEffect } from "react";
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

  const isPipelineRunning = triggering || (status && status.last_pipeline === "Running");

  return (
    <div className="app-container">
      <NavBar />

      <main className="app-main">
        {error && <div className="error-banner">{error}</div>}

        <div className="analytics-page-title-row">
          <h2>System Performance &amp; Pipelines</h2>
          <p className="subtitle">ETL orchestration pipelines and telemetry checks</p>
        </div>

        {/* SECTION A: Overview Hero Metrics */}
        <div className="section-header">System Health &amp; Telemetry</div>
        <div className="fc-kpi-row-restructured">
          <div className="fc-kpi-card" style={{ "--accent": status?.pipeline === "healthy" ? "var(--gain)" : "var(--loss)" }}>
            <p className="fc-kpi-label">System Health</p>
            <p className="fc-kpi-value capitalize" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="signal-dot" style={{
                display: "inline-block", width: 10, height: 10, borderRadius: "50%",
                background: status?.pipeline === "healthy" ? "var(--gain)" : "var(--loss)",
                boxShadow: status?.pipeline === "healthy" ? "0 0 8px var(--gain)" : "0 0 8px var(--loss)"
              }} />
              {status ? status.pipeline : "—"}
            </p>
            <p className="fc-kpi-sub">Overall Platform Status</p>
          </div>

          <div className="fc-kpi-card" style={{ "--accent": "#3b82f6" }}>
            <p className="fc-kpi-label">Tracked Symbols</p>
            <p className="fc-kpi-value">{status ? status.stocks : "—"}</p>
            <p className="fc-kpi-sub">Colombo Stock Exchange</p>
          </div>

          <div className="fc-kpi-card" style={{ "--accent": "var(--gain)" }}>
            <p className="fc-kpi-label">Total Price Records</p>
            <p className="fc-kpi-value">{status ? status.records.toLocaleString() : "—"}</p>
            <p className="fc-kpi-sub">Stored OHLCV datapoints</p>
          </div>

          <div className="fc-kpi-card" style={{ "--accent": "#6b7280" }}>
            <p className="fc-kpi-label">Last Pipeline Run</p>
            <p className="fc-kpi-value" style={{ fontSize: "1.1rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {status ? status.last_pipeline_time : "—"}
            </p>
            <p className="fc-kpi-sub">
              Status: <span style={{ fontWeight: 700, color: "var(--accent-color)" }}>{status ? status.last_pipeline : "—"}</span>
            </p>
          </div>
        </div>

        {/* SECTION B: Pipeline Orchestration Panel */}
        <div className="section-header">Pipeline Orchestration</div>
        <div className="signals-panel-card">
          <div className="signals-split-content" style={{ display: "grid", gridTemplateColumns: "1fr auto", alignItems: "center", gap: "2rem" }}>
            <div>
              <h4 style={{ color: "var(--text-primary)", fontSize: "0.95rem", textTransform: "none", letterSpacing: "normal", margin: "0 0 0.5rem 0" }}>
                ETL Processing Control
              </h4>
              <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                Executes the data pipeline sequentially: fetches stock prices from CSE, validates structure,
                processes macroeconomic indicators from CBSL, joins Google Trends data, and writes records
                to the storage layer.
              </p>
            </div>
            <div>
              <button
                className={`action-btn ${isPipelineRunning ? "btn-loading" : ""}`}
                onClick={triggerPipeline}
                disabled={isPipelineRunning}
                style={{
                  padding: "0.75rem 1.5rem", fontSize: "0.85rem", fontWeight: 700,
                  borderRadius: "8px", border: "none", cursor: isPipelineRunning ? "not-allowed" : "pointer",
                  background: isPipelineRunning ? "rgba(255,255,255,0.05)" : "var(--accent-color)",
                  color: "white", display: "inline-flex", alignItems: "center", gap: "0.5rem"
                }}
              >
                {isPipelineRunning ? (
                  <>
                    <span className="spinner" style={{
                      width: "14px", height: "14px", border: "2px solid rgba(255,255,255,0.2)",
                      borderTopColor: "white", borderRadius: "50%", display: "inline-block",
                      animation: "spin 0.8s linear infinite"
                    }}></span>
                    Pipeline Running…
                  </>
                ) : (
                  "Trigger ETL Pipeline"
                )}
              </button>
            </div>
          </div>
        </div>

        {/* SECTION C: Execution History logs */}
        <div className="section-header">Execution Log History</div>
        <div className="fc-model-table-card" style={{ padding: "1.25rem" }}>
          <div className="table-responsive">
            <table className="fc-performance-table">
              <thead>
                <tr>
                  <th style={{ textAlign: "left" }}>Job ID</th>
                  <th>Pipeline Name</th>
                  <th>Started Timestamp</th>
                  <th>Finished Timestamp</th>
                  <th>Status</th>
                  <th>Processed Rows</th>
                  <th style={{ textAlign: "right" }}>Logs/Errors</th>
                </tr>
              </thead>
              <tbody>
                {logs.length > 0 ? (
                  logs.map((log) => (
                    <tr key={log.id} className="fc-model-table-row">
                      <td style={{ textAlign: "left", fontFamily: "monospace", fontSize: "0.85rem" }}>#{log.id}</td>
                      <td><strong>{log.pipeline}</strong></td>
                      <td>{log.started_at}</td>
                      <td>{log.finished_at || "—"}</td>
                      <td>
                        <span className={`indicator-status-badge ${log.status.toLowerCase()}`}>
                          {log.status}
                        </span>
                      </td>
                      <td>{log.rows_processed}</td>
                      <td style={{ textAlign: "right", maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {log.error_message ? (
                          <span style={{ color: "var(--loss)", fontSize: "0.8rem" }} title={log.error_message}>{log.error_message}</span>
                        ) : (
                          <span style={{ color: "var(--gain)", fontSize: "0.8rem" }}>None</span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="empty-table" style={{ padding: "2rem", color: "var(--text-secondary)", fontStyle: "italic" }}>
                      No pipeline execution logs recorded yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} CSE Market Intelligence &mdash; Colombo Stock Exchange Analytics Platform</p>
      </footer>
    </div>
  );
}

export default SystemStatus;
