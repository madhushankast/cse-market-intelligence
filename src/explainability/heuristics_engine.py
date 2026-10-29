"""
Domain Indicator Heuristics Engine
----------------------------------
Translates mathematical features (OHLCV & ASPI benchmark indicators) into
standardized indicator validation cards tagged as 'Supporting', 'Rejecting / Risk',
or 'Neutral' relative to the 30-day predicted trajectory.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class IndicatorHeuristicsEngine:
    """
    Domain Heuristics Engine (Layer 2).
    Validates model return predictions against institutional technical rules of thumb:
      - Relative Strength Index (RSI) momentum & boundary overbought/oversold states
      - Moving average crossovers & medium-term trend alignment (SMA 20/50)
      - Intraday high-low volatility regimes (Parkinson Volatility)
      - Colombo Stock Exchange broad market benchmark momentum (ASPI)
      - MACD momentum expansion & volume surge confirmation
    """

    def evaluate_alignment(
        self,
        features: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        predicted_return_p50: float,
    ) -> List[Dict[str, Any]]:
        """
        Evaluates indicator alignment against the 30-day median return prediction.

        Parameters:
          features: Feature mapping or row containing technical and market indicators.
          predicted_return_p50: Cumulative 30-day forward log return (y_hat_P50).

        Returns:
          List of standardized indicator status dictionaries:
            [{
                "indicator": str,
                "value": Any,
                "status": "Supporting" | "Rejecting / Risk" | "Neutral",
                "signal": "Bullish" | "Bearish" | "Neutral",
                "explanation": str
            }]
        """
        # Convert to dictionary
        if isinstance(features, pd.DataFrame):
            row = features.iloc[-1].to_dict()
        elif isinstance(features, pd.Series):
            row = features.to_dict()
        else:
            row = dict(features)

        is_bullish = predicted_return_p50 > 0.0
        cards: List[Dict[str, Any]] = []

        # ---------------------------------------------------------------------
        # 1. RSI (14-day)
        # ---------------------------------------------------------------------
        rsi_raw = row.get("rsi_14")
        if rsi_raw is not None and pd.notna(rsi_raw):
            rsi = float(rsi_raw)
            if is_bullish:
                if 35.0 <= rsi <= 60.0:
                    status = "Supporting"
                    signal = "Bullish"
                    explanation = (
                        f"RSI is in a healthy momentum zone ({rsi:.1f}), offering clear "
                        "upside room without immediate overbought resistance."
                    )
                elif rsi > 70.0:
                    status = "Rejecting / Risk"
                    signal = "Bearish"
                    explanation = (
                        f"RSI is overbought ({rsi:.1f} > 70), warning of buyer exhaustion "
                        "and heightened pullback / mean-reversion risk."
                    )
                elif rsi < 35.0:
                    status = "Supporting"
                    signal = "Bullish"
                    explanation = (
                        f"RSI is in an oversold rebound zone ({rsi:.1f} < 35), offering strong "
                        "value-recovery upside potential."
                    )
                else:  # 60 < rsi <= 70
                    status = "Neutral"
                    signal = "Bullish"
                    explanation = (
                        f"RSI is elevated at {rsi:.1f}, approaching overbought territory but "
                        "still carrying upward momentum."
                    )
            else:  # Bearish forecast
                if rsi < 30.0:
                    status = "Rejecting / Risk"
                    signal = "Bullish"
                    explanation = (
                        f"RSI is severely oversold ({rsi:.1f} < 30), creating divergence "
                        "and risk of an abrupt technical bounce against the short forecast."
                    )
                elif rsi > 70.0:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"RSI is overbought ({rsi:.1f} > 70), confirming rollover and "
                        "downward price pressure."
                    )
                elif 30.0 <= rsi <= 50.0:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"RSI is below midline ({rsi:.1f} <= 50), confirming sustained "
                        "downward price momentum."
                    )
                else:
                    status = "Neutral"
                    signal = "Neutral"
                    explanation = f"RSI is neutral at {rsi:.1f} relative to the downward trajectory."

            cards.append({
                "indicator": "RSI (14)",
                "value": round(rsi, 1),
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        # ---------------------------------------------------------------------
        # 2. Moving Average Trend (SMA 20 vs SMA 50)
        # ---------------------------------------------------------------------
        sma_ratio_raw = row.get("sma_ratio_20_50")
        if sma_ratio_raw is not None and pd.notna(sma_ratio_raw):
            sma_ratio = float(sma_ratio_raw)
            diff_pct = (sma_ratio - 1.0) * 100.0

            if is_bullish:
                if sma_ratio > 1.0:
                    status = "Supporting"
                    signal = "Bullish"
                    explanation = (
                        f"20-day SMA is {diff_pct:+.1f}% above 50-day SMA (Golden Cross alignment), "
                        "confirming medium-term upward trend support."
                    )
                else:
                    status = "Rejecting / Risk"
                    signal = "Bearish"
                    explanation = (
                        f"20-day SMA is {abs(diff_pct):.1f}% below 50-day SMA, indicating "
                        "downtrend resistance that could cap the forecast upside."
                    )
            else:
                if sma_ratio < 1.0:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"20-day SMA is {abs(diff_pct):.1f}% below 50-day SMA, confirming "
                        "medium-term downtrend pressure."
                    )
                else:
                    status = "Rejecting / Risk"
                    signal = "Bullish"
                    explanation = (
                        f"20-day SMA is {diff_pct:+.1f}% above 50-day SMA, opposing the negative "
                        "forecast with upward moving average momentum."
                    )

            cards.append({
                "indicator": "SMA 20/50 Trend",
                "value": round(sma_ratio, 3),
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        # ---------------------------------------------------------------------
        # 3. Intraday Volatility (Parkinson Volatility)
        # ---------------------------------------------------------------------
        vol_raw = row.get("parkinson_vol_20d") or row.get("parkinson_vol_10d") or row.get("parkinson_vol")
        if vol_raw is not None and pd.notna(vol_raw):
            vol_ann_pct = float(vol_raw) * 100.0
            if vol_ann_pct > 35.0:
                if is_bullish:
                    status = "Rejecting / Risk"
                    signal = "Bearish"
                    explanation = (
                        f"20-day Parkinson volatility is elevated at {vol_ann_pct:.1f}%, widening "
                        "the forecast cone and heightening downside drawdown risk."
                    )
                else:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"Elevated price variance ({vol_ann_pct:.1f}%) confirms unstable market "
                        "conditions supporting the downside projection."
                    )
            else:
                status = "Supporting"
                signal = "Bullish" if is_bullish else "Neutral"
                explanation = (
                    f"20-day Parkinson volatility is controlled ({vol_ann_pct:.1f}%), fostering "
                    "orderly price discovery along the projected path."
                )

            cards.append({
                "indicator": "Parkinson Volatility (20d)",
                "value": f"{vol_ann_pct:.1f}%",
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        # ---------------------------------------------------------------------
        # 4. CSE Market Benchmark Momentum (ASPI 30-day Trend)
        # ---------------------------------------------------------------------
        aspi_ret_raw = row.get("aspi_return_30d")
        if aspi_ret_raw is not None and pd.notna(aspi_ret_raw):
            aspi_ret_pct = float(aspi_ret_raw) * 100.0
            if is_bullish:
                if aspi_ret_pct > 0.0:
                    status = "Supporting"
                    signal = "Bullish"
                    explanation = (
                        f"CSE ASPI benchmark gained {aspi_ret_pct:+.1f}% over 30 days, providing "
                        "broad market tailwinds for the stock's expected advance."
                    )
                else:
                    status = "Neutral"  # Contrarian decoupling
                    signal = "Neutral"
                    explanation = (
                        f"CSE ASPI index is down {abs(aspi_ret_pct):.1f}% over 30 days; positive stock "
                        "forecast represents a contrarian decoupling from market headwinds."
                    )
            else:
                if aspi_ret_pct < 0.0:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"CSE ASPI index dropped {abs(aspi_ret_pct):.1f}% over 30 days, creating market-wide "
                        "selling pressure aligned with the negative forecast."
                    )
                else:
                    status = "Rejecting / Risk"
                    signal = "Bullish"
                    explanation = (
                        f"CSE ASPI benchmark is up {aspi_ret_pct:+.1f}%, creating risk of market-wide "
                        "buying lifting the stock against the negative prediction."
                    )

            cards.append({
                "indicator": "ASPI 30d Benchmark",
                "value": f"{aspi_ret_pct:+.1f}%",
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        # ---------------------------------------------------------------------
        # 5. MACD Momentum Acceleration
        # ---------------------------------------------------------------------
        macd_hist = row.get("macd_hist")
        if macd_hist is not None and pd.notna(macd_hist):
            hist_val = float(macd_hist)
            if is_bullish:
                if hist_val > 0.0:
                    status = "Supporting"
                    signal = "Bullish"
                    explanation = (
                        f"MACD histogram is positive ({hist_val:+.2f}), indicating active "
                        "bullish momentum expansion."
                    )
                else:
                    status = "Rejecting / Risk"
                    signal = "Bearish"
                    explanation = (
                        f"MACD histogram is negative ({hist_val:+.2f}), showing bearish divergence "
                        "that cautions against immediate breakout."
                    )
            else:
                if hist_val < 0.0:
                    status = "Supporting"
                    signal = "Bearish"
                    explanation = (
                        f"MACD histogram is negative ({hist_val:+.2f}), confirming downward "
                        "momentum acceleration."
                    )
                else:
                    status = "Rejecting / Risk"
                    signal = "Bullish"
                    explanation = (
                        f"MACD histogram is positive ({hist_val:+.2f}), warning that selling pressure "
                        "may be weakening."
                    )

            cards.append({
                "indicator": "MACD Histogram",
                "value": round(hist_val, 3),
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        # ---------------------------------------------------------------------
        # 6. Volume Surge & Institutional Activity
        # ---------------------------------------------------------------------
        vol_surge = row.get("volume_surge_ratio")
        if vol_surge is not None and pd.notna(vol_surge):
            surge_ratio = float(vol_surge)
            if surge_ratio >= 1.5:
                status = "Supporting" if is_bullish else "Neutral"
                signal = "Bullish"
                explanation = (
                    f"Volume is surging at {surge_ratio:.1f}x its 20-day moving average, signaling "
                    "heightened institutional liquidity."
                )
            elif surge_ratio < 0.7:
                status = "Neutral"
                signal = "Neutral"
                explanation = (
                    f"Volume is light ({surge_ratio:.1f}x 20d average), reflecting quiet trading "
                    "and low immediate turnover conviction."
                )
            else:
                status = "Supporting"
                signal = "Neutral"
                explanation = (
                    f"Volume is stable at {surge_ratio:.1f}x normal levels, consistent with orderly "
                    "continuous trading."
                )

            cards.append({
                "indicator": "Volume Surge Ratio",
                "value": round(surge_ratio, 2),
                "status": status,
                "signal": signal,
                "explanation": explanation,
            })

        return cards

    def evaluate_signals(
        self,
        latest_row: pd.Series,
        forecast_direction: str = "bullish",
    ) -> List[Dict[str, Any]]:
        """Backwards-compatible wrapper."""
        pred_ret = 0.05 if forecast_direction.lower() == "bullish" else -0.05
        return self.evaluate_alignment(latest_row, pred_ret)


# Alias for backward compatibility
HeuristicsEngine = IndicatorHeuristicsEngine
