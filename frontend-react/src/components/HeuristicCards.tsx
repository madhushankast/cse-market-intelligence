import React from 'react';
import type { HeuristicCard } from '../api';
import {
  CheckCircle2,
  AlertTriangle,
  MinusCircle,
  TrendingUp,
  TrendingDown,
  Activity,
  Layers,
} from 'lucide-react';

interface HeuristicCardsProps {
  heuristics?: HeuristicCard[];
  predictedReturn?: number;
}

export const HeuristicCards: React.FC<HeuristicCardsProps> = ({
  heuristics = [],
}) => {
  if (!heuristics || heuristics.length === 0) {
    return (
      <div className="p-8 text-center bg-surface border border-borderline rounded-xl text-muted font-mono text-sm">
        No heuristic alignment signals available for this asset.
      </div>
    );
  }

  const getStatusBadge = (status: HeuristicCard['status']) => {
    switch (status) {
      case 'Supporting':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Supporting
          </span>
        );
      case 'Rejecting / Risk':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            Rejecting / Risk
          </span>
        );
      case 'Neutral':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/30">
            <MinusCircle className="w-3.5 h-3.5" />
            Neutral
          </span>
        );
    }
  };

  const getSignalBadge = (signal: HeuristicCard['signal']) => {
    switch (signal) {
      case 'Bullish':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-mono font-bold text-bullish">
            <TrendingUp className="w-3 h-3" />
            Bullish Stance
          </span>
        );
      case 'Bearish':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-mono font-bold text-bearish">
            <TrendingDown className="w-3 h-3" />
            Bearish Stance
          </span>
        );
      case 'Neutral':
      default:
        return (
          <span className="inline-flex items-center gap-1 text-xs font-mono text-muted">
            <Activity className="w-3 h-3" />
            Neutral Stance
          </span>
        );
    }
  };

  // Group summary metrics
  const supportingCount = heuristics.filter((h) => h.status === 'Supporting').length;
  const riskCount = heuristics.filter((h) => h.status === 'Rejecting / Risk').length;
  const neutralCount = heuristics.filter((h) => h.status === 'Neutral').length;

  return (
    <div className="flex flex-col gap-5">
      {/* Engine Synthesis Bar */}
      <div className="flex flex-wrap items-center justify-between p-4 bg-surface border border-borderline rounded-xl gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-brand/10 border border-brand/20 text-brand">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-200">
              Dual-Layer Indicator Heuristics Synthesis
            </h4>
            <p className="text-xs text-muted">
              Rule-based validation cross-referencing mathematical forecasts with market indicators
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-subsurface border border-borderline">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-muted">Supporting:</span>
            <span className="text-emerald-400 font-bold">{supportingCount}</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-subsurface border border-borderline">
            <span className="w-2 h-2 rounded-full bg-rose-400" />
            <span className="text-muted">Risk Warnings:</span>
            <span className="text-rose-400 font-bold">{riskCount}</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-subsurface border border-borderline">
            <span className="w-2 h-2 rounded-full bg-slate-400" />
            <span className="text-muted">Neutral:</span>
            <span className="text-slate-300 font-bold">{neutralCount}</span>
          </div>
        </div>
      </div>

      {/* Grid of Indicator Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {heuristics.map((card, idx) => (
          <div
            key={idx}
            className="flex flex-col justify-between p-4 bg-surface border border-borderline rounded-xl hover:border-brand/40 transition-all duration-200 shadow-lg group"
          >
            <div>
              {/* Header: Title and Status */}
              <div className="flex items-start justify-between gap-2 mb-3">
                <span className="text-sm font-semibold text-gray-200 group-hover:text-brand transition-colors">
                  {card.indicator}
                </span>
                {getStatusBadge(card.status)}
              </div>

              {/* Value and Signal */}
              <div className="flex items-baseline justify-between mb-3 px-3 py-2 bg-subsurface/60 rounded-lg border border-borderline/50">
                <div className="flex flex-col">
                  <span className="text-[10px] uppercase font-mono tracking-wider text-muted">
                    Observed Metric
                  </span>
                  <span className="font-mono text-base font-bold text-gray-100">
                    {typeof card.value === 'number'
                      ? Number.isInteger(card.value)
                        ? card.value
                        : card.value.toFixed(3)
                      : card.value}
                  </span>
                </div>
                <div>{getSignalBadge(card.signal)}</div>
              </div>

              {/* Explanation Narrative */}
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                {card.explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
