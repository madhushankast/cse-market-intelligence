import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

export default function FeatureImportanceChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="xai-coming-soon">No importance data to display</p>;
  }

  // Find max value to center or format chart properly
  const maxVal = Math.max(...data.map(d => Math.abs(d.impact)), 1);

  return (
    <div className="xai-chart-container" style={{ width: "100%", height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            type="number"
            tick={{ fill: "#9ca3af", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            domain={['dataMin - 0.1', 'dataMax + 0.1']}
          />

          <YAxis
            dataKey="feature"
            type="category"
            tick={{ fill: "#9ca3af", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={120}
          />
          <Tooltip
            contentStyle={{
              background: "#1e2330",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "8px",
            }}
            labelStyle={{ color: "#e2e8f0" }}
            itemStyle={{ color: "#94a3b8" }}
            formatter={(val) => [`LKR ${parseFloat(val).toFixed(2)}`, "Impact"]}
          />
          <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.direction === "positive" ? "#34d399" : "#f87171"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
