from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import datetime
from app.database.connection import SessionLocal
from app.repositories.stock_repository import StockPriceRepository
from app.preprocessing.pipeline import ProcessingPipeline
from app.analytics.correlation import CorrelationAnalyzer
from app.analytics.causality import GrangerCausalityTester
from app.analytics.lag import LagAnalyzer
from app.analytics.technical_signal import TechnicalSignalEngine
from app.analytics.backtest import BacktestEngine


router = APIRouter()
pipeline = ProcessingPipeline()


def clean_val(val):
    if val is None or pd.isna(val) or np.isinf(val):
        return None
    return float(val)


@router.get("/analytics/stocks/{symbol}")
def get_analytics(symbol: str):
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol)

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No stock data found in DB for {symbol}. Run ingestion POST first."
            )

        # Convert to DataFrame
        data = [{
            "symbol": r.symbol,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in records]

        df_raw = pd.DataFrame(data)

        # Run preprocessing and indicator builder pipeline
        df_processed = pipeline.process(df_raw)

        # Grab the latest daily row
        latest_row = df_processed.iloc[-1]

        return {
            "symbol": symbol,
            "features": {
                "close": clean_val(latest_row.get("close")),
                "daily_return": clean_val(latest_row.get("daily_return")),
                "rsi": clean_val(latest_row.get("rsi")),
                "sma_20": clean_val(latest_row.get("sma_20")),
                "sma_50": clean_val(latest_row.get("sma_50")),
                "macd": clean_val(latest_row.get("macd")),
                "volatility": clean_val(latest_row.get("volatility")),
                "date": str(latest_row.get("date"))
            }
        }
    finally:
        db.close()


def _get_processed_dataframe(symbol: str) -> pd.DataFrame:
    """Helper method to fetch and calculate stock indicators."""
    db = SessionLocal()
    try:
        repo = StockPriceRepository(db)
        records = repo.get_by_symbol(symbol)
        if not records:
            raise ValueError(f"No stock data found in DB for {symbol}.")

        data = [{
            "symbol": r.symbol,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume
        } for r in records]
        df_stock = pd.DataFrame(data)
        return pipeline.process(df_stock)
    finally:
        db.close()


@router.get("/analytics/stocks/{symbol}/integrated")
def get_integrated_data(symbol: str):
    try:
        df_processed = _get_processed_dataframe(symbol)
        output = []
        for _, row in df_processed.iterrows():
            dt_str = str(row["date"])
            output.append({
                "date": dt_str,
                "symbol": row["symbol"],
                "close": clean_val(row["close"]),
                "volume": int(row["volume"]),
                "rsi": clean_val(row.get("rsi")),
                "macd": clean_val(row.get("macd")),
                "volatility": clean_val(row.get("volatility")),
                "sma_20": clean_val(row.get("sma_20")),
                "sma_50": clean_val(row.get("sma_50"))
            })

        return {
            "symbol": symbol,
            "count": len(output),
            "data": output
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{symbol}/correlation")
def get_correlation(symbol: str):
    try:
        df_processed = _get_processed_dataframe(symbol)
        return CorrelationAnalyzer.calculate(df_processed)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{symbol}/causality")
def get_causality(symbol: str):
    try:
        df_processed = _get_processed_dataframe(symbol)
        return GrangerCausalityTester.test_causality(df_processed)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/analytics/{symbol}/lag")
def get_lag(symbol: str):
    try:
        df_processed = _get_processed_dataframe(symbol)
        return LagAnalyzer.calculate_lag_correlations(df_processed)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{symbol}/technical-summary")
def get_technical_summary(symbol: str):
    """
    Returns a beginner-friendly technical analysis summary for the given symbol.
    Scores RSI, SMA20/50 trend, MACD crossover, and Volume against their moving
    average to produce an overall market signal with confidence and explanations.

    Deliberately avoids BUY/SELL — uses tendency language (Bullish, Neutral, etc.)
    because markets are uncertain.
    """
    try:
        df_processed = _get_processed_dataframe(symbol)
        result = TechnicalSignalEngine.calculate(df_processed)

        # Propagate engine-level errors as 422 (not a server error, just bad data)
        if "error" in result:
            raise HTTPException(status_code=422, detail=result["error"])

        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/stocks/{symbol}/backtest")
def get_backtest(symbol: str, initial_capital: float = 100000.0):
    """
    Runs trading backtest simulation on historical stock data.
    """
    try:
        df_processed = _get_processed_dataframe(symbol)
        engine = BacktestEngine(initial_capital=initial_capital)
        res = engine.run(df_processed)
        res["symbol"] = symbol
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


