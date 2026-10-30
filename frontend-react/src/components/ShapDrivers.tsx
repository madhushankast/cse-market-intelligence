import React from 'react';
import type { ShapExplanation, ShapDriver } from '../api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import { Sparkles, ArrowUpRight, ArrowDownRight, Info } from 'lucide-react';

interface ShapDriversProps {
  shapExplanation?: ShapExplanation;
}

export const ShapDrivers: React.FC<ShapDriversProps> = ({ shapExplanation }) => {
  if (!shapExplanation) {
    return (
      <div className="p-8 text-center bg-surface border border-borderline rounded-xl text-muted font-mono text-sm">
        No TreeSHAP mathematical feature attribution available for this stock.
      </div>
    );
  }

  const { base_value, predicted_return, top_positive_drivers = [], top_negative_drivers = [] } =
    shapExplanation;

  // Combine positive and negative drivers into a single sorted list
  const allDrivers: (ShapDriver & { displayName: string; rawFeature: string })[] = [
    ...top_positive_drivers.map((d) => ({
      ...d,
      displayName: d.description || d.feature,
      rawFeature: d.feature,
    })),
    ...top_negative_drivers.map((d) => ({
      ...d,
      displayName: d.description || d.feature,
      rawFeature: d.feature,
    })),
  ].sort((a, b) => b.shap_impact - a.shap_impact);

  const totalShapSum = allDrivers.reduce((acc, curr) => acc + curr.shap_impact, 0);

  return (
    <div className="flex flex-col gap-6">
      {/* Shapley Additive Identity Formula Banner */}
      <div className="p-4 sm:p-5 bg-surface border border-borderline rounded-xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-brand mb-1">
            <Sparkles className="w-4 h-4 shrink-0" />
            <span>EXACT SHAPLEY ADDITIVITY PRINCIPLE</span>
          </div>
          <h3 className="text-base font-semibold text-gray-100 font-mono tracking-tight">
            ŷ_P50 = φ₀ + Σ φᵢ
          </h3>
          <p className="text-xs text-muted mt-1">
            The 30-day predicted return equals the historical base rate plus the exact sum of feature attributions.
          </p>
        </div>

        {/* Breakdown Values */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs font-mono">
          <div className="px-2.5 sm:px-3.5 py-2 rounded-lg bg-subsurface border border-borderline">
            <span className="text-muted block text-[10px] uppercase">Base Value (φ₀)</span>
            <span className="font-bold text-gray-200">
              {(base_value * 100).toFixed(2)}%
            </span>
          </div>

          <span className="text-muted font-bold">+</span>

          <div className="px-2.5 sm:px-3.5 py-2 rounded-lg bg-subsurface border border-borderline">
            <span className="text-muted block text-[10px] uppercase">Net Drivers (Σ φᵢ)</span>
            <span
              className={`font-bold ${
                totalShapSum >= 0 ? 'text-bullish' : 'text-bearish'
              }`}
            >
              {totalShapSum >= 0 ? '+' : ''}
              {(totalShapSum * 100).toFixed(2)}%
            </span>
          </div>

          <span className="text-muted font-bold">=</span>

          <div className="px-2.5 sm:px-3.5 py-2 rounded-lg bg-brand/10 border border-brand/30">
            <span className="text-brand block text-[10px] uppercase">P50 Return (ŷ)</span>
            <span className="font-bold text-brand">
              {(predicted_return * 100).toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* Waterfall Horizontal Bar Chart */}
      <div className="p-4 sm:p-5 bg-surface border border-borderline rounded-xl shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h4 className="text-sm font-semibold text-gray-200">
              Top Mathematical Feature Drivers (SHAP Attribution)
            </h4>
            <p className="text-xs text-muted">
              Marginal contribution of each technical indicator to the final 30-day forecast return
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-bullish">
              <span className="w-2.5 h-2.5 rounded bg-bullish inline-block shrink-0" />
              Positive Lift
            </span>
            <span className="flex items-center gap-1.5 text-bearish">
              <span className="w-2.5 h-2.5 rounded bg-bearish inline-block shrink-0" />
              Negative Drag
            </span>
          </div>
        </div>

        {/* Desktop / Tablet Recharts Waterfall */}
        <div className="hidden sm:block h-[360px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={allDrivers}
              margin={{ top: 10, right: 30, left: 160, bottom: 10 }}
            >
              <XAxis
                type="number"
                tick={{ fill: '#8b949e', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                tickFormatter={(val) => `${(val * 100).toFixed(1)}%`}
                stroke="#30363d"
              />
              <YAxis
                type="category"
                dataKey="displayName"
                tick={{ fill: '#c9d1d9', fontSize: 11, fontFamily: 'system-ui' }}
                stroke="#30363d"
                width={150}
              />
              <ReferenceLine x={0} stroke="#484f58" strokeWidth={1.5} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload;
                    const isPos = item.shap_impact >= 0;
                    return (
                      <div className="p-3 bg-subsurface/95 border border-borderline rounded-lg shadow-2xl backdrop-blur font-mono text-xs">
                        <div className="font-semibold text-gray-200 mb-1">{item.displayName}</div>
                        <div className="text-muted text-[11px] mb-2 font-sans">{item.rawFeature}</div>
                        <div className="flex justify-between gap-4 text-gray-300">
                          <span>Raw Value:</span>
                          <span className="font-bold text-gray-100">
                            {typeof item.value === 'number' ? item.value.toFixed(4) : item.value}
                          </span>
                        </div>
                        <div className="flex justify-between gap-4 mt-1">
                          <span>SHAP Impact:</span>
                          <span className={`font-bold ${isPos ? 'text-bullish' : 'text-bearish'}`}>
                            {isPos ? '+' : ''}
                            {(item.shap_impact * 100).toFixed(3)}%
                          </span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="shap_impact" radius={[4, 4, 4, 4]}>
                {allDrivers.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.shap_impact >= 0 ? '#3fb950' : '#f85149'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Mobile Compact Attribution Bars */}
        <div className="sm:hidden flex flex-col gap-2.5">
          {(() => {
            const maxAbs = Math.max(...allDrivers.map((d) => Math.abs(d.shap_impact)), 0.001);
            return allDrivers.map((driver, idx) => {
              const isPos = driver.shap_impact >= 0;
              const pctWidth = Math.min(100, Math.max(6, (Math.abs(driver.shap_impact) / maxAbs) * 100));
              return (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-subsurface/60 border border-borderline/60 flex flex-col gap-1.5"
                >
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="text-gray-200 font-medium truncate">{driver.displayName}</span>
                    <span className={`font-mono font-bold shrink-0 ${isPos ? 'text-bullish' : 'text-bearish'}`}>
                      {isPos ? '+' : ''}
                      {(driver.shap_impact * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-canvas rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isPos ? 'bg-bullish' : 'bg-bearish'}`}
                      style={{ width: `${pctWidth}%` }}
                    />
                  </div>
                </div>
              );
            });
          })()}
        </div>
      </div>

      {/* Feature Attribution Breakdown Table */}
      <div className="bg-surface border border-borderline rounded-xl overflow-hidden shadow-xl">
        <div className="px-5 py-3 border-b border-borderline flex items-center gap-2">
          <Info className="w-4 h-4 text-brand" />
          <h4 className="text-xs font-mono uppercase tracking-wider text-muted font-semibold">
            Feature Attribution Details
          </h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-borderline bg-subsurface/50 text-muted uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-4">Feature Name</th>
                <th className="py-2.5 px-4">Observed Value</th>
                <th className="py-2.5 px-4">SHAP Contribution</th>
                <th className="py-2.5 px-4">Impact Direction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderline">
              {allDrivers.map((driver, idx) => {
                const isPos = driver.shap_impact >= 0;
                return (
                  <tr key={idx} className="hover:bg-subsurface/40 transition-colors">
                    <td className="py-2.5 px-4">
                      <span className="text-gray-200 font-sans font-medium">{driver.displayName}</span>
                      <span className="block text-[11px] text-muted">{driver.rawFeature}</span>
                    </td>
                    <td className="py-2.5 px-4 text-gray-300">
                      {typeof driver.value === 'number' ? driver.value.toFixed(4) : driver.value}
                    </td>
                    <td className={`py-2.5 px-4 font-bold ${isPos ? 'text-bullish' : 'text-bearish'}`}>
                      {isPos ? '+' : ''}
                      {(driver.shap_impact * 100).toFixed(3)}%
                    </td>
                    <td className="py-2.5 px-4">
                      {isPos ? (
                        <span className="inline-flex items-center gap-1 text-bullish font-semibold">
                          <ArrowUpRight className="w-3.5 h-3.5" />
                          Upward Lift
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-bearish font-semibold">
                          <ArrowDownRight className="w-3.5 h-3.5" />
                          Downside Drag
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
