import React from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  Award,
  Layers,
  Sparkles,
  ShieldAlert,
  Database,
  Sliders,
  GitBranch,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  MinusCircle,
} from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col gap-6 sm:gap-8 py-4 sm:py-6 max-w-[1400px] mx-auto px-3 sm:px-6 lg:px-8">
      {/* 1. Hero Section */}
      <section className="rounded-xl border border-borderline bg-surface p-5 sm:p-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-subsurface border border-borderline text-gray-300 font-mono text-[10px] sm:text-xs mb-3">
              <Sparkles className="w-3.5 h-3.5 text-brand shrink-0" />
              <span className="truncate">COLOMBO STOCK EXCHANGE &bull; QUANTITATIVE FORECASTING ENGINE</span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-gray-100 font-sans leading-tight">
              CSE Market Intelligence Platform
            </h1>

            <p className="mt-2.5 text-sm sm:text-base text-gray-300 leading-relaxed font-sans">
              End-to-end 30-day equity return forecasting powered by Multi-Quantile LightGBM, TreeSHAP
              feature attribution, and purged walk-forward validation across 26 Colombo Stock Exchange equities.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col xl:flex-row items-stretch sm:items-center gap-3 shrink-0">
            <Link
              to="/terminal"
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-brand hover:bg-sky-400 text-gray-950 font-semibold text-xs sm:text-sm transition-colors"
            >
              <TrendingUp className="w-4 h-4" />
              <span>Launch Trading Terminal</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/benchmarks"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-subsurface hover:bg-borderline border border-borderline text-gray-200 font-semibold text-xs sm:text-sm transition-colors"
            >
              <Award className="w-4 h-4 text-brand" />
              <span>Model Benchmarks</span>
            </Link>

            <Link
              to="/pipeline"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-subsurface hover:bg-borderline border border-borderline text-gray-200 font-semibold text-xs sm:text-sm transition-colors"
            >
              <Database className="w-4 h-4 text-emerald-400" />
              <span>Data Pipeline</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. FIRST: USER GUIDE — How to Interpret the Trading Terminal */}
      <section className="rounded-xl bg-surface border border-borderline p-5 sm:p-7 flex flex-col gap-5">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-borderline pb-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
              USER GUIDE
            </span>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-100 mt-1">
              How to Interpret the Trading Terminal
            </h2>
            <p className="text-xs sm:text-sm text-muted mt-1 font-sans">
              The platform provides both quantitative forecast bounds and rule-based heuristic indicator statuses.
            </p>
          </div>
          <Link
            to="/terminal"
            className="text-xs font-mono text-brand hover:underline inline-flex items-center gap-1 shrink-0"
          >
            <span>Open Terminal</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Indicator Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 sm:p-5 rounded-xl bg-subsurface border border-emerald-500/30 flex flex-col justify-between gap-3">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400 font-mono font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>Supporting Signals (Green)</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  CONFIRMS
                </span>
              </div>
              <p className="text-xs text-gray-300 font-sans leading-relaxed">
                The technical indicator independently validates and agrees with the model&apos;s 30-day directional forecast (e.g. oversold RSI confirming a forecasted bounce, or a bullish moving average crossover).
              </p>
            </div>
            <div className="pt-2.5 border-t border-borderline/60 text-[11px] font-mono text-emerald-400">
              High conviction alignment with P50 trajectory
            </div>
          </div>

          <div className="p-4 sm:p-5 rounded-xl bg-subsurface border border-rose-500/30 flex flex-col justify-between gap-3">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-rose-400 font-mono font-bold text-sm">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>Rejecting / Risk Warnings (Red)</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  CAUTION
                </span>
              </div>
              <p className="text-xs text-gray-300 font-sans leading-relaxed">
                The technical indicator warns of contrary pressure that may cap the trajectory (e.g. overbought divergence, elevated volatility, or broad ASPI benchmark selling drag).
              </p>
            </div>
            <div className="pt-2.5 border-t border-borderline/60 text-[11px] font-mono text-rose-400">
              Monitor P10 downside floor &amp; position sizing
            </div>
          </div>

          <div className="p-4 sm:p-5 rounded-xl bg-subsurface border border-slate-500/30 flex flex-col justify-between gap-3">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-300 font-mono font-bold text-sm">
                  <MinusCircle className="w-4 h-4 shrink-0" />
                  <span>Neutral / Indecision (Slate)</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-500/10 text-slate-300 border border-slate-500/20">
                  NEUTRAL
                </span>
              </div>
              <p className="text-xs text-gray-300 font-sans leading-relaxed">
                The metric sits in an equilibrium range without offering strong directional conviction (e.g. RSI between 45 and 55, or normal baseline trading volume).
              </p>
            </div>
            <div className="pt-2.5 border-t border-borderline/60 text-[11px] font-mono text-slate-400">
              No secondary override on primary ML forecast
            </div>
          </div>
        </div>

        {/* Quick Forecast Bound Reference Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          <div className="px-4 py-3 rounded-lg bg-subsurface border border-borderline flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm bg-bearish shrink-0" />
              <span className="text-xs font-mono font-semibold text-gray-200">P10 Bearish Bound</span>
            </div>
            <span className="text-[11px] font-mono text-muted">10th Percentile VaR Floor</span>
          </div>

          <div className="px-4 py-3 rounded-lg bg-subsurface border border-borderline flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm bg-sky-400 shrink-0" />
              <span className="text-xs font-mono font-semibold text-gray-200">P50 Base Trajectory</span>
            </div>
            <span className="text-[11px] font-mono text-muted">Median 30d Expected Path</span>
          </div>

          <div className="px-4 py-3 rounded-lg bg-subsurface border border-borderline flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm bg-bullish shrink-0" />
              <span className="text-xs font-mono font-semibold text-gray-200">P90 Bullish Bound</span>
            </div>
            <span className="text-[11px] font-mono text-muted">90th Percentile Upside Ceiling</span>
          </div>
        </div>
      </section>

      {/* 3. SECOND: METHODOLOGY & TARGET FORMULATION */}
      <section className="rounded-xl bg-surface border border-borderline p-5 sm:p-7 flex flex-col gap-5">
        <div className="border-b border-borderline pb-4">
          <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
            METHODOLOGY &amp; TARGET FORMULATION
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-100 mt-1">
            Why Predicting Raw Nominal Prices is an Anti-Pattern
          </h2>
          <p className="text-xs sm:text-sm text-muted mt-1 font-sans">
            How we formulate stationary forward return targets and calibrate probabilistic uncertainty cones.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Random Walk Illusion */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mb-3.5">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-gray-100 mb-2">
                The Non-Stationary Price Trap
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Forecasting nominal levels creates an illusion of high R-squared while simply learning a delayed lag of yesterday&apos;s price. Financial prices are non-stationary random walks with unbounded variance.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-borderline font-mono text-[11px] text-rose-400">
              Anti-pattern: MSE on nominal prices
            </div>
          </div>

          {/* Card 2: Cumulative Log Return */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-lg bg-surface border border-borderline text-brand flex items-center justify-center mb-3.5">
                <Sliders className="w-4 h-4" />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-gray-100 mb-2">
                Cumulative Forward Log Return Target
              </h3>
              <p className="text-xs text-gray-300 leading-relaxed font-sans">
                Our models predict the stationary 30-day forward cumulative log return:
              </p>
              <div className="my-3 p-2.5 bg-surface rounded-lg border border-borderline text-center font-mono text-xs sm:text-sm text-brand font-bold">
                {'y_t = ln( P_{t+30} / P_t )'}
              </div>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Log returns are time-additive, symmetric, and preserve stationarity without lookahead leakage.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-borderline font-mono text-[11px] text-brand">
              Target: Stationary 30-day drift
            </div>
          </div>

          {/* Card 3: Multi-Quantile Asymmetric Loss */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3.5">
                <TrendingUp className="w-4 h-4" />
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-gray-100 mb-2">
                Multi-Quantile Uncertainty Cones
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Point predictions fail to communicate market risk. We train 3 simultaneous LightGBM models optimizing Pinball Loss across quantiles:
              </p>
              <ul className="mt-3 space-y-1.5 text-xs font-mono text-gray-300">
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded bg-bearish" />
                  <span>P10: 90% Value-at-Risk Downside Floor</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded bg-sky-400" />
                  <span>P50: Median Expected Trajectory</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded bg-bullish" />
                  <span>P90: 90th % Bullish Upside Ceiling</span>
                </li>
              </ul>
            </div>
            <div className="mt-4 pt-3 border-t border-borderline font-mono text-[11px] text-emerald-400">
              Loss: Quantile Pinball Calibration
            </div>
          </div>
        </div>
      </section>

      {/* 4. THIRD: SYSTEM BLUEPRINT — End-to-End MLOps Pipeline Architecture */}
      <section className="rounded-xl bg-surface border border-borderline p-5 sm:p-7 flex flex-col gap-5">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-borderline pb-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
              SYSTEM BLUEPRINT
            </span>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-100 mt-1">
              End-to-End MLOps Pipeline Architecture
            </h2>
            <p className="text-xs sm:text-sm text-muted mt-1 font-sans">
              Automated CSE market ingestion, feature engineering, purged cross-validation, and dual-layer explainability.
            </p>
          </div>
          <Link
            to="/pipeline"
            className="text-xs font-mono text-brand hover:underline inline-flex items-center gap-1 shrink-0"
          >
            <span>Inspect Pipeline Status</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Stage 1 */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-borderline text-brand">
                  STAGE 01
                </span>
                <Database className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-100 mb-1.5">
                Strict OHLCV &amp; ASPI Ingestion
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Historical records for 26 CSE stocks standardized into partitioned Parquet and Supabase PostgreSQL. Direct integration with official CSE API for live session &amp; ASPI feeds.
              </p>
            </div>
            <div className="mt-4 pt-2.5 border-t border-borderline/60 font-mono text-[10px] text-muted">
              CSE Official API &bull; Supabase &amp; Parquet
            </div>
          </div>

          {/* Stage 2 */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-borderline text-brand">
                  STAGE 02
                </span>
                <Sliders className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-100 mb-1.5">
                Vectorized Feature Engineering
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Backward-looking technical indicators: Parkinson extreme-value volatility, Wilder RSI-14, MACD signal &amp; histogram, volume momentum, and rolling ASPI relative strength.
              </p>
            </div>
            <div className="mt-4 pt-2.5 border-t border-borderline/60 font-mono text-[10px] text-muted">
              17 Stationary Features &bull; Shifted Windows
            </div>
          </div>

          {/* Stage 3 */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-borderline text-brand">
                  STAGE 03
                </span>
                <GitBranch className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-100 mb-1.5">
                Purged Walk-Forward CV
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Standard random K-Fold is strictly forbidden in finance due to temporal auto-correlation. We enforce an expanding window with a 30-day embargo gap between splits.
              </p>
            </div>
            <div className="mt-4 pt-2.5 border-t border-borderline/60 font-mono text-[10px] text-muted">
              30-day Embargo Gap &bull; 5 Expanding Folds
            </div>
          </div>

          {/* Stage 4 */}
          <div className="p-5 rounded-xl bg-subsurface border border-borderline flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-borderline text-brand">
                  STAGE 04
                </span>
                <Layers className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-100 mb-1.5">
                Dual-Layer Explainability
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Fuses Layer 1 exact TreeSHAP feature attributions with Layer 2 rule-based domain heuristics, translating machine learning weights into actionable investor indicator cards.
              </p>
            </div>
            <div className="mt-4 pt-2.5 border-t border-borderline/60 font-mono text-[10px] text-muted">
              TreeSHAP &bull; Rule-Based Heuristics
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
