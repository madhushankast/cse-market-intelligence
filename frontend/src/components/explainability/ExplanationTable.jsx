import React from "react";

export default function ExplanationTable({ features }) {
  if (!features || features.length === 0) {
    return <p className="xai-coming-soon">No features to display</p>;
  }

  return (
    <div className="table-responsive" style={{ marginTop: "1rem" }}>
      <table className="data-table" style={{ width: "100%" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Rank</th>
            <th style={{ textAlign: "left" }}>Feature</th>
            <th style={{ textAlign: "right" }}>Impact (LKR)</th>
            <th style={{ textAlign: "center" }}>Direction</th>
          </tr>
        </thead>
        <tbody>
          {features.map((f, idx) => (
            <tr key={idx}>
              <td>#{idx + 1}</td>
              <td style={{ fontWeight: 600 }}>{f.feature}</td>
              <td
                style={{
                  textAlign: "right",
                  color: f.direction === "positive" ? "#34d399" : "#f87171",
                  fontFamily: "monospace",
                }}
              >
                {f.impact >= 0 ? "+" : ""}
                {f.impact.toFixed(4)}
              </td>
              <td style={{ textAlign: "center" }}>
                <span
                  className="badge"
                  style={{
                    backgroundColor:
                      f.direction === "positive"
                        ? "rgba(52, 211, 153, 0.1)"
                        : "rgba(248, 113, 113, 0.1)",
                    color: f.direction === "positive" ? "#34d399" : "#f87171",
                    border: `1px solid ${
                      f.direction === "positive" ? "rgba(52,211,153,0.2)" : "rgba(248,113,113,0.2)"
                    }`,
                  }}
                >
                  {f.direction === "positive" ? "Raises Price ▲" : "Lowers Price ▼"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
