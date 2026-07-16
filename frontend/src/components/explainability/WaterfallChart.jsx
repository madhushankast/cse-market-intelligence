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

export default function WaterfallChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="xai-coming-soon">No waterfall data to display</p>;
  }

  // Map values for cumulative representation in Recharts.
  // In a standard waterfall, we plot floating bars between the previous cumulative value and the new cumulative value.
  // Recharts represents this using stacked bar layers: a transparent placeholder layer for the bottom, and a colored layer for the delta.
  const chartData = data.map((d, i) => {
    const isTotal = d.is_total || i === 0 || i === data.length - 1;
    
    // For waterfall steps
    let start = 0;
    let size = 0;

    if (i === 0) {
      // First base bar
      start = 0;
      size = d.cumulative;
    } else if (i === data.length - 1) {
      // Last prediction bar
      start = 0;
      size = d.cumulative;
    } else {
      // Intermediate shifts
      const prevCumulative = data[i - 1].cumulative;
      if (d.value >= 0) {
        start = prevCumulative;
        size = d.value;
      } else {
        start = prevCumulative + d.value;
        size = Math.abs(d.value);
      }
    }

    return {
      name: d.label,
      start: parseFloat(start.toFixed(4)),
      size: parseFloat(size.toFixed(4)),
      value: d.value,
      cumulative: d.cumulative,
      direction: d.direction,
      isTotal,
    };
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="fc-tooltip">
          <p className="fc-tooltip-label">{d.name}</p>
          <p className="fc-tooltip-row" style={{ color: "#e2e8f0" }}>
            Value: <strong>LKR {d.value >= 0 ? "+" : ""}{d.value.toFixed(2)}</strong>
          </p>
          <p className="fc-tooltip-row" style={{ color: "#94a3b8" }}>
            Cumulative: <strong>LKR {d.cumulative.toFixed(2)}</strong>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="xai-chart-container" style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 10, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#9ca3af", fontSize: 9 }}
            axisLine={false}
            tickLine={false}
            interval={0}
            angle={-15}
            textAnchor="end"
          />
          <YAxis
            tick={{ fill: "#9ca3af", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            domain={["auto", "auto"]}
          />
          <Tooltip content={<CustomTooltip />} />
          {/* Stacked bar logic to simulate floating bars */}
          <Bar dataKey="start" stackId="a" fill="transparent" />
          <Bar dataKey="size" stackId="a" radius={[3, 3, 0, 0]}>
            {chartData.map((entry, index) => {
              let fill = "#60a5fa"; // Base/Prediction total
              if (!entry.isTotal) {
                fill = entry.direction === "positive" ? "#34d399" : "#f87171";
              }
              return <Cell key={`cell-${index}`} fill={fill} />;
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
