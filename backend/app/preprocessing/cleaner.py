import pandas as pd


class DataCleaner:


    def clean(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()


        # Remove duplicates based on symbol and date

        df.drop_duplicates(subset=["symbol", "date"], inplace=True)


        # Sort by date

        df["date"] = pd.to_datetime(df["date"])

        df.sort_values("date", inplace=True)

        df.reset_index(drop=True, inplace=True)


        # Handle missing values via forward fill
        df.ffill(inplace=True)

        return df
