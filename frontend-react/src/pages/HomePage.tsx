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
    <div className="flex flex-col gap-8 sm:gap-12 py-4 sm:py-6 max-w-[1400px] mx-auto px-3 sm:px-6 lg:px-8">
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden rounded-2xl border border-borderline bg-gradient-to-b from-surface via-surface to-canvas p-5 sm:p-8 lg:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-2.5 sm:px-3 py-1 rounded-full bg-brand/10 border border-brand/20 text-brand font-mono text-[10px] sm:text-xs mb-3 sm:mb-4">
            <Sparkles className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">INSTITUTIONAL QUANTITATIVE SERVING ENGINE</span>
          </div>

          <h1 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-gray-100 font-sans leading-tight">
            Colombo Stock Exchange (CSE) Quantitative Intelligence Platform
          </h1>

          <p className="mt-3 sm:mt-4 text-sm sm:text-lg text-gray-300 leading-relaxed font-sans">
            An end-to-end MLOps forecasting engine leveraging Multi-Quantile LightGBM, TreeSHAP
            mathematical attribution, and purged walk-forward cross-validation on frontier equity
            time series.
          </p>

          <div className="mt-6 sm:mt-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4">
            <Link
              to="/terminal"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-brand hover:bg-sky-400 text-gray-950 font-semibold text-sm transition-all shadow-lg shadow-brand/20 hover:scale-[1.02]"
            >
              <TrendingUp className="w-4 h-4" />
              <span>Launch Trading Terminal</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/benchmarks"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-subsurface hover:bg-borderline border border-borderline text-gray-200 font-semibold text-sm transition-all hover:scale-[1.02]"
            >
              <Award className="w-4 h-4 text-brand" />
              <span>View Model Benchmarks</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. The Financial ML Problem Statement */}
      <section className="flex flex-col gap-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
            METHODOLOGY & TARGET FORMULATION
          </span>
          <h2 className="text-2xl font-bold text-gray-100 mt-1">
            Why Predicting Raw Nominal Prices is an Anti-Pattern
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Random Walk Illusion */}
          <div className="p-6 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-xl">
            <div>
              <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mb-4">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-gray-100 mb-2">
                The Non-Stationary Price Trap
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Forecasting nominal levels creates an illusion of high R-squared while simply learning a delayed lag of yesterday's price. Financial prices are non-stationary random walks with unbounded variance.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-borderline font-mono text-[11px] text-rose-400">
              Anti-pattern: MSE on nominal prices
            </div>
          </div>

          {/* Card 2: Cumulative Log Return */}
          <div className="p-6 rounded-xl bg-surface border border-brand/40 flex flex-col justify-between shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-brand/5 rounded-full blur-xl pointer-events-none" />
            <div>
              <div className="w-10 h-10 rounded-lg bg-brand/10 border border-brand/20 text-brand flex items-center justify-center mb-4">
                <Sliders className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-gray-100 mb-2">
                Cumulative Forward Log Return Target
              </h3>
              <p className="text-xs text-gray-300 leading-relaxed font-sans">
                Our models predict the stationary 30-day forward cumulative log return:
              </p>
              <div className="my-3 p-3 bg-subsurface rounded-lg border border-borderline text-center font-mono text-sm text-brand font-bold">
                {"y_t = ln( P_{t+30} / P_t )"}
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
          <div className="p-6 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-xl">
            <div>
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-gray-100 mb-2">
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

      {/* 3. Architecture & Pipeline Blueprint */}
      <section className="flex flex-col gap-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
            SYSTEM BLUEPRINT
          </span>
          <h2 className="text-2xl font-bold text-gray-100 mt-1">
            End-to-End MLOps Pipeline Architecture
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Stage 1 */}
          <div className="p-5 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderline text-brand">
                  STAGE 01
                </span>
                <Database className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">
                Strict OHLCV & ASPI Ingestion
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Historical records for 26 CSE stocks standardized into partitioned Parquet. Direct integration with official CSE API for live ASPI benchmark feeds with zero lookahead bias.
              </p>
            </div>
            <div className="mt-4 pt-2 border-t border-borderline/60 font-mono text-[10px] text-muted">
              CSE Official API &bull; Parquet Storage
            </div>
          </div>

          {/* Stage 2 */}
          <div className="p-5 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderline text-brand">
                  STAGE 02
                </span>
                <Sliders className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">
                Vectorized Feature Engineering
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Backward-looking technical indicators: Parkinson extreme-value volatility, Wilder RSI-14, MACD signal & histogram, volume momentum, and rolling ASPI market-relative strength.
              </p>
            </div>
            <div className="mt-4 pt-2 border-t border-borderline/60 font-mono text-[10px] text-muted">
              17 Stationary Features &bull; Shifted Windows
            </div>
          </div>

          {/* Stage 3 */}
          <div className="p-5 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderline text-brand">
                  STAGE 03
                </span>
                <GitBranch className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">
                Purged Walk-Forward Cross-Validation
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Standard random K-Fold is strictly forbidden in finance due to temporal auto-correlation. We enforce an expanding window with a 30-day embargo gap between train and test splits.
              </p>
            </div>
            <div className="mt-4 pt-2 border-t border-borderline/60 font-mono text-[10px] text-muted">
              30-day Embargo Gap &bull; 5 Expanding Folds
            </div>
          </div>

          {/* Stage 4 */}
          <div className="p-5 rounded-xl bg-surface border border-borderline flex flex-col justify-between shadow-lg">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderline text-brand">
                  STAGE 04
                </span>
                <Layers className="w-4 h-4 text-muted" />
              </div>
              <h4 className="text-sm font-semibold text-gray-200 mb-1">
                Dual-Layer Explainability
              </h4>
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                Fuses Layer 1 exact TreeSHAP feature attributions with Layer 2 rule-based domain heuristics, translating machine learning weights into actionable investor indicator cards.
              </p>
            </div>
            <div className="mt-4 pt-2 border-t border-borderline/60 font-mono text-[10px] text-muted">
              TreeSHAP &bull; Rule-Based Heuristics
            </div>
          </div>
        </div>
      </section>

      {/* 4. How to Read the Terminal */}
      <section className="p-5 sm:p-8 rounded-2xl bg-surface border border-borderline shadow-xl flex flex-col gap-5 sm:gap-6">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-brand font-semibold">
            USER GUIDE
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-100 mt-1">
            How to Interpret the Trading Terminal
          </h2>
          <p className="text-xs text-muted mt-1 font-sans">
            The platform provides both quantitative forecast bounds and rule-based heuristic indicator statuses.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 rounded-xl bg-subsurface/60 border border-emerald-500/30 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-emerald-400 font-mono font-bold text-sm">
              <CheckCircle2 className="w-4 h-4" />
              <span>Supporting Signals (Green)</span>
            </div>
            <p className="text-xs text-gray-300 font-sans leading-relaxed">
              The technical indicator independently validates and agrees with the model's 30-day directional forecast (e.g. oversold RSI confirming a forecasted bounce, or a bullish moving average crossover).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-subsurface/60 border border-rose-500/30 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-rose-400 font-mono font-bold text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>Rejecting / Risk Warnings (Red)</span>
            </div>
            <p className="text-xs text-gray-300 font-sans leading-relaxed">
              The technical indicator warns of contrary pressure that may cap the trajectory (e.g. overbought divergence, extreme volatility, or broad benchmark index selling drag).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-subsurface/60 border border-slate-500/30 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-slate-300 font-mono font-bold text-sm">
              <MinusCircle className="w-4 h-4" />
              <span>Neutral / Indecision (Slate)</span>
            </div>
            <p className="text-xs text-gray-300 font-sans leading-relaxed">
              The metric sits in an equilibrium range without offering strong directional conviction (e.g. RSI between 45 and 55, or normal baseline trading volume).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
