import React from "react";

export default function ModelBadge({ model, method }) {
  const getColors = () => {
    switch (method) {
      case "shap":
        return { bg: "rgba(99, 102, 241, 0.15)", text: "#818cf8", border: "rgba(99, 102, 241, 0.3)", label: "SHAP" };
      case "sarimax_coefficients":
        return { bg: "rgba(129, 140, 248, 0.15)", text: "#818cf8", border: "rgba(129, 140, 248, 0.3)", label: "Params" };
      case "permutation_importance":
      case "permutation_importance_fallback":
        return { bg: "rgba(52, 211, 153, 0.15)", text: "#34d399", border: "rgba(52, 211, 153, 0.3)", label: "Permutation" };
      default:
        return { bg: "rgba(107, 114, 128, 0.15)", text: "#9ca3af", border: "rgba(107, 114, 128, 0.3)", label: "Placeholder" };
    }
  };

  const meta = getColors();

  return (
    <div style={{ display: "inline-flex", gap: "0.5rem", alignItems: "center" }}>
      <span
        className="badge"
        style={{
          textTransform: "uppercase",
          fontWeight: "bold",
          fontSize: "0.75rem",
        }}
      >
        {model}
      </span>
      <span
        className="badge"
        style={{
          backgroundColor: meta.bg,
          color: meta.text,
          border: `1px solid ${meta.border}`,
          fontSize: "0.7rem",
          fontWeight: 700,
        }}
      >
        {meta.label}
      </span>
    </div>
  );
}
