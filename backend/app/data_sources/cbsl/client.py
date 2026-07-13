import os
import pandas as pd


class CBSLClient:


    def __init__(self):

        self.file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "raw", "cbsl", "macro_indicators.csv"
        )


    def fetch(self) -> pd.DataFrame:

        """
        Loads the macroeconomic indicators from the CSV database archive.
        """

        if not os.path.exists(self.file_path):

            raise FileNotFoundError(f"CBSL indicators CSV not found at {self.file_path}")


        return pd.read_csv(self.file_path)
