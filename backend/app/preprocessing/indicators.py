import ta
import pandas as pd


class IndicatorBuilder:


    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()


        # 1. Daily Return

        df["daily_return"] = df["close"].pct_change()


        # 2. Simple Moving Averages (SMA20, SMA50)

        df["sma_20"] = df["close"].rolling(20).mean()

        df["sma_50"] = df["close"].rolling(50).mean()


        # 3. Relative Strength Index (RSI)

        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()


        # 4. Moving Average Convergence Divergence (MACD)

        df["macd"] = ta.trend.MACD(close=df["close"]).macd()


        # 5. Volatility (20-day standard deviation of returns)

        df["volatility"] = df["daily_return"].rolling(20).std()


        return df
