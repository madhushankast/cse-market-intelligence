import pandas as pd


class CBSLParser:


    def parse(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        return df
