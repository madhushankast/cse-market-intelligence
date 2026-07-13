import logging
import pandas as pd
from app.data_sources.cse.client import CSEClient
from app.data_sources.cse.csv_client import CSECSVClient
from app.data_sources.cse.parser import CSEParser

logger = logging.getLogger(__name__)


class CSEService:


    def __init__(self):

        self.client = CSEClient()

        self.csv_client = CSECSVClient()

        self.parser = CSEParser()



    def get_stock_prices(self, symbol: str, period: str = "5") -> pd.DataFrame:

        """
        Retrieves stock prices. Tries API first, falls back to CSV on failure.
        """

        formatted_symbol = symbol if "." in symbol else f"{symbol}.N0000"


        try:

            logger.info(f"Attempting to fetch {formatted_symbol} from CSE API")

            stock_id = self.client.get_stock_id(formatted_symbol)

            if stock_id:

                raw_data = self.client.get_historical_data(stock_id, period=period)

                df = self.parser.parse_api_response(formatted_symbol, raw_data)

                if not df.empty:

                    return df

            logger.warning(f"Could not resolve stockId for {formatted_symbol}. Falling back to CSV.")

        except Exception as e:

            logger.error(f"Error fetching from CSE API for {formatted_symbol}: {e}. Falling back to CSV.")


        try:

            logger.info(f"Loading {symbol} from CSV fallback")

            csv_data = self.csv_client.get_historical_data(symbol)

            return self.parser.parse_csv_data(formatted_symbol, csv_data)

        except Exception as csv_err:

            logger.error(f"Fallback CSV loading failed for {symbol}: {csv_err}")

            return pd.DataFrame(columns=["symbol", "date", "open", "high", "low", "close", "volume"])
