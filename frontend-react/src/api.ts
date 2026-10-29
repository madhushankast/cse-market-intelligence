import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
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

export async function checkHealth(): Promise<HealthStatus> {
  const resp = await client.get('/health');
  return resp.data;
}

export async function fetchAvailableStocks(): Promise<StockQuote[]> {
  const resp = await client.get('/api/v1/stocks');
  return resp.data.data;
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
    return resp.data.data;
  } catch (err) {
    // Fallback to GET endpoint if POST fails
    const resp = await client.get(`/api/v1/predict/${encodeURIComponent(symbol)}`, {
      params: { horizon_days: horizonDays, explain: true },
    });
    return resp.data.data;
  }
}
