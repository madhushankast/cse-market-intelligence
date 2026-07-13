from pydantic import BaseModel
from datetime import date


class StockPrice(BaseModel):
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
