/**
 * forecastService.js
 * Thin API client for all forecasting-related endpoints.
 */
import api from "./api";

const forecastService = {
  /**
   * Fetch multi-model predictions for a symbol.
   * @param {string} symbol - Stock ticker, e.g. "COMB"
   * @param {number} horizon - Forecast horizon in trading days (default 7)
   */
  getPredictions: (symbol, horizon = 7) =>
    api.get(`/predictions/${symbol}?horizon=${horizon}`).then((r) => r.data),

  /**
   * Fetch side-by-side model comparison metrics.
   * @param {string} symbol - Stock ticker
   */
  getModelComparison: (symbol) =>
    api.get(`/predictions/${symbol}/compare`).then((r) => r.data),

  /**
   * Fetch last N historical close prices for the chart.
   * @param {string} symbol - Stock ticker
   * @param {number} n - Number of data points
   */
  getPriceHistory: (symbol, n = 60) =>
    api.get(`/predictions/${symbol}/history?n=${n}`).then((r) => r.data),
};

export default forecastService;
