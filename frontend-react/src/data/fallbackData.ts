// High-fidelity fallback & offline preview datasets
// Ensures the terminal functions seamlessly during cloud cold starts (e.g. Render free tier)
import type { StockQuote, PredictionPayload, BenchmarkRecord } from '../api';

export const FALLBACK_STOCKS: StockQuote[] = [
  {
    "symbol": "AAIC_N0000",
    "code": "AAIC",
    "name": "AAIC PLC",
    "sector": "Equities",
    "latest_close": 74.0,
    "latest_date": "2026-10-27",
    "latest_volume": 25451
  },
  {
    "symbol": "ACL_N0000",
    "code": "ACL",
    "name": "ACL Cables PLC",
    "sector": "Capital Goods",
    "latest_close": 87.4,
    "latest_date": "2026-10-27",
    "latest_volume": 125831
  },
  {
    "symbol": "AHUN_N0000",
    "code": "AHUN",
    "name": "AHUN PLC",
    "sector": "Equities",
    "latest_close": 78.0,
    "latest_date": "2026-10-27",
    "latest_volume": 61105
  },
  {
    "symbol": "CARG_N0000",
    "code": "CARG",
    "name": "Cargills (Ceylon) PLC",
    "sector": "Consumer Staples",
    "latest_close": 650.0,
    "latest_date": "2026-10-27",
    "latest_volume": 294
  },
  {
    "symbol": "COMB_N0000",
    "code": "COMB",
    "name": "Commercial Bank of Ceylon PLC",
    "sector": "Banking",
    "latest_close": 199.0,
    "latest_date": "2026-10-27",
    "latest_volume": 94533
  },
  {
    "symbol": "DIAL_N0000",
    "code": "DIAL",
    "name": "Dialog Axiata PLC",
    "sector": "Telecommunication",
    "latest_close": 43.5,
    "latest_date": "2026-10-27",
    "latest_volume": 20206560
  },
  {
    "symbol": "DIST_N0000",
    "code": "DIST",
    "name": "Distilleries Company of Sri Lanka PLC",
    "sector": "Consumer Goods",
    "latest_close": 52.0,
    "latest_date": "2026-10-27",
    "latest_volume": 227716
  },
  {
    "symbol": "EXPO_N0000",
    "code": "EXPO",
    "name": "Expolanka Holdings PLC",
    "sector": "Transportation & Logistics",
    "latest_close": 158.76,
    "latest_date": "2026-09-18",
    "latest_volume": 357566
  },
  {
    "symbol": "HAYL_N0000",
    "code": "HAYL",
    "name": "Hayleys PLC",
    "sector": "Diversified Holdings",
    "latest_close": 218.75,
    "latest_date": "2026-10-27",
    "latest_volume": 16987
  },
  {
    "symbol": "HEMA_N0000",
    "code": "HEMA",
    "name": "HEMA PLC",
    "sector": "Equities",
    "latest_close": 80.08,
    "latest_date": "2026-09-18",
    "latest_volume": 493956
  },
  {
    "symbol": "HNB_N0000",
    "code": "HNB",
    "name": "Hatton National Bank PLC",
    "sector": "Banking",
    "latest_close": 374.75,
    "latest_date": "2026-10-27",
    "latest_volume": 6842
  },
  {
    "symbol": "JKH_N0000",
    "code": "JKH",
    "name": "John Keells Holdings PLC",
    "sector": "Diversified Holdings",
    "latest_close": 17.8,
    "latest_date": "2026-10-27",
    "latest_volume": 1667616
  },
  {
    "symbol": "KGAL_N0000",
    "code": "KGAL",
    "name": "KGAL PLC",
    "sector": "Equities",
    "latest_close": 130.0,
    "latest_date": "2026-10-27",
    "latest_volume": 132
  },
  {
    "symbol": "LIOC_N0000",
    "code": "LIOC",
    "name": "Lanka IOC PLC",
    "sector": "Energy",
    "latest_close": 123.5,
    "latest_date": "2026-10-27",
    "latest_volume": 10545
  },
  {
    "symbol": "LOLC_N0000",
    "code": "LOLC",
    "name": "LOLC Holdings PLC",
    "sector": "Financials",
    "latest_close": 390.0,
    "latest_date": "2026-10-27",
    "latest_volume": 6127
  },
  {
    "symbol": "LWL_N0000",
    "code": "LWL",
    "name": "LWL PLC",
    "sector": "Equities",
    "latest_close": 39.7,
    "latest_date": "2026-10-27",
    "latest_volume": 2082
  },
  {
    "symbol": "MADU_N0000",
    "code": "MADU",
    "name": "MADU PLC",
    "sector": "Equities",
    "latest_close": 8.6,
    "latest_date": "2026-10-27",
    "latest_volume": 6115
  },
  {
    "symbol": "NDB_N0000",
    "code": "NDB",
    "name": "National Development Bank PLC",
    "sector": "Banking",
    "latest_close": 103.5,
    "latest_date": "2026-10-27",
    "latest_volume": 62422
  },
  {
    "symbol": "ODEL_N0000",
    "code": "ODEL",
    "name": "ODEL PLC",
    "sector": "Equities",
    "latest_close": 10.6,
    "latest_date": "2026-10-27",
    "latest_volume": 2750
  },
  {
    "symbol": "OSEA_N0000",
    "code": "OSEA",
    "name": "OSEA PLC",
    "sector": "Equities",
    "latest_close": 48.5,
    "latest_date": "2026-10-27",
    "latest_volume": 54044
  },
  {
    "symbol": "RICH_N0000",
    "code": "RICH",
    "name": "Richard Pieris and Company PLC",
    "sector": "Diversified Holdings",
    "latest_close": 26.1,
    "latest_date": "2026-10-27",
    "latest_volume": 1364
  },
  {
    "symbol": "SAMP_N0000",
    "code": "SAMP",
    "name": "Sampath Bank PLC",
    "sector": "Banking",
    "latest_close": 139.25,
    "latest_date": "2026-10-27",
    "latest_volume": 201582
  },
  {
    "symbol": "SEYB_N0000",
    "code": "SEYB",
    "name": "Seylan Bank PLC",
    "sector": "Banking",
    "latest_close": 90.3,
    "latest_date": "2026-10-27",
    "latest_volume": 3506
  },
  {
    "symbol": "SLTL_N0000",
    "code": "SLTL",
    "name": "Sri Lanka Telecom PLC",
    "sector": "Telecommunication",
    "latest_close": 79.9,
    "latest_date": "2026-10-27",
    "latest_volume": 29311
  },
  {
    "symbol": "TKYO_N0000",
    "code": "TKYO",
    "name": "Tokyo Cement Company (Lanka) PLC",
    "sector": "Materials",
    "latest_close": 75.0,
    "latest_date": "2026-10-27",
    "latest_volume": 288891
  },
  {
    "symbol": "UML_N0000",
    "code": "UML",
    "name": "UML PLC",
    "sector": "Equities",
    "latest_close": 21.9,
    "latest_date": "2026-10-27",
    "latest_volume": 119622
  }
];

export const FALLBACK_JKH_PREDICTION: PredictionPayload = {
  "current_price": 17.8,
  "as_of_date": "2026-10-27",
  "horizon_days": 30,
  "target_returns": {
    "p10_log_return": -0.0537,
    "p50_log_return": 0.0188,
    "p90_log_return": 0.0334,
    "expected_pct_change": 1.9
  },
  "target_prices": {
    "price_p10": 16.87,
    "price_p50": 18.14,
    "price_p90": 18.4
  },
  "cone_trajectory": [
    {
      "step": 1,
      "date": "2026-10-28",
      "price_p10": 17.77,
      "price_p50": 17.81,
      "price_p90": 17.82
    },
    {
      "step": 2,
      "date": "2026-10-29",
      "price_p10": 17.74,
      "price_p50": 17.82,
      "price_p90": 17.84
    },
    {
      "step": 3,
      "date": "2026-10-30",
      "price_p10": 17.7,
      "price_p50": 17.83,
      "price_p90": 17.86
    },
    {
      "step": 4,
      "date": "2026-11-02",
      "price_p10": 17.67,
      "price_p50": 17.84,
      "price_p90": 17.88
    },
    {
      "step": 5,
      "date": "2026-11-03",
      "price_p10": 17.64,
      "price_p50": 17.86,
      "price_p90": 17.9
    },
    {
      "step": 6,
      "date": "2026-11-04",
      "price_p10": 17.61,
      "price_p50": 17.87,
      "price_p90": 17.92
    },
    {
      "step": 7,
      "date": "2026-11-05",
      "price_p10": 17.58,
      "price_p50": 17.88,
      "price_p90": 17.94
    },
    {
      "step": 8,
      "date": "2026-11-06",
      "price_p10": 17.55,
      "price_p50": 17.89,
      "price_p90": 17.96
    },
    {
      "step": 9,
      "date": "2026-11-09",
      "price_p10": 17.52,
      "price_p50": 17.9,
      "price_p90": 17.98
    },
    {
      "step": 10,
      "date": "2026-11-10",
      "price_p10": 17.48,
      "price_p50": 17.91,
      "price_p90": 18.0
    },
    {
      "step": 11,
      "date": "2026-11-11",
      "price_p10": 17.45,
      "price_p50": 17.92,
      "price_p90": 18.02
    },
    {
      "step": 12,
      "date": "2026-11-12",
      "price_p10": 17.42,
      "price_p50": 17.93,
      "price_p90": 18.04
    },
    {
      "step": 13,
      "date": "2026-11-13",
      "price_p10": 17.39,
      "price_p50": 17.95,
      "price_p90": 18.06
    },
    {
      "step": 14,
      "date": "2026-11-16",
      "price_p10": 17.36,
      "price_p50": 17.96,
      "price_p90": 18.08
    },
    {
      "step": 15,
      "date": "2026-11-17",
      "price_p10": 17.33,
      "price_p50": 17.97,
      "price_p90": 18.1
    },
    {
      "step": 16,
      "date": "2026-11-18",
      "price_p10": 17.3,
      "price_p50": 17.98,
      "price_p90": 18.12
    },
    {
      "step": 17,
      "date": "2026-11-19",
      "price_p10": 17.27,
      "price_p50": 17.99,
      "price_p90": 18.14
    },
    {
      "step": 18,
      "date": "2026-11-20",
      "price_p10": 17.24,
      "price_p50": 18.0,
      "price_p90": 18.16
    },
    {
      "step": 19,
      "date": "2026-11-23",
      "price_p10": 17.2,
      "price_p50": 18.01,
      "price_p90": 18.18
    },
    {
      "step": 20,
      "date": "2026-11-24",
      "price_p10": 17.17,
      "price_p50": 18.02,
      "price_p90": 18.2
    },
    {
      "step": 21,
      "date": "2026-11-25",
      "price_p10": 17.14,
      "price_p50": 18.04,
      "price_p90": 18.22
    },
    {
      "step": 22,
      "date": "2026-11-26",
      "price_p10": 17.11,
      "price_p50": 18.05,
      "price_p90": 18.24
    },
    {
      "step": 23,
      "date": "2026-11-27",
      "price_p10": 17.08,
      "price_p50": 18.06,
      "price_p90": 18.26
    },
    {
      "step": 24,
      "date": "2026-11-30",
      "price_p10": 17.05,
      "price_p50": 18.07,
      "price_p90": 18.28
    },
    {
      "step": 25,
      "date": "2026-12-01",
      "price_p10": 17.02,
      "price_p50": 18.08,
      "price_p90": 18.3
    },
    {
      "step": 26,
      "date": "2026-12-02",
      "price_p10": 16.99,
      "price_p50": 18.09,
      "price_p90": 18.32
    },
    {
      "step": 27,
      "date": "2026-12-03",
      "price_p10": 16.96,
      "price_p50": 18.1,
      "price_p90": 18.34
    },
    {
      "step": 28,
      "date": "2026-12-04",
      "price_p10": 16.93,
      "price_p50": 18.12,
      "price_p90": 18.36
    },
    {
      "step": 29,
      "date": "2026-12-07",
      "price_p10": 16.9,
      "price_p50": 18.13,
      "price_p90": 18.38
    },
    {
      "step": 30,
      "date": "2026-12-08",
      "price_p10": 16.87,
      "price_p50": 18.14,
      "price_p90": 18.4
    }
  ],
  "symbol": "JKH_N0000",
  "shap_explanation": {
    "base_value": -0.0356,
    "predicted_return": 0.0188,
    "top_positive_drivers": [
      {
        "feature": "sma_ratio_20_50",
        "value": 0.9509,
        "shap_impact": 0.01834,
        "shap_impact_pct": 1.83,
        "description": "Medium-term moving average trend (SMA 20/50)",
        "direction": "positive"
      },
      {
        "feature": "parkinson_vol_20d",
        "value": 0.15,
        "shap_impact": 0.01496,
        "shap_impact_pct": 1.5,
        "description": "20-day high-low price variance",
        "direction": "positive"
      },
      {
        "feature": "macd_hist",
        "value": 0.0283,
        "shap_impact": 0.00872,
        "shap_impact_pct": 0.87,
        "description": "MACD histogram acceleration",
        "direction": "positive"
      },
      {
        "feature": "macd_signal",
        "value": -0.4083,
        "shap_impact": 0.00737,
        "shap_impact_pct": 0.74,
        "description": "MACD 9-day signal trigger line",
        "direction": "positive"
      },
      {
        "feature": "macd",
        "value": -0.38,
        "shap_impact": 0.00708,
        "shap_impact_pct": 0.71,
        "description": "MACD momentum oscillator line",
        "direction": "positive"
      }
    ],
    "top_negative_drivers": [
      {
        "feature": "rolling_corr_aspi_30d",
        "value": -0.0136,
        "shap_impact": -0.01025,
        "shap_impact_pct": -1.02,
        "description": "30-day rolling correlation with ASPI (Beta proxy)",
        "direction": "negative"
      },
      {
        "feature": "aspi_return_10d",
        "value": -0.0149,
        "shap_impact": -0.00345,
        "shap_impact_pct": -0.35,
        "description": "10-day ASPI CSE benchmark return",
        "direction": "negative"
      },
      {
        "feature": "relative_strength_30d",
        "value": -0.0799,
        "shap_impact": -0.00314,
        "shap_impact_pct": -0.31,
        "description": "30-day stock outperformance vs. ASPI index",
        "direction": "negative"
      },
      {
        "feature": "return_5d",
        "value": 0.0113,
        "shap_impact": -0.00062,
        "shap_impact_pct": -0.06,
        "description": "Short-term 5-day momentum",
        "direction": "negative"
      },
      {
        "feature": "volume_surge_ratio",
        "value": 0.4173,
        "shap_impact": -0.00039,
        "shap_impact_pct": -0.04,
        "description": "Trading volume expansion relative to 20d average",
        "direction": "negative"
      }
    ]
  },
  "indicator_heuristics": [
    {
      "indicator": "RSI (14)",
      "value": 34.0,
      "status": "Supporting",
      "signal": "Bullish",
      "explanation": "RSI is in an oversold rebound zone (34.0 < 35), offering strong value-recovery upside potential."
    },
    {
      "indicator": "SMA 20/50 Trend",
      "value": 0.951,
      "status": "Rejecting / Risk",
      "signal": "Bearish",
      "explanation": "20-day SMA is 4.9% below 50-day SMA, indicating downtrend resistance that could cap the forecast upside."
    },
    {
      "indicator": "Parkinson Volatility (20d)",
      "value": "15.0%",
      "status": "Supporting",
      "signal": "Bullish",
      "explanation": "20-day Parkinson volatility is controlled (15.0%), fostering orderly price discovery along the projected path."
    },
    {
      "indicator": "ASPI 30d Benchmark",
      "value": "-1.1%",
      "status": "Neutral",
      "signal": "Neutral",
      "explanation": "CSE ASPI index is down 1.1% over 30 days; positive stock forecast represents a contrarian decoupling from market headwinds."
    },
    {
      "indicator": "MACD Histogram",
      "value": 0.028,
      "status": "Supporting",
      "signal": "Bullish",
      "explanation": "MACD histogram is positive (+0.03), indicating active bullish momentum expansion."
    },
    {
      "indicator": "Volume Surge Ratio",
      "value": 0.42,
      "status": "Neutral",
      "signal": "Neutral",
      "explanation": "Volume is light (0.4x 20d average), reflecting quiet trading and low immediate turnover conviction."
    }
  ],
  "historical_series": [
    {
      "date": "2026-06-10",
      "open": 19.7,
      "high": 19.9,
      "low": 19.7,
      "close": 19.8,
      "volume": 16496004
    },
    {
      "date": "2026-06-11",
      "open": 19.8,
      "high": 19.8,
      "low": 19.6,
      "close": 19.7,
      "volume": 14884685
    },
    {
      "date": "2026-06-12",
      "open": 19.7,
      "high": 20.0,
      "low": 19.7,
      "close": 20.0,
      "volume": 3163380
    },
    {
      "date": "2026-06-15",
      "open": 20.0,
      "high": 20.7,
      "low": 20.0,
      "close": 20.5,
      "volume": 5624133
    },
    {
      "date": "2026-06-16",
      "open": 20.5,
      "high": 20.6,
      "low": 20.4,
      "close": 20.5,
      "volume": 7660678
    },
    {
      "date": "2026-06-17",
      "open": 20.5,
      "high": 20.6,
      "low": 20.3,
      "close": 20.4,
      "volume": 1910670
    },
    {
      "date": "2026-06-18",
      "open": 20.4,
      "high": 20.5,
      "low": 20.3,
      "close": 20.4,
      "volume": 1790522
    },
    {
      "date": "2026-06-19",
      "open": 20.4,
      "high": 20.5,
      "low": 20.3,
      "close": 20.4,
      "volume": 3053730
    },
    {
      "date": "2026-06-22",
      "open": 20.4,
      "high": 20.5,
      "low": 20.2,
      "close": 20.2,
      "volume": 1204598
    },
    {
      "date": "2026-06-23",
      "open": 20.2,
      "high": 20.3,
      "low": 20.0,
      "close": 20.2,
      "volume": 2952961
    },
    {
      "date": "2026-06-24",
      "open": 20.2,
      "high": 20.3,
      "low": 20.0,
      "close": 20.2,
      "volume": 718232
    },
    {
      "date": "2026-06-25",
      "open": 20.2,
      "high": 20.6,
      "low": 20.2,
      "close": 20.5,
      "volume": 3081621
    },
    {
      "date": "2026-06-26",
      "open": 20.5,
      "high": 20.5,
      "low": 20.3,
      "close": 20.4,
      "volume": 1809426
    },
    {
      "date": "2026-06-30",
      "open": 20.4,
      "high": 20.5,
      "low": 20.1,
      "close": 20.2,
      "volume": 2113732
    },
    {
      "date": "2026-07-01",
      "open": 20.2,
      "high": 20.4,
      "low": 20.2,
      "close": 20.3,
      "volume": 747346
    },
    {
      "date": "2026-07-02",
      "open": 20.3,
      "high": 20.4,
      "low": 20.2,
      "close": 20.3,
      "volume": 2258944
    },
    {
      "date": "2026-07-03",
      "open": 20.3,
      "high": 20.4,
      "low": 20.2,
      "close": 20.2,
      "volume": 1680208
    },
    {
      "date": "2026-07-06",
      "open": 20.2,
      "high": 20.3,
      "low": 20.0,
      "close": 20.1,
      "volume": 2172802
    },
    {
      "date": "2026-07-07",
      "open": 20.1,
      "high": 20.1,
      "low": 20.0,
      "close": 20.0,
      "volume": 15334161
    },
    {
      "date": "2026-07-08",
      "open": 20.0,
      "high": 20.1,
      "low": 19.9,
      "close": 20.0,
      "volume": 22217095
    },
    {
      "date": "2026-07-09",
      "open": 20.0,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 5477632
    },
    {
      "date": "2026-07-10",
      "open": 19.9,
      "high": 20.2,
      "low": 19.9,
      "close": 20.0,
      "volume": 6052893
    },
    {
      "date": "2026-07-13",
      "open": 20.0,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 1089506
    },
    {
      "date": "2026-07-14",
      "open": 19.9,
      "high": 20.0,
      "low": 19.8,
      "close": 19.8,
      "volume": 947538
    },
    {
      "date": "2026-07-15",
      "open": 19.8,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 3858312
    },
    {
      "date": "2026-07-16",
      "open": 19.9,
      "high": 20.2,
      "low": 19.9,
      "close": 20.0,
      "volume": 3319037
    },
    {
      "date": "2026-07-17",
      "open": 20.0,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 1631636
    },
    {
      "date": "2026-07-20",
      "open": 19.9,
      "high": 20.0,
      "low": 19.7,
      "close": 19.7,
      "volume": 5524178
    },
    {
      "date": "2026-07-21",
      "open": 19.7,
      "high": 19.9,
      "low": 19.7,
      "close": 19.8,
      "volume": 489792
    },
    {
      "date": "2026-07-22",
      "open": 19.8,
      "high": 19.8,
      "low": 19.6,
      "close": 19.6,
      "volume": 2513517
    },
    {
      "date": "2026-07-23",
      "open": 19.6,
      "high": 19.8,
      "low": 19.6,
      "close": 19.6,
      "volume": 12786719
    },
    {
      "date": "2026-07-24",
      "open": 19.6,
      "high": 19.8,
      "low": 19.6,
      "close": 19.6,
      "volume": 2708744
    },
    {
      "date": "2026-07-27",
      "open": 19.6,
      "high": 19.9,
      "low": 19.6,
      "close": 19.8,
      "volume": 33444192
    },
    {
      "date": "2026-07-28",
      "open": 19.8,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 1591248
    },
    {
      "date": "2026-07-30",
      "open": 19.9,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 3511696
    },
    {
      "date": "2026-07-31",
      "open": 19.9,
      "high": 20.0,
      "low": 19.9,
      "close": 19.9,
      "volume": 1446809
    },
    {
      "date": "2026-08-03",
      "open": 19.9,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 5868112
    },
    {
      "date": "2026-08-04",
      "open": 19.9,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 17822175
    },
    {
      "date": "2026-08-05",
      "open": 19.9,
      "high": 20.1,
      "low": 19.9,
      "close": 20.0,
      "volume": 6547250
    },
    {
      "date": "2026-08-06",
      "open": 20.0,
      "high": 20.1,
      "low": 19.9,
      "close": 20.0,
      "volume": 5942393
    },
    {
      "date": "2026-08-07",
      "open": 20.0,
      "high": 20.2,
      "low": 20.0,
      "close": 20.1,
      "volume": 2508160
    },
    {
      "date": "2026-08-10",
      "open": 20.1,
      "high": 20.2,
      "low": 19.9,
      "close": 20.0,
      "volume": 19954825
    },
    {
      "date": "2026-08-11",
      "open": 20.0,
      "high": 20.0,
      "low": 19.9,
      "close": 19.9,
      "volume": 3230164
    },
    {
      "date": "2026-08-12",
      "open": 19.9,
      "high": 20.0,
      "low": 19.9,
      "close": 20.0,
      "volume": 6427272
    },
    {
      "date": "2026-08-13",
      "open": 20.0,
      "high": 20.0,
      "low": 19.9,
      "close": 20.0,
      "volume": 6862353
    },
    {
      "date": "2026-08-14",
      "open": 20.0,
      "high": 20.1,
      "low": 19.9,
      "close": 20.0,
      "volume": 1577810
    },
    {
      "date": "2026-08-17",
      "open": 20.0,
      "high": 20.1,
      "low": 19.9,
      "close": 20.0,
      "volume": 3380209
    },
    {
      "date": "2026-08-18",
      "open": 20.0,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 35136186
    },
    {
      "date": "2026-08-19",
      "open": 19.9,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 609802
    },
    {
      "date": "2026-08-20",
      "open": 19.9,
      "high": 19.9,
      "low": 19.8,
      "close": 19.8,
      "volume": 4731661
    },
    {
      "date": "2026-08-21",
      "open": 19.8,
      "high": 19.9,
      "low": 19.8,
      "close": 19.8,
      "volume": 4668121
    },
    {
      "date": "2026-08-24",
      "open": 19.8,
      "high": 20.0,
      "low": 19.8,
      "close": 19.9,
      "volume": 7433443
    },
    {
      "date": "2026-08-25",
      "open": 19.9,
      "high": 19.9,
      "low": 19.8,
      "close": 19.8,
      "volume": 1865306
    },
    {
      "date": "2026-08-28",
      "open": 19.8,
      "high": 19.9,
      "low": 19.7,
      "close": 19.8,
      "volume": 2700918
    },
    {
      "date": "2026-08-31",
      "open": 19.8,
      "high": 19.9,
      "low": 19.8,
      "close": 19.9,
      "volume": 895194
    },
    {
      "date": "2026-09-01",
      "open": 19.9,
      "high": 19.9,
      "low": 19.5,
      "close": 19.5,
      "volume": 28674519
    },
    {
      "date": "2026-09-02",
      "open": 19.5,
      "high": 19.7,
      "low": 19.5,
      "close": 19.5,
      "volume": 1321052
    },
    {
      "date": "2026-09-03",
      "open": 19.5,
      "high": 19.7,
      "low": 19.4,
      "close": 19.5,
      "volume": 5245296
    },
    {
      "date": "2026-09-04",
      "open": 19.5,
      "high": 19.7,
      "low": 19.5,
      "close": 19.6,
      "volume": 964580
    },
    {
      "date": "2026-09-07",
      "open": 19.6,
      "high": 19.6,
      "low": 19.5,
      "close": 19.5,
      "volume": 2722158
    },
    {
      "date": "2026-09-08",
      "open": 19.5,
      "high": 19.6,
      "low": 19.5,
      "close": 19.5,
      "volume": 4495509
    },
    {
      "date": "2026-09-09",
      "open": 19.5,
      "high": 19.6,
      "low": 19.4,
      "close": 19.5,
      "volume": 2443326
    },
    {
      "date": "2026-09-10",
      "open": 19.5,
      "high": 19.5,
      "low": 19.4,
      "close": 19.4,
      "volume": 2224354
    },
    {
      "date": "2026-09-11",
      "open": 19.4,
      "high": 19.5,
      "low": 19.3,
      "close": 19.3,
      "volume": 10542731
    },
    {
      "date": "2026-09-14",
      "open": 19.3,
      "high": 19.4,
      "low": 19.3,
      "close": 19.3,
      "volume": 13190225
    },
    {
      "date": "2026-09-15",
      "open": 19.3,
      "high": 19.4,
      "low": 19.2,
      "close": 19.3,
      "volume": 10542395
    },
    {
      "date": "2026-09-16",
      "open": 19.3,
      "high": 19.3,
      "low": 19.1,
      "close": 19.1,
      "volume": 9198867
    },
    {
      "date": "2026-09-17",
      "open": 19.1,
      "high": 19.2,
      "low": 19.0,
      "close": 19.2,
      "volume": 4944066
    },
    {
      "date": "2026-09-18",
      "open": 19.2,
      "high": 19.2,
      "low": 19.0,
      "close": 19.1,
      "volume": 1361318
    },
    {
      "date": "2026-09-29",
      "open": 18.7,
      "high": 18.9,
      "low": 18.7,
      "close": 18.7,
      "volume": 6039992
    },
    {
      "date": "2026-09-30",
      "open": 18.7,
      "high": 18.9,
      "low": 18.6,
      "close": 18.7,
      "volume": 7239407
    },
    {
      "date": "2026-10-01",
      "open": 18.7,
      "high": 18.7,
      "low": 18.5,
      "close": 18.6,
      "volume": 1227973
    },
    {
      "date": "2026-10-04",
      "open": 18.6,
      "high": 18.6,
      "low": 18.4,
      "close": 18.4,
      "volume": 8535005
    },
    {
      "date": "2026-10-05",
      "open": 18.4,
      "high": 18.6,
      "low": 18.4,
      "close": 18.5,
      "volume": 1824103
    },
    {
      "date": "2026-10-06",
      "open": 18.5,
      "high": 18.6,
      "low": 18.3,
      "close": 18.4,
      "volume": 6358650
    },
    {
      "date": "2026-10-07",
      "open": 18.4,
      "high": 18.4,
      "low": 18.2,
      "close": 18.3,
      "volume": 1195027
    },
    {
      "date": "2026-10-08",
      "open": 18.3,
      "high": 18.4,
      "low": 18.2,
      "close": 18.4,
      "volume": 4226660
    },
    {
      "date": "2026-10-11",
      "open": 18.4,
      "high": 19.0,
      "low": 18.4,
      "close": 18.5,
      "volume": 1084602
    },
    {
      "date": "2026-10-12",
      "open": 18.5,
      "high": 18.5,
      "low": 18.1,
      "close": 18.1,
      "volume": 4468228
    },
    {
      "date": "2026-10-13",
      "open": 18.1,
      "high": 18.2,
      "low": 17.9,
      "close": 17.9,
      "volume": 11486819
    },
    {
      "date": "2026-10-14",
      "open": 17.9,
      "high": 18.0,
      "low": 17.8,
      "close": 17.9,
      "volume": 4270542
    },
    {
      "date": "2026-10-15",
      "open": 17.9,
      "high": 18.1,
      "low": 17.9,
      "close": 18.0,
      "volume": 1186254
    },
    {
      "date": "2026-10-18",
      "open": 18.0,
      "high": 18.1,
      "low": 17.6,
      "close": 17.7,
      "volume": 6308277
    },
    {
      "date": "2026-10-19",
      "open": 17.7,
      "high": 17.8,
      "low": 17.6,
      "close": 17.8,
      "volume": 738740
    },
    {
      "date": "2026-10-20",
      "open": 17.8,
      "high": 17.9,
      "low": 17.5,
      "close": 17.6,
      "volume": 3077563
    },
    {
      "date": "2026-10-21",
      "open": 17.6,
      "high": 17.8,
      "low": 17.5,
      "close": 17.6,
      "volume": 8938336
    },
    {
      "date": "2026-10-22",
      "open": 17.6,
      "high": 17.8,
      "low": 17.5,
      "close": 17.6,
      "volume": 1806338
    },
    {
      "date": "2026-10-25",
      "open": 17.6,
      "high": 17.8,
      "low": 17.5,
      "close": 17.7,
      "volume": 1430205
    },
    {
      "date": "2026-10-26",
      "open": 17.7,
      "high": 17.9,
      "low": 17.7,
      "close": 17.9,
      "volume": 2846762
    },
    {
      "date": "2026-10-27",
      "open": 17.9,
      "high": 17.9,
      "low": 17.7,
      "close": 17.8,
      "volume": 1667616
    }
  ]
};

export const FALLBACK_BENCHMARKS: BenchmarkRecord[] = [
  {
    "symbol": "AAIC_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 60.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 36.33,
    "dir_acc_edge_vs_naive": 10.33,
    "lgb_rmse": 0.0944,
    "naive_rmse": 0.0975,
    "prophet_rmse": 0.125,
    "lgb_mae": 0.0757,
    "naive_mae": 0.0811,
    "prophet_mae": 0.0999,
    "lgb_mean_pinball": 0.02676,
    "lgb_pinball_p10": 0.0118,
    "lgb_pinball_p50": 0.03783,
    "lgb_pinball_p90": 0.03065,
    "lgb_coverage_80": 88.0
  },
  {
    "symbol": "ACL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 68.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 73.0,
    "dir_acc_edge_vs_naive": 18.33,
    "lgb_rmse": 0.1101,
    "naive_rmse": 0.1149,
    "prophet_rmse": 0.111,
    "lgb_mae": 0.0815,
    "naive_mae": 0.0885,
    "prophet_mae": 0.0845,
    "lgb_mean_pinball": 0.02592,
    "lgb_pinball_p10": 0.0185,
    "lgb_pinball_p50": 0.04077,
    "lgb_pinball_p90": 0.0185,
    "lgb_coverage_80": 87.0
  },
  {
    "symbol": "AHUN_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 37.0,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 40.0,
    "dir_acc_edge_vs_naive": -13.0,
    "lgb_rmse": 0.1561,
    "naive_rmse": 0.1415,
    "prophet_rmse": 0.1612,
    "lgb_mae": 0.1238,
    "naive_mae": 0.107,
    "prophet_mae": 0.1362,
    "lgb_mean_pinball": 0.03674,
    "lgb_pinball_p10": 0.02005,
    "lgb_pinball_p50": 0.06188,
    "lgb_pinball_p90": 0.02829,
    "lgb_coverage_80": 71.33
  },
  {
    "symbol": "CARG_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 50.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 50.33,
    "dir_acc_edge_vs_naive": 0.33,
    "lgb_rmse": 0.0919,
    "naive_rmse": 0.0882,
    "prophet_rmse": 0.0904,
    "lgb_mae": 0.0692,
    "naive_mae": 0.0597,
    "prophet_mae": 0.0705,
    "lgb_mean_pinball": 0.01989,
    "lgb_pinball_p10": 0.00755,
    "lgb_pinball_p50": 0.03459,
    "lgb_pinball_p90": 0.01752,
    "lgb_coverage_80": 83.0
  },
  {
    "symbol": "COMB_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 64.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 50.0,
    "dir_acc_edge_vs_naive": 14.67,
    "lgb_rmse": 0.1208,
    "naive_rmse": 0.1192,
    "prophet_rmse": 0.1213,
    "lgb_mae": 0.0983,
    "naive_mae": 0.0976,
    "prophet_mae": 0.1037,
    "lgb_mean_pinball": 0.02784,
    "lgb_pinball_p10": 0.01695,
    "lgb_pinball_p50": 0.04914,
    "lgb_pinball_p90": 0.01743,
    "lgb_coverage_80": 87.67
  },
  {
    "symbol": "DIAL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 64.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 75.67,
    "dir_acc_edge_vs_naive": 14.67,
    "lgb_rmse": 0.1427,
    "naive_rmse": 0.1535,
    "prophet_rmse": 0.1459,
    "lgb_mae": 0.1221,
    "naive_mae": 0.1323,
    "prophet_mae": 0.1228,
    "lgb_mean_pinball": 0.03317,
    "lgb_pinball_p10": 0.01718,
    "lgb_pinball_p50": 0.06104,
    "lgb_pinball_p90": 0.02128,
    "lgb_coverage_80": 72.0
  },
  {
    "symbol": "DIST_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 70.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 52.33,
    "dir_acc_edge_vs_naive": 20.33,
    "lgb_rmse": 0.1089,
    "naive_rmse": 0.1125,
    "prophet_rmse": 0.1105,
    "lgb_mae": 0.0723,
    "naive_mae": 0.0756,
    "prophet_mae": 0.0836,
    "lgb_mean_pinball": 0.02374,
    "lgb_pinball_p10": 0.0121,
    "lgb_pinball_p50": 0.03615,
    "lgb_pinball_p90": 0.02298,
    "lgb_coverage_80": 78.67
  },
  {
    "symbol": "EXPO_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 48.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 69.67,
    "dir_acc_edge_vs_naive": -1.67,
    "lgb_rmse": 0.1019,
    "naive_rmse": 0.0927,
    "prophet_rmse": 0.0877,
    "lgb_mae": 0.0826,
    "naive_mae": 0.076,
    "prophet_mae": 0.0719,
    "lgb_mean_pinball": 0.02344,
    "lgb_pinball_p10": 0.01498,
    "lgb_pinball_p50": 0.04128,
    "lgb_pinball_p90": 0.01406,
    "lgb_coverage_80": 84.33
  },
  {
    "symbol": "HAYL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 64.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 56.33,
    "dir_acc_edge_vs_naive": 14.33,
    "lgb_rmse": 0.0985,
    "naive_rmse": 0.1035,
    "prophet_rmse": 0.1081,
    "lgb_mae": 0.0787,
    "naive_mae": 0.0858,
    "prophet_mae": 0.0827,
    "lgb_mean_pinball": 0.02583,
    "lgb_pinball_p10": 0.02073,
    "lgb_pinball_p50": 0.03934,
    "lgb_pinball_p90": 0.01742,
    "lgb_coverage_80": 87.33
  },
  {
    "symbol": "HEMA_N0000",
    "n_folds": 4,
    "total_test_samples": 240,
    "lgb_dir_acc": 64.58,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 59.17,
    "dir_acc_edge_vs_naive": 14.58,
    "lgb_rmse": 0.0875,
    "naive_rmse": 0.091,
    "prophet_rmse": 0.0913,
    "lgb_mae": 0.0707,
    "naive_mae": 0.0749,
    "prophet_mae": 0.0749,
    "lgb_mean_pinball": 0.02058,
    "lgb_pinball_p10": 0.01154,
    "lgb_pinball_p50": 0.03535,
    "lgb_pinball_p90": 0.01484,
    "lgb_coverage_80": 72.08
  },
  {
    "symbol": "HNB_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 45.0,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 48.33,
    "dir_acc_edge_vs_naive": -5.0,
    "lgb_rmse": 0.1244,
    "naive_rmse": 0.1199,
    "prophet_rmse": 0.1209,
    "lgb_mae": 0.0899,
    "naive_mae": 0.0796,
    "prophet_mae": 0.088,
    "lgb_mean_pinball": 0.02663,
    "lgb_pinball_p10": 0.01283,
    "lgb_pinball_p50": 0.04497,
    "lgb_pinball_p90": 0.02208,
    "lgb_coverage_80": 86.0
  },
  {
    "symbol": "JKH_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 38.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 50.0,
    "dir_acc_edge_vs_naive": -11.33,
    "lgb_rmse": 0.0833,
    "naive_rmse": 0.0839,
    "prophet_rmse": 0.0896,
    "lgb_mae": 0.063,
    "naive_mae": 0.0637,
    "prophet_mae": 0.0699,
    "lgb_mean_pinball": 0.01961,
    "lgb_pinball_p10": 0.01403,
    "lgb_pinball_p50": 0.03149,
    "lgb_pinball_p90": 0.01332,
    "lgb_coverage_80": 76.33
  },
  {
    "symbol": "KGAL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 56.0,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 56.67,
    "dir_acc_edge_vs_naive": 6.0,
    "lgb_rmse": 0.0817,
    "naive_rmse": 0.0823,
    "prophet_rmse": 0.0822,
    "lgb_mae": 0.0567,
    "naive_mae": 0.0591,
    "prophet_mae": 0.0574,
    "lgb_mean_pinball": 0.01747,
    "lgb_pinball_p10": 0.01043,
    "lgb_pinball_p50": 0.02837,
    "lgb_pinball_p90": 0.01361,
    "lgb_coverage_80": 77.67
  },
  {
    "symbol": "LIOC_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 72.0,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 32.0,
    "dir_acc_edge_vs_naive": 22.0,
    "lgb_rmse": 0.0577,
    "naive_rmse": 0.0622,
    "prophet_rmse": 0.1655,
    "lgb_mae": 0.0436,
    "naive_mae": 0.0471,
    "prophet_mae": 0.1267,
    "lgb_mean_pinball": 0.01706,
    "lgb_pinball_p10": 0.01094,
    "lgb_pinball_p50": 0.02178,
    "lgb_pinball_p90": 0.01847,
    "lgb_coverage_80": 92.33
  },
  {
    "symbol": "LOLC_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 64.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 69.67,
    "dir_acc_edge_vs_naive": 14.67,
    "lgb_rmse": 0.1277,
    "naive_rmse": 0.1283,
    "prophet_rmse": 0.1259,
    "lgb_mae": 0.0771,
    "naive_mae": 0.086,
    "prophet_mae": 0.0776,
    "lgb_mean_pinball": 0.02712,
    "lgb_pinball_p10": 0.01516,
    "lgb_pinball_p50": 0.03857,
    "lgb_pinball_p90": 0.02762,
    "lgb_coverage_80": 88.0
  },
  {
    "symbol": "LWL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 79.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 63.0,
    "dir_acc_edge_vs_naive": 29.33,
    "lgb_rmse": 0.0537,
    "naive_rmse": 0.0664,
    "prophet_rmse": 0.1109,
    "lgb_mae": 0.04,
    "naive_mae": 0.0533,
    "prophet_mae": 0.0906,
    "lgb_mean_pinball": 0.01383,
    "lgb_pinball_p10": 0.01104,
    "lgb_pinball_p50": 0.02001,
    "lgb_pinball_p90": 0.01045,
    "lgb_coverage_80": 90.33
  },
  {
    "symbol": "MADU_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 62.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 47.67,
    "dir_acc_edge_vs_naive": 12.67,
    "lgb_rmse": 0.0887,
    "naive_rmse": 0.0935,
    "prophet_rmse": 0.0939,
    "lgb_mae": 0.0656,
    "naive_mae": 0.0722,
    "prophet_mae": 0.0725,
    "lgb_mean_pinball": 0.02117,
    "lgb_pinball_p10": 0.01606,
    "lgb_pinball_p50": 0.03281,
    "lgb_pinball_p90": 0.01463,
    "lgb_coverage_80": 72.33
  },
  {
    "symbol": "NDB_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 56.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 52.33,
    "dir_acc_edge_vs_naive": 6.67,
    "lgb_rmse": 0.1376,
    "naive_rmse": 0.1467,
    "prophet_rmse": 0.1553,
    "lgb_mae": 0.1031,
    "naive_mae": 0.1093,
    "prophet_mae": 0.1211,
    "lgb_mean_pinball": 0.03293,
    "lgb_pinball_p10": 0.02089,
    "lgb_pinball_p50": 0.05153,
    "lgb_pinball_p90": 0.02636,
    "lgb_coverage_80": 73.67
  },
  {
    "symbol": "ODEL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 64.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 64.33,
    "dir_acc_edge_vs_naive": 14.33,
    "lgb_rmse": 0.9452,
    "naive_rmse": 0.9425,
    "prophet_rmse": 0.9421,
    "lgb_mae": 0.232,
    "naive_mae": 0.2357,
    "prophet_mae": 0.2335,
    "lgb_mean_pinball": 0.10658,
    "lgb_pinball_p10": 0.10285,
    "lgb_pinball_p50": 0.11602,
    "lgb_pinball_p90": 0.10087,
    "lgb_coverage_80": 84.0
  },
  {
    "symbol": "OSEA_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 62.0,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 76.67,
    "dir_acc_edge_vs_naive": 12.0,
    "lgb_rmse": 0.0976,
    "naive_rmse": 0.1084,
    "prophet_rmse": 0.1022,
    "lgb_mae": 0.0717,
    "naive_mae": 0.0779,
    "prophet_mae": 0.0711,
    "lgb_mean_pinball": 0.02325,
    "lgb_pinball_p10": 0.01276,
    "lgb_pinball_p50": 0.03584,
    "lgb_pinball_p90": 0.02114,
    "lgb_coverage_80": 81.33
  },
  {
    "symbol": "RICH_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 45.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 40.67,
    "dir_acc_edge_vs_naive": -4.33,
    "lgb_rmse": 0.095,
    "naive_rmse": 0.0948,
    "prophet_rmse": 0.0974,
    "lgb_mae": 0.067,
    "naive_mae": 0.0679,
    "prophet_mae": 0.0723,
    "lgb_mean_pinball": 0.02169,
    "lgb_pinball_p10": 0.0146,
    "lgb_pinball_p50": 0.03349,
    "lgb_pinball_p90": 0.01698,
    "lgb_coverage_80": 79.33
  },
  {
    "symbol": "SAMP_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 51.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 53.67,
    "dir_acc_edge_vs_naive": 1.33,
    "lgb_rmse": 0.0723,
    "naive_rmse": 0.07,
    "prophet_rmse": 0.0957,
    "lgb_mae": 0.0557,
    "naive_mae": 0.0522,
    "prophet_mae": 0.0732,
    "lgb_mean_pinball": 0.01805,
    "lgb_pinball_p10": 0.01154,
    "lgb_pinball_p50": 0.02787,
    "lgb_pinball_p90": 0.01475,
    "lgb_coverage_80": 89.33
  },
  {
    "symbol": "SEYB_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 62.67,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 47.0,
    "dir_acc_edge_vs_naive": 12.67,
    "lgb_rmse": 0.0985,
    "naive_rmse": 0.1156,
    "prophet_rmse": 0.1153,
    "lgb_mae": 0.0741,
    "naive_mae": 0.0888,
    "prophet_mae": 0.0916,
    "lgb_mean_pinball": 0.02596,
    "lgb_pinball_p10": 0.01571,
    "lgb_pinball_p50": 0.03707,
    "lgb_pinball_p90": 0.0251,
    "lgb_coverage_80": 88.67
  },
  {
    "symbol": "SLTL_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 45.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 40.67,
    "dir_acc_edge_vs_naive": -4.67,
    "lgb_rmse": 0.1077,
    "naive_rmse": 0.1038,
    "prophet_rmse": 0.1429,
    "lgb_mae": 0.0833,
    "naive_mae": 0.0842,
    "prophet_mae": 0.113,
    "lgb_mean_pinball": 0.02445,
    "lgb_pinball_p10": 0.01427,
    "lgb_pinball_p50": 0.04167,
    "lgb_pinball_p90": 0.01741,
    "lgb_coverage_80": 82.33
  },
  {
    "symbol": "TKYO_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 53.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 59.0,
    "dir_acc_edge_vs_naive": 3.33,
    "lgb_rmse": 0.1082,
    "naive_rmse": 0.1122,
    "prophet_rmse": 0.1071,
    "lgb_mae": 0.0812,
    "naive_mae": 0.0883,
    "prophet_mae": 0.0816,
    "lgb_mean_pinball": 0.0251,
    "lgb_pinball_p10": 0.01552,
    "lgb_pinball_p50": 0.04062,
    "lgb_pinball_p90": 0.01916,
    "lgb_coverage_80": 87.0
  },
  {
    "symbol": "UML_N0000",
    "n_folds": 5,
    "total_test_samples": 300,
    "lgb_dir_acc": 63.33,
    "naive_dir_acc": 50.0,
    "prophet_dir_acc": 72.0,
    "dir_acc_edge_vs_naive": 13.33,
    "lgb_rmse": 0.1413,
    "naive_rmse": 0.1474,
    "prophet_rmse": 0.1435,
    "lgb_mae": 0.1092,
    "naive_mae": 0.1206,
    "prophet_mae": 0.1148,
    "lgb_mean_pinball": 0.03245,
    "lgb_pinball_p10": 0.01947,
    "lgb_pinball_p50": 0.05459,
    "lgb_pinball_p90": 0.02329,
    "lgb_coverage_80": 84.67
  }
];
