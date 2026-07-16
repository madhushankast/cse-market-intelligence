from sqlalchemy import func
from app.database.models import StockPrice
from app.repositories.base import BaseRepository


class StockPriceRepository(BaseRepository):

    def get_by_symbol(self, symbol: str) -> list[StockPrice]:
        formatted_symbol = symbol if "." in symbol else f"{symbol}.N0000"
        return self.db.query(StockPrice).filter(
            (StockPrice.symbol == formatted_symbol) | (StockPrice.symbol == symbol)
        ).order_by(StockPrice.date.asc()).all()

    def check_exists(self, symbol: str, date: str) -> bool:
        return self.db.query(StockPrice).filter(
            StockPrice.symbol == symbol,
            StockPrice.date == date
        ).first() is not None

    def add(self, stock_price: StockPrice) -> StockPrice:
        self.db.add(stock_price)
        return stock_price

    def get_total_count(self) -> int:
        return self.db.query(StockPrice).count()

    def get_unique_symbols_count(self) -> int:
        return self.db.query(func.distinct(StockPrice.symbol)).count()

    def get_last_updated_date(self) -> str:
        res = self.db.query(func.max(StockPrice.date)).scalar()
        return res if res else "N/A"
