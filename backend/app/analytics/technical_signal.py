"""
Technical Signal Engine
-----------------------
Pure rule-based scoring engine that converts already-computed technical
indicators (RSI, MACD, SMA, Volume, Bollinger Bands) into a beginner-friendly
market signal with confidence score and plain-language explanations.

Deliberately avoids "BUY / SELL" language — uses tendency/outlook language
because markets are uncertain and this is an educational analytics platform.
"""

import math
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple


# ── Rating thresholds ────────────────────────────────────────────────────────
def _score_to_rating(score: int) -> str:
    if score >= 3:
        return "Bullish"
    if score >= 1:
        return "Slightly Positive"
    if score >= -1:
        return "Neutral"
    if score >= -3:
        return "Slightly Bearish"
    return "Bearish"


def _score_to_confidence(score: int) -> int:
    """Maps absolute score magnitude to a rough confidence percentage."""
    return min(95, 50 + abs(score) * 9)


def _safe(val) -> Optional[float]:
    """Return float or None, stripping NaN/Inf."""
    try:
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, 4)
    except (TypeError, ValueError):
        return None


# ── Individual indicator scorers ─────────────────────────────────────────────

def _score_rsi(rsi: Optional[float]) -> Dict[str, Any]:
    if rsi is None:
        return {"indicator": "RSI", "value": None, "status": "Unknown",
                "label": "Insufficient data to calculate RSI", "score": 0}

    if rsi < 30:
        return {"indicator": "RSI", "value": round(rsi, 1), "score": 2,
                "status": "Oversold",
                "label": f"RSI {rsi:.1f} — Market may be oversold, potential recovery signal"}
    if rsi < 50:
        return {"indicator": "RSI", "value": round(rsi, 1), "score": 0,
                "status": "Neutral",
                "label": f"RSI {rsi:.1f} — Momentum is neutral to slightly weak"}
    if rsi < 70:
        return {"indicator": "RSI", "value": round(rsi, 1), "score": 1,
                "status": "Positive",
                "label": f"RSI {rsi:.1f} — Healthy buying momentum"}
    # rsi >= 70
    return {"indicator": "RSI", "value": round(rsi, 1), "score": -1,
            "status": "Overbought",
            "label": f"RSI {rsi:.1f} — Market may be overbought, momentum may slow"}


def _score_sma20(close: float, sma20: Optional[float]) -> Dict[str, Any]:
    if sma20 is None:
        return {"indicator": "SMA20 Trend", "value": None, "status": "Unknown",
                "label": "Insufficient data for 20-day moving average", "score": 0}

    pct = ((close - sma20) / sma20) * 100
    if close > sma20:
        return {"indicator": "SMA20 Trend", "value": round(sma20, 2), "score": 1,
                "status": "Uptrend",
                "label": f"Price is {pct:.1f}% above 20-day moving average (short-term uptrend)"}
    return {"indicator": "SMA20 Trend", "value": round(sma20, 2), "score": -1,
            "status": "Downtrend",
            "label": f"Price is {abs(pct):.1f}% below 20-day moving average (short-term downtrend)"}


def _score_sma50(close: float, sma50: Optional[float]) -> Dict[str, Any]:
    if sma50 is None:
        return {"indicator": "SMA50 Trend", "value": None, "status": "Unknown",
                "label": "Insufficient data for 50-day moving average", "score": 0}

    pct = ((close - sma50) / sma50) * 100
    if close > sma50:
        return {"indicator": "SMA50 Trend", "value": round(sma50, 2), "score": 1,
                "status": "Uptrend",
                "label": f"Price is {pct:.1f}% above 50-day average (medium-term uptrend)"}
    return {"indicator": "SMA50 Trend", "value": round(sma50, 2), "score": -1,
            "status": "Downtrend",
            "label": f"Price is {abs(pct):.1f}% below 50-day average (medium-term downtrend)"}


def _score_macd(macd: Optional[float], macd_signal: Optional[float]) -> Dict[str, Any]:
    if macd is None or macd_signal is None:
        return {"indicator": "MACD", "value": None, "status": "Unknown",
                "label": "Insufficient data for MACD calculation", "score": 0}

    diff = macd - macd_signal
    if diff > 0:
        return {"indicator": "MACD", "value": round(macd, 4), "score": 1,
                "status": "Bullish",
                "label": f"MACD ({macd:.3f}) is above signal line — improving momentum"}
    return {"indicator": "MACD", "value": round(macd, 4), "score": -1,
            "status": "Bearish",
            "label": f"MACD ({macd:.3f}) is below signal line — weakening momentum"}


def _score_volume(volume: Optional[float], volume_ma: Optional[float]) -> Dict[str, Any]:
    if volume is None or volume_ma is None or volume_ma == 0:
        return {"indicator": "Volume", "value": None, "status": "Unknown",
                "label": "Volume data unavailable", "score": 0}

    ratio = volume / volume_ma
    vol_int = int(volume)
    if ratio > 1.3:
        return {"indicator": "Volume", "value": vol_int, "score": 1,
                "status": "High",
                "label": f"Volume is {ratio:.1f}x above average — strong market interest"}
    if ratio < 0.7:
        return {"indicator": "Volume", "value": vol_int, "score": -1,
                "status": "Low",
                "label": f"Volume is {ratio:.1f}x below average — weak participation"}
    return {"indicator": "Volume", "value": vol_int, "score": 0,
            "status": "Neutral",
            "label": f"Volume is within normal range ({ratio:.1f}x average)"}


def _score_bollinger(close: float, upper_bb: Optional[float],
                     lower_bb: Optional[float], middle_bb: Optional[float]) -> Dict[str, Any]:
    """Bollinger Band position — informational only, not scored."""
    if upper_bb is None or lower_bb is None or middle_bb is None:
        return {"position": "unknown", "label": "Bollinger Band data unavailable"}

    band_width = upper_bb - lower_bb
    if band_width == 0:
        return {"position": "unknown", "label": "Bollinger Band width is zero"}

    position_pct = (close - lower_bb) / band_width  # 0 = lower, 1 = upper

    if close >= upper_bb:
        return {"position": "upper", "pct": round(position_pct * 100, 1),
                "label": "Price touching upper Bollinger Band — possible resistance"}
    if close <= lower_bb:
        return {"position": "lower", "pct": round(position_pct * 100, 1),
                "label": "Price touching lower Bollinger Band — possible support"}
    if position_pct > 0.7:
        return {"position": "upper_mid", "pct": round(position_pct * 100, 1),
                "label": "Price in upper half of Bollinger Band — moderate bullish pressure"}
    if position_pct < 0.3:
        return {"position": "lower_mid", "pct": round(position_pct * 100, 1),
                "label": "Price in lower half of Bollinger Band — moderate bearish pressure"}
    return {"position": "middle", "pct": round(position_pct * 100, 1),
            "label": "Price within normal Bollinger Band range"}


# ── Reasons and Warnings builder ─────────────────────────────────────────────

def _build_reasons_warnings(signals: List[Dict], rsi_val: Optional[float],
                             bollinger: Dict) -> Tuple[List[str], List[str]]:
    reasons: List[str] = []
    warnings: List[str] = []

    for sig in signals:
        s = sig["score"]
        ind = sig["indicator"]
        status = sig.get("status", "")

        if s > 0:
            reasons.append(sig["label"])
        elif s < 0:
            warnings.append(sig["label"])

    # Extra RSI warnings
    if rsi_val is not None:
        if rsi_val > 65:
            warnings.append(f"RSI at {rsi_val:.1f} — approaching overbought territory (>70)")
        if rsi_val < 35:
            reasons.append(f"RSI at {rsi_val:.1f} — potentially oversold, watch for reversal")

    # Bollinger extras
    bb_pos = bollinger.get("position", "")
    if bb_pos == "upper":
        warnings.append(bollinger["label"])
    elif bb_pos == "lower":
        reasons.append(bollinger["label"])

    return reasons, warnings


# ── Main public interface ────────────────────────────────────────────────────

class TechnicalSignalEngine:
    """
    Calculates a rule-based technical signal from an already-processed DataFrame.
    The DataFrame must contain columns produced by IndicatorBuilder.
    """

    @staticmethod
    def calculate(df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty or len(df) < 10:
            return {
                "error": "Insufficient historical data for technical analysis",
                "min_rows_needed": 10
            }

        # Use latest row (most recent trading day)
        latest = df.iloc[-1]

        close      = _safe(latest.get("close"))
        rsi        = _safe(latest.get("rsi"))
        macd       = _safe(latest.get("macd"))
        macd_sig   = _safe(latest.get("macd_signal"))
        sma20      = _safe(latest.get("sma_20"))
        sma50      = _safe(latest.get("sma_50"))
        volume     = _safe(latest.get("volume"))
        volume_ma  = _safe(latest.get("volume_ma"))
        upper_bb   = _safe(latest.get("upper_bb"))
        lower_bb   = _safe(latest.get("lower_bb"))
        middle_bb  = _safe(latest.get("middle_bb"))
        atr        = _safe(latest.get("atr"))
        volatility = _safe(latest.get("volatility"))
        as_of      = str(latest.get("date", ""))

        if close is None:
            return {"error": "Close price data is missing"}

        # ── Score each indicator ──────────────────────────────────────────
        signals = [
            _score_rsi(rsi),
            _score_sma20(close, sma20),
            _score_sma50(close, sma50),
            _score_macd(macd, macd_sig),
            _score_volume(volume, volume_ma),
        ]

        total_score = sum(s["score"] for s in signals)
        rating      = _score_to_rating(total_score)
        confidence  = _score_to_confidence(total_score)

        # ── Bollinger (informational, not scored) ─────────────────────────
        bollinger = _score_bollinger(close, upper_bb, lower_bb, middle_bb)

        # ── Volatility description ────────────────────────────────────────
        vol_label = "Unknown"
        if volatility is not None:
            if volatility < 0.01:
                vol_label = "Low — relatively stable price movement"
            elif volatility < 0.025:
                vol_label = "Moderate — normal price fluctuation"
            else:
                vol_label = "High — significant price swings, higher risk"

        # ── Recent price trend (last 7 data points) ───────────────────────
        recent_closes: List[float] = []
        if "close" in df.columns and len(df) >= 7:
            tail = df["close"].dropna().tail(7)
            recent_closes = [round(float(v), 2) for v in tail.tolist()]

        trend_direction = "Flat"
        if len(recent_closes) >= 2:
            chg = recent_closes[-1] - recent_closes[0]
            pct = (chg / recent_closes[0]) * 100
            if pct > 1.0:
                trend_direction = f"Rising ({pct:+.1f}% over 7 days)"
            elif pct < -1.0:
                trend_direction = f"Falling ({pct:+.1f}% over 7 days)"
            else:
                trend_direction = f"Sideways ({pct:+.1f}% over 7 days)"

        # ── Action Signal, Trend, Momentum ──────────────────────────────
        action_signal = "HOLD"
        if total_score >= 2:
            action_signal = "BUY"
        elif total_score <= -2:
            action_signal = "SELL"

        trend_view = "Neutral"
        if total_score >= 1:
            trend_view = "Bullish"
        elif total_score <= -1:
            trend_view = "Bearish"

        momentum_view = "Neutral"
        if macd is not None and macd_sig is not None:
            momentum_view = "Improving" if macd > macd_sig else "Weakening"

        # ── Reasons & Warnings ────────────────────────────────────────────
        reasons, warnings_list = _build_reasons_warnings(signals, rsi, bollinger)

        # Add volatility-based warning
        if volatility is not None and volatility > 0.025:
            warnings_list.append(f"High volatility detected — price swings are above normal")

        # Formatted reasons (✓) and risks (⚠)
        formatted_reasons = [f"✓ {r}" for r in reasons]
        formatted_risks = [f"⚠ {w}" for w in warnings_list]

        return {
            "symbol":           latest.get("symbol", ""),
            "as_of":            as_of,
            "current_price":    close,
            "action_signal":    action_signal,
            "signal":           action_signal,
            "rating":           rating,
            "score":            total_score,
            "score_max":        5,
            "confidence":       confidence,
            "trend":            trend_view,
            "momentum":         momentum_view,
            "signals":          signals,
            "rsi_value":        rsi,
            "bollinger":        bollinger,
            "volatility":       {"value": volatility, "label": vol_label},
            "atr":              atr,
            "recent_closes":    recent_closes,
            "trend_direction":  trend_direction,
            "reasons":          formatted_reasons,
            "risks":            formatted_risks,
            "warnings":         warnings_list,
        }
