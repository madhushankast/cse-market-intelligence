import React, { useEffect, useState } from 'react';
import {
  fetchAvailableStocks,
  fetchPrediction,
  API_BASE_URL,
  type StockQuote,
  type PredictionPayload,
} from '../api';
import { ForecastChart } from '../components/ForecastChart';
import { HeuristicCards } from '../components/HeuristicCards';
import { ShapDrivers } from '../components/ShapDrivers';
import {
  TrendingUp,
  TrendingDown,
  Layers,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  Calendar,
  AlertCircle,
} from 'lucide-react';

export const TerminalPage: React.FC = () => {
  const [stocks, setStocks] = useState<StockQuote[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('JKH_N0000');
  const [prediction, setPrediction] = useState<PredictionPayload | null>(null);
  const [activeTab, setActiveTab] = useState<'heuristics' | 'shap'>('heuristics');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Load initial stocks list
  useEffect(() => {
    fetchAvailableStocks()
      .then((stocksData) => {
        setStocks(stocksData);
        if (stocksData.length > 0) {
          const defaultSym =
            stocksData.find((s) => s.symbol.includes('JKH'))?.symbol || stocksData[0].symbol;
          setSelectedSymbol(defaultSym);
        }
      })
      .catch((err: any) => {
        console.error('Failed to load stocks:', err);
        setError(`Failed to fetch available stocks from the backend on ${API_BASE_URL}.`);
        setLoading(false);
      });
  }, []);

  // 2. Fetch prediction when selectedSymbol changes
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
          setError(
            `Unable to generate multi-quantile forecast for ${selectedSymbol}. Please ensure backend models are trained.`
          );
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
    <div className="flex-1 max-w-[1600px] w-full mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 flex flex-col gap-4 sm:gap-6">
      {/* Ticker Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 sm:p-4 bg-surface border border-borderline rounded-xl shadow-lg gap-3 sm:gap-4">
        <div className="flex items-end gap-2.5 w-full sm:w-auto min-w-0">
          <div className="flex flex-col flex-1 sm:flex-initial min-w-0">
            <span className="text-[10px] font-mono uppercase tracking-wider text-muted">
              Select CSE Equity
            </span>
            <div className="relative mt-1 w-full sm:w-auto">
              <select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full sm:w-auto max-w-full truncate bg-subsurface border border-borderline text-gray-100 text-xs sm:text-sm font-mono rounded-lg px-3 py-2 pr-8 focus:outline-none focus:border-brand transition-colors cursor-pointer appearance-none shadow-inner"
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
            className="shrink-0 p-2 rounded-lg bg-subsurface hover:bg-borderline/60 border border-borderline text-muted hover:text-gray-100 transition-colors mb-0.5"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-brand' : ''}`} />
          </button>
        </div>

        {/* Quick Sector and Date Summary */}
        <div className="flex items-center justify-between sm:justify-end gap-4 text-xs font-mono pt-2 sm:pt-0 border-t sm:border-t-0 border-borderline/60">
          <div className="flex flex-col sm:text-right">
            <span className="text-muted text-[10px] uppercase">Market Sector</span>
            <span className="text-gray-200 font-semibold">{currentStock?.sector || 'Equities'}</span>
          </div>

          <div className="flex flex-col text-right pl-4 border-l border-borderline">
            <span className="text-muted text-[10px] uppercase">Data Timestamp</span>
            <span className="text-gray-200 font-semibold">{prediction?.as_of_date || '—'}</span>
          </div>
        </div>
      </div>

      {/* Fallback / Cold Start Preview Mode Banner */}
      {prediction?.is_fallback && (
        <div className="p-3.5 bg-amber-500/10 border border-amber-500/25 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-amber-300">
          <div className="flex items-center gap-2.5">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping shrink-0" />
            <span>
              <strong>Preview Mode:</strong> Live backend is waking up or offline. Displaying cached LightGBM forecast.
            </span>
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
            className="w-full sm:w-auto text-center px-3 py-1.5 sm:py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/30 text-[11px] transition-colors"
          >
            Retry Live Connection
          </button>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start gap-3 text-rose-300 text-xs font-mono">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <div>
            <span className="font-bold">System Alert:</span> {error}
          </div>
        </div>
      )}

      {/* KPI Metrics Cards */}
      {prediction && (
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
          {/* 1. Asset Identity */}
          <div className="p-3.5 sm:p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-muted truncate">
                Active Asset
              </span>
              <span className="text-[9px] sm:text-[10px] font-mono px-1.5 sm:px-2 py-0.5 rounded bg-subsurface border border-borderline text-muted truncate max-w-[90px]">
                {currentStock?.sector || 'CSE'}
              </span>
            </div>
            <div className="mt-2">
              <h2 className="text-lg sm:text-xl font-bold font-mono text-gray-100 tracking-tight">
                {currentStock?.code || prediction.symbol.split('_')[0]}
              </h2>
              <p className="text-[11px] sm:text-xs text-muted truncate">
                {currentStock?.name || prediction.symbol}
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] sm:text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60">
              <Calendar className="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" />
              <span className="truncate">As of {prediction.as_of_date}</span>
            </div>
          </div>

          {/* 2. Current Price */}
          <div className="p-3.5 sm:p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
            <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-muted">
              Spot Close Price
            </span>
            <div className="mt-2">
              <div className="text-lg sm:text-2xl font-bold font-mono text-gray-100">
                LKR {prediction.current_price.toFixed(2)}
              </div>
              <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-1 truncate">
                Vol: {currentStock ? currentStock.latest_volume.toLocaleString() : '—'}
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] sm:text-[11px] font-mono text-emerald-400 mt-2 pt-2 border-t border-borderline/60">
              <ShieldCheck className="w-3 h-3 sm:w-3.5 sm:h-3.5 shrink-0" />
              <span className="truncate">Verified Anchor</span>
            </div>
          </div>

          {/* 3. Expected Median Target (P50) */}
          <div className="col-span-2 sm:col-span-2 lg:col-span-1 p-3.5 sm:p-4 bg-surface border border-brand/40 rounded-xl flex flex-col justify-between shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-brand/5 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between gap-2">
              <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-brand font-semibold">
                P50 Expected Target (30d)
              </span>
              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded shrink-0 ${
                  isBullish
                    ? 'bg-bullish/10 text-bullish border border-bullish/30'
                    : 'bg-bearish/10 text-bearish border border-bearish/30'
                }`}
              >
                {pctChange >= 0 ? '+' : ''}
                {pctChange.toFixed(2)}%
              </span>
            </div>
            <div className="mt-2">
              <div className="text-xl sm:text-2xl font-bold font-mono text-brand">
                LKR {prediction.target_prices.price_p50.toFixed(2)}
              </div>
              <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-1">
                Log Return: {(prediction.target_returns.p50_log_return * 100).toFixed(2)}%
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] sm:text-[11px] font-mono text-gray-300 mt-2 pt-2 border-t border-borderline/60">
              {isBullish ? (
                <TrendingUp className="w-3.5 h-3.5 text-bullish shrink-0" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-bearish shrink-0" />
              )}
              <span className="font-semibold">{isBullish ? 'Bullish Drift' : 'Bearish Pullback'}</span>
            </div>
          </div>

          {/* 4. Bullish Ceiling (P90) */}
          <div className="p-3.5 sm:p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
            <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-bullish">
              P90 Ceiling (90th %)
            </span>
            <div className="mt-2">
              <div className="text-lg sm:text-2xl font-bold font-mono text-bullish">
                LKR {prediction.target_prices.price_p90.toFixed(2)}
              </div>
              <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-1">
                Log Return: +{(prediction.target_returns.p90_log_return * 100).toFixed(2)}%
              </div>
            </div>
            <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60 truncate">
              Upper Tail Resistance
            </div>
          </div>

          {/* 5. 90% VaR Floor (P10) */}
          <div className="p-3.5 sm:p-4 bg-surface border border-borderline rounded-xl flex flex-col justify-between shadow-lg">
            <span className="text-[11px] sm:text-xs uppercase font-mono tracking-wider text-bearish">
              P10 Floor (10th %)
            </span>
            <div className="mt-2">
              <div className="text-lg sm:text-2xl font-bold font-mono text-bearish">
                LKR {prediction.target_prices.price_p10.toFixed(2)}
              </div>
              <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-1">
                Log Return: {(prediction.target_returns.p10_log_return * 100).toFixed(2)}%
              </div>
            </div>
            <div className="text-[10px] sm:text-[11px] font-mono text-muted mt-2 pt-2 border-t border-borderline/60 truncate">
              90% VaR Support
            </div>
          </div>
        </div>
      )}

      {/* Primary Chart Viewport */}
      <section className="flex flex-col gap-2">
        {loading && !prediction ? (
          <div className="h-[380px] sm:h-[480px] bg-surface border border-borderline rounded-xl flex flex-col items-center justify-center gap-3 text-muted font-mono text-xs shadow-xl px-4 text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-brand" />
            <span>Running LightGBM Multi-Quantile Inference for {selectedSymbol}...</span>
          </div>
        ) : prediction ? (
          <div className="h-[400px] sm:h-[480px] w-full">
            <ForecastChart prediction={prediction} />
          </div>
        ) : null}
      </section>

      {/* Dual-Layer Explainability Navigation & Panes */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-borderline pb-3">
          <div className="grid grid-cols-1 sm:flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => setActiveTab('heuristics')}
              className={`flex items-center justify-center sm:justify-start gap-2 px-3.5 sm:px-4 py-2.5 sm:py-2 rounded-lg text-xs font-mono font-semibold transition-all ${
                activeTab === 'heuristics'
                  ? 'bg-subsurface text-brand border border-borderline shadow-md'
                  : 'text-muted hover:text-gray-200 hover:bg-subsurface/40 border border-transparent'
              }`}
            >
              <Layers className="w-4 h-4 shrink-0" />
              <span className="truncate">Layer 2: Domain Heuristics Alignment</span>
              {prediction?.indicator_heuristics && (
                <span className="px-1.5 py-0.2 rounded bg-borderline text-[10px] shrink-0">
                  {prediction.indicator_heuristics.length}
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('shap')}
              className={`flex items-center justify-center sm:justify-start gap-2 px-3.5 sm:px-4 py-2.5 sm:py-2 rounded-lg text-xs font-mono font-semibold transition-all ${
                activeTab === 'shap'
                  ? 'bg-subsurface text-brand border border-borderline shadow-md'
                  : 'text-muted hover:text-gray-200 hover:bg-subsurface/40 border border-transparent'
              }`}
            >
              <Sparkles className="w-4 h-4 shrink-0" />
              <span className="truncate">Layer 1: TreeSHAP Mathematical Drivers</span>
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
    </div>
  );
};
