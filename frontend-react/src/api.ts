import axios from 'axios';
import { FALLBACK_STOCKS, FALLBACK_JKH_PREDICTION, FALLBACK_BENCHMARKS } from './data/fallbackData';

export const LIVE_RENDER_API_URL = 'https://cse-market-intelligence.onrender.com';

const defaultBaseUrl = import.meta.env.PROD
  ? LIVE_RENDER_API_URL
  : 'http://localhost:8000';

export const API_BASE_URL = (import.meta.env.VITE_API_URL || defaultBaseUrl)
  .replace(/\/+$/, '')
  .replace('cse-market-intelligence-api.onrender.com', 'cse-market-intelligence.onrender.com');

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 35000, // Allow 35s for free tier cold starts (e.g. Render)
  headers: {
    'Content-Type': 'application/json',
  },
});

const remoteFallbackClient = axios.create({
  baseURL: LIVE_RENDER_API_URL,
  timeout: 35000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StockQuote {
  symbol: string;
  code: string;
  name: string;
  sector: string;
  latest_close: number;
  latest_date: string;
  latest_volume: number;
}

export interface ConePoint {
  step: number;
  date: string;
  price_p10: number;
  price_p50: number;
  price_p90: number;
}

export interface HistoricalBar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ShapDriver {
  feature: string;
  value: number;
  shap_impact: number;
  shap_impact_pct: number;
  description: string;
  direction: 'positive' | 'negative';
}

export interface ShapExplanation {
  base_value: number;
  predicted_return: number;
  top_positive_drivers: ShapDriver[];
  top_negative_drivers: ShapDriver[];
}

export interface HeuristicCard {
  indicator: string;
  value: string | number;
  status: 'Supporting' | 'Rejecting / Risk' | 'Neutral';
  signal: 'Bullish' | 'Bearish' | 'Neutral';
  explanation: string;
}

export interface TargetReturns {
  p10_log_return: number;
  p50_log_return: number;
  p90_log_return: number;
  expected_pct_change: number;
}

export interface TargetPrices {
  price_p10: number;
  price_p50: number;
  price_p90: number;
}

export interface PredictionPayload {
  symbol: string;
  current_price: number;
  as_of_date: string;
  horizon_days: number;
  target_returns: TargetReturns;
  target_prices: TargetPrices;
  cone_trajectory: ConePoint[];
  shap_explanation?: ShapExplanation;
  indicator_heuristics?: HeuristicCard[];
  historical_series?: HistoricalBar[];
  is_fallback?: boolean;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  uptime_seconds: number;
  models_count: number;
  available_equities_count: number;
  available_models: string[];
}

export interface BenchmarkRecord {
  symbol: string;
  n_folds: number;
  total_test_samples: number;
  lgb_dir_acc: number;
  naive_dir_acc: number;
  prophet_dir_acc: number;
  dir_acc_edge_vs_naive: number;
  lgb_rmse: number;
  naive_rmse: number;
  prophet_rmse: number;
  lgb_mae: number;
  naive_mae: number;
  prophet_mae: number;
  lgb_mean_pinball: number;
  lgb_pinball_p10: number;
  lgb_pinball_p50: number;
  lgb_pinball_p90: number;
  lgb_coverage_80: number;
}

export async function checkHealth(): Promise<HealthStatus> {
  try {
    const resp = await client.get('/health');
    return resp.data;
  } catch (err) {
    if (API_BASE_URL !== LIVE_RENDER_API_URL) {
      const resp = await remoteFallbackClient.get('/health');
      return resp.data;
    }
    throw err;
  }
}

export async function fetchAvailableStocks(): Promise<StockQuote[]> {
  try {
    const resp = await client.get('/api/v1/stocks');
    if (resp.data && Array.isArray(resp.data.data) && resp.data.data.length > 0) {
      return resp.data.data;
    }
    return FALLBACK_STOCKS;
  } catch (err) {
    if (API_BASE_URL !== LIVE_RENDER_API_URL) {
      try {
        const resp = await remoteFallbackClient.get('/api/v1/stocks');
        if (resp.data && Array.isArray(resp.data.data) && resp.data.data.length > 0) {
          return resp.data.data;
        }
      } catch {
        // Ignore and proceed to static fallback
      }
    }
    console.warn(`[CSE API] Unable to connect to backend at ${API_BASE_URL}. Falling back to cached equities list.`);
    return FALLBACK_STOCKS;
  }
}

export async function fetchBenchmarks(): Promise<BenchmarkRecord[]> {
  try {
    const resp = await client.get('/api/v1/benchmarks');
    if (resp.data && Array.isArray(resp.data.data) && resp.data.data.length > 0) {
      return resp.data.data;
    }
    return FALLBACK_BENCHMARKS;
  } catch (err) {
    if (API_BASE_URL !== LIVE_RENDER_API_URL) {
      try {
        const resp = await remoteFallbackClient.get('/api/v1/benchmarks');
        if (resp.data && Array.isArray(resp.data.data) && resp.data.data.length > 0) {
          return resp.data.data;
        }
      } catch {
        // Ignore and proceed to static fallback
      }
    }
    console.warn(`[CSE API] Unable to connect to backend at ${API_BASE_URL}. Falling back to cached benchmark report.`);
    return FALLBACK_BENCHMARKS;
  }
}

export async function fetchPrediction(
  symbol: string,
  horizonDays: number = 30
): Promise<PredictionPayload> {
  try {
    const resp = await client.post('/api/v1/predict', {
      symbol,
      horizon_days: horizonDays,
      explain: true,
    });
    return { ...resp.data.data, is_fallback: false };
  } catch (err) {
    try {
      // Fallback to GET endpoint
      const resp = await client.get(`/api/v1/predict/${encodeURIComponent(symbol)}`, {
        params: { horizon_days: horizonDays, explain: true },
      });
      return { ...resp.data.data, is_fallback: false };
    } catch (innerErr) {
      if (API_BASE_URL !== LIVE_RENDER_API_URL) {
        try {
          const resp = await remoteFallbackClient.post('/api/v1/predict', {
            symbol,
            horizon_days: horizonDays,
            explain: true,
          });
          return { ...resp.data.data, is_fallback: false };
        } catch {
          // Ignore and proceed to static fallback
        }
      }
      console.warn(`[CSE API] Live prediction failed for ${symbol} at ${API_BASE_URL}. Engaging fallback cache.`);
      
      const cleanSym = symbol.replace('.', '_');
      if (cleanSym.includes('JKH') || cleanSym === 'JKH_N0000') {
        return { ...FALLBACK_JKH_PREDICTION, is_fallback: true };
      }

      // If another asset is selected, scale the high-fidelity trajectory to this asset's price
      const meta = FALLBACK_STOCKS.find((s) => s.symbol === cleanSym || s.code === cleanSym);
      if (meta) {
        const p = meta.latest_close;
        const refP = FALLBACK_JKH_PREDICTION.current_price;
        const ratio = p / refP;

        return {
          ...FALLBACK_JKH_PREDICTION,
          symbol: cleanSym,
          current_price: p,
          target_prices: {
            price_p10: Math.round(p * 0.945 * 100) / 100,
            price_p50: Math.round(p * 1.019 * 100) / 100,
            price_p90: Math.round(p * 1.034 * 100) / 100,
          },
          cone_trajectory: FALLBACK_JKH_PREDICTION.cone_trajectory.map((pt) => ({
            ...pt,
            price_p10: Math.round(pt.price_p10 * ratio * 100) / 100,
            price_p50: Math.round(pt.price_p50 * ratio * 100) / 100,
            price_p90: Math.round(pt.price_p90 * ratio * 100) / 100,
          })),
          historical_series: FALLBACK_JKH_PREDICTION.historical_series?.map((b) => ({
            ...b,
            open: Math.round(b.open * ratio * 100) / 100,
            high: Math.round(b.high * ratio * 100) / 100,
            low: Math.round(b.low * ratio * 100) / 100,
            close: Math.round(b.close * ratio * 100) / 100,
          })),
          is_fallback: true,
        };
      }

      return { ...FALLBACK_JKH_PREDICTION, symbol: cleanSym, is_fallback: true };
    }
  }
}
