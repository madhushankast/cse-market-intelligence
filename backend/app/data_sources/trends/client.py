import os
import pandas as pd
from pytrends.request import TrendReq


class TrendsClient:


    def __init__(self):

        self.pytrends = TrendReq(hl='en-US', tz=360)

        self.fallback_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "raw", "trends", "trends_cse.csv"
        )


    def fetch_live(self, keyword: str) -> pd.DataFrame:

        """
        Fetch query trends from Google Trends API.
        """

        self.pytrends.build_payload([keyword], cat=0, timeframe='today 5-y', geo='LK', gprop='')

        df = self.pytrends.interest_over_time()

        if not df.empty:

            df = df.reset_index()

            # Rename keyword column to 'trend_score'

            df.rename(columns={keyword: "trend_score", "date": "date"}, inplace=True)

            return df[["date", "trend_score"]]

        return pd.DataFrame()


    def fetch_fallback(self) -> pd.DataFrame:

        """
        Fetch query trends from local CSV fallback.
        """

        if not os.path.exists(self.fallback_path):

            raise FileNotFoundError(f"Trends fallback CSV not found at {self.fallback_path}")


        return pd.read_csv(self.fallback_path)
