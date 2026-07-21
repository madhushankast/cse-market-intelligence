import ta
import pandas as pd
import numpy as np


class IndicatorBuilder:

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Price Features & Returns
        df["daily_return"] = df["close"].pct_change()
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))
        df["high_low_pct"] = (df["high"] - df["low"]) / df["low"]
        df["open_close_pct"] = (df["close"] - df["open"]) / df["open"]

        # 2. Simple & Exponential Moving Averages (Trend)
        df["sma_10"] = df["close"].rolling(10).mean()
        df["sma_20"] = df["close"].rolling(20).mean()
        df["sma_50"] = df["close"].rolling(50).mean()
        df["ema_10"] = df["close"].ewm(span=10, adjust=False).mean()
        df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()

        # ADX (Trend Strength)
        adx_ind = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14)
        df["adx"] = adx_ind.adx()

        # 3. Momentum Indicators
        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
        
        macd_ind = ta.trend.MACD(close=df["close"])
        df["macd"] = macd_ind.macd()
        df["macd_signal"] = macd_ind.macd_signal()
        df["roc"] = ta.momentum.ROCIndicator(close=df["close"], window=12).roc()

        stoch_ind = ta.momentum.StochasticOscillator(
            high=df["high"], low=df["low"], close=df["close"], window=14, smooth_window=3
        )
        df["stoch_k"] = stoch_ind.stoch()
        df["stoch_d"] = stoch_ind.stoch_signal()

        df["williams_r"] = ta.momentum.WilliamsRIndicator(
            high=df["high"], low=df["low"], close=df["close"], lbp=14
        ).williams_r()

        # 4. Volatility Indicators
        bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
        df["upper_bb"] = bb.bollinger_hband()
        df["middle_bb"] = bb.bollinger_mavg()
        df["lower_bb"] = bb.bollinger_lband()
        
        df["atr"] = ta.volatility.AverageTrueRange(
            high=df["high"], low=df["low"], close=df["close"], window=14
        ).average_true_range()

        # 5. Volume Indicators
        df["obv"] = ta.volume.OnBalanceVolumeIndicator(
            close=df["close"], volume=df["volume"]
        ).on_balance_volume()
        df["volume_ma"] = df["volume"].rolling(20).mean()

        # Fallback volatility for backward compatibility (20-day std of returns)
        df["volatility"] = df["daily_return"].rolling(20).std()

        return df

