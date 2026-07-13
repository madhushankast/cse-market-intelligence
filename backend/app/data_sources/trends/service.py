import logging
import pandas as pd
from app.data_sources.trends.client import TrendsClient

logger = logging.getLogger(__name__)


class TrendsService:


    def __init__(self):

        self.client = TrendsClient()


    def get_search_trends(self, keyword: str = "CSE") -> pd.DataFrame:

        try:

            logger.info(f"Attempting to query Google Trends for: '{keyword}'")

            df = self.client.fetch_live(keyword)

            if not df.empty:

                df["date"] = pd.to_datetime(df["date"])

                return df

        except Exception as e:

            logger.warning(f"Google Trends live query failed: {e}. Falling back to CSV.")


        # Fallback

        df = self.client.fetch_fallback()

        df["date"] = pd.to_datetime(df["date"])

        return df
