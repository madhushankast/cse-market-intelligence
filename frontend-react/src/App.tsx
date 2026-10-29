import React, { useEffect, useState } from 'react';
import {
  fetchAvailableStocks,
  fetchPrediction,
  checkHealth,
  type StockQuote,
  type PredictionPayload,
  type HealthStatus,
} from './api';
import { ForecastChart } from './components/ForecastChart';
import { HeuristicCards } from './components/HeuristicCards';
import { ShapDrivers } from './components/ShapDrivers';
import {
  TrendingUp,
  TrendingDown,
  Layers,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  Calendar,
  AlertCircle,
  BarChart2,
} from 'lucide-react';

export const App: React.FC = () => {
  const [stocks, setStocks] = useState<StockQuote[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('JKH_N0000');
  const [prediction, setPrediction] = useState<PredictionPayload | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [activeTab, setActiveTab] = useState<'heuristics' | 'shap'>('heuristics');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial Load: Stocks & Health
  useEffect(() => {
    async function init() {
      try {
        const [stocksData, healthData] = await Promise.all([
          fetchAvailableStocks(),
          checkHealth().catch(() => null),
        ]);
        setStocks(stocksData);
        setHealth(healthData);

        if (stocksData.length > 0) {
          // Default to JKH_N0000 if available, else first
          const defaultSym =
            stocksData.find((s) => s.symbol.includes('JKH'))?.symbol || stocksData[0].symbol;
          setSelectedSymbol(defaultSym);
        }
      } catch (err: any) {
        console.error('Failed to initialize platform:', err);
        setError('Failed to connect to CSE Market Intelligence backend on http://localhost:8000.');
        setLoading(false);
      }
    }
    init();
  }, []);

  // 2. Fetch Prediction on selectedSymbol change
  useEffect(() => {
    if (!selectedSymbol) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    fetchPrediction(selectedSymbol, 30)
      .then((data) => {
        if (isMounted) {
          setPrediction(data);
          setLoading(false);
        }
      })
      .catch((err: any) => {
        if (isMounted) {
          console.error(`Prediction error for ${selectedSymbol}:`, err);
          setError(`Unable to generate multi-quantile forecast for ${selectedSymbol}. Please ensure backend models are loaded.`);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [selectedSymbol]);

  const currentStock = stocks.find((s) => s.symbol === selectedSymbol);
  const pctChange = prediction?.target_returns?.expected_pct_change ?? 0;
  const isBullish = pctChange > 0;

  return (
    <div className="min-h-screen bg-canvas text-gray-200 flex flex-col font-sans">
      {/* Top Institutional Navigation Bar */}
      <header className="border-b border-borderline bg-surface/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand to-sky-400 flex items-center justify-center font-bold text-canvas shadow-lg shadow-brand/20">
              <BarChart2 className="w-5 h-5 text-gray-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-gray-100">
                  CSE Market Intelligence
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-subsurface text-muted border border-borderline">
                  v2.0 MLOps
                </span>
              </div>
              <p className="text-[11px] text-muted hidden sm:block">
                Colombo Stock Exchange • Multi-Quantile LightGBM Terminal
              </p>
            </div>
          </div>

          {/* Center: Equity Selector */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="bg-subsurface border border-borderline text-gray-100 text-xs font-mono rounded-lg px-3 py-2 pr-8 focus:outline-none focus:border-brand transition-colors cursor-pointer appearance-none shadow-inner"
              >
                {stocks.map((s) => (
                  <option key={s.symbol} value={s.symbol} className="bg-subsurface text-gray-200">
                    {s.code} • {s.name} (LKR {s.latest_close.toFixed(2)})
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-muted">
                ▼
              </div>
            </div>

            <button
              onClick={() => {
                if (selectedSymbol) {
                  setLoading(true);
                  fetchPrediction(selectedSymbol, 30)
                    .then(setPrediction)
                    .finally(() => setLoading(false));
                }
              }}
              title="Refresh Forecast"
              className="p-2 rounded-lg bg-subsurface hover:bg-borderline/60 border border-borderline text-muted hover:text-gray-100 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-brand' : ''}`} />
            </button>
          </div>

          {/* Right: System Status Probe */}
          <div className="hidden lg:flex items-center gap-3 text-xs font-mono">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>{health ? 'API Connected' : 'Online'}</span>
            </div>
            <div className="text-muted text-[11px]">
              {stocks.length} Equities Active
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col gap-6">
        {/* Error Notice */}
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start gap-3 text-rose-300 text-xs font-mono">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="font-bold">System Notification:</span> {error}
            </div>
          </div>
        )}

        {/* Ticker Header & KPI Ribbon */}
        {prediction && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* 1. Asset Identity */}
            <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-mono tracking-wider text-muted">
                  Active Asset
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderline text-muted">
                  {currentStock?.sector || 'CSE'}
                </span>
              </div>
              <div className="mt-2">
                <h2 className="text-xl font-bold font-mono text-gray-100 tracking-tight">
                  {currentStock?.code || prediction.symbol.split('_')[0]}
                </h2>
                <p className="text-xs text-muted truncate">
                  {currentStock?.name || prediction.symbol}
                </p>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60">
                <Calendar className="w-3.5 h-3.5" />
                <span>As of {prediction.as_of_date}</span>
              </div>
            </div>

            {/* 2. Current Price */}
            <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
              <span className="text-xs uppercase font-mono tracking-wider text-muted">
                Spot Close Price
              </span>
              <div className="mt-2">
                <div className="text-2xl font-bold font-mono text-gray-100">
                  LKR {prediction.current_price.toFixed(2)}
                </div>
                <div className="text-[11px] font-mono text-muted mt-1">
                  Volume: {currentStock ? currentStock.latest_volume.toLocaleString() : '—'}
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 mt-2 pt-2 border-t border-borderline/60">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Verified Historical Anchor</span>
              </div>
            </div>

            {/* 3. Expected Median Target (P50) */}
            <div className="p-4 bg-surface border border-brand/40 rounded-xl flex flex-col justify-between shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-brand/5 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-mono tracking-wider text-brand font-semibold">
                  P50 Expected Target (30d)
                </span>
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                  isBullish ? 'bg-bullish/10 text-bullish border border-bullish/30' : 'bg-bearish/10 text-bearish border border-bearish/30'
                }`}>
                  {pctChange >= 0 ? '+' : ''}{pctChange.toFixed(2)}%
                </span>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold font-mono text-brand">
                  LKR {prediction.target_prices.price_p50.toFixed(2)}
                </div>
                <div className="text-[11px] font-mono text-muted mt-1">
                  Log Return: {(prediction.target_returns.p50_log_return * 100).toFixed(2)}%
                </div>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-gray-300 mt-2 pt-2 border-t border-borderline/60">
                {isBullish ? (
                  <TrendingUp className="w-3.5 h-3.5 text-bullish" />
                ) : (
                  <TrendingDown className="w-3.5 h-3.5 text-bearish" />
                )}
                <span className="font-semibold">{isBullish ? 'Bullish Drift' : 'Bearish Pullback'}</span>
              </div>
            </div>

            {/* 4. Bullish Ceiling (P90) */}
            <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
              <span className="text-xs uppercase font-mono tracking-wider text-bullish">
                P90 Upside Ceiling (90th %)
              </span>
              <div className="mt-2">
                <div className="text-2xl font-bold font-mono text-bullish">
                  LKR {prediction.target_prices.price_p90.toFixed(2)}
                </div>
                <div className="text-[11px] font-mono text-muted mt-1">
                  Log Return: +{(prediction.target_returns.p90_log_return * 100).toFixed(2)}%
                </div>
              </div>
              <div className="text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60">
                Upper Tail Resistance
              </div>
            </div>

            {/* 5. 90% VaR Floor (P10) */}
            <div className="p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
              <span className="text-xs uppercase font-mono tracking-wider text-bearish">
                P10 Downside Floor (10th %)
              </span>
              <div className="mt-2">
                <div className="text-2xl font-bold font-mono text-bearish">
                  LKR {prediction.target_prices.price_p10.toFixed(2)}
                </div>
                <div className="text-[11px] font-mono text-muted mt-1">
                  Log Return: {(prediction.target_returns.p10_log_return * 100).toFixed(2)}%
                </div>
              </div>
              <div className="text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60">
                90% Value-at-Risk Support
              </div>
            </div>
          </div>
        )}

        {/* Primary Viewport: TradingView Forecast Cone */}
        <section className="flex flex-col gap-2">
          {loading && !prediction ? (
            <div className="h-[480px] bg-surface border border-borderline rounded-xl flex flex-col items-center justify-center gap-3 text-muted font-mono text-xs">
              <RefreshCw className="w-8 h-8 animate-spin text-brand" />
              <span>Running LightGBM Multi-Quantile Inference for {selectedSymbol}...</span>
            </div>
          ) : prediction ? (
            <div className="h-[480px] w-full">
              <ForecastChart prediction={prediction} />
            </div>
          ) : null}
        </section>

        {/* Tab Navigation for Dual-Layer Explainability */}
        <section className="flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-borderline pb-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('heuristics')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-semibold transition-all ${
                  activeTab === 'heuristics'
                    ? 'bg-subsurface text-brand border border-borderline shadow-md'
                    : 'text-muted hover:text-gray-200 hover:bg-subsurface/40'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Layer 2: Domain Heuristics Alignment</span>
                {prediction?.indicator_heuristics && (
                  <span className="px-1.5 py-0.2 rounded bg-borderline text-[10px]">
                    {prediction.indicator_heuristics.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => setActiveTab('shap')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-mono font-semibold transition-all ${
                  activeTab === 'shap'
                    ? 'bg-subsurface text-brand border border-borderline shadow-md'
                    : 'text-muted hover:text-gray-200 hover:bg-subsurface/40'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                <span>Layer 1: TreeSHAP Mathematical Drivers</span>
              </button>
            </div>
          </div>

          {/* Tab Content Panes */}
          <div className="transition-all duration-200">
            {activeTab === 'heuristics' ? (
              <HeuristicCards
                heuristics={prediction?.indicator_heuristics}
                predictedReturn={prediction?.target_returns?.p50_log_return}
              />
            ) : (
              <ShapDrivers shapExplanation={prediction?.shap_explanation} />
            )}
          </div>
        </section>
      </main>

      {/* Terminal Footer */}
      <footer className="border-t border-borderline py-4 px-6 bg-surface/50 text-xs font-mono text-muted flex flex-col sm:flex-row items-center justify-between gap-3">
        <div>
          <span>CSE Market Intelligence Platform • Colombo Stock Exchange</span>
        </div>
        <div className="flex items-center gap-4 text-[11px]">
          <span>Purged Walk-Forward Cross-Validation (30d Embargo)</span>
          <span>•</span>
          <span>Dual-Layer Explainability</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
