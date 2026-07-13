import os
import pandas as pd


class CSECSVClient:


    def __init__(self, data_dir: str = None):

        if data_dir is None:

            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "data", "raw", "cse"
            )

        else:

            self.data_dir = data_dir



    def get_historical_data(self, symbol: str) -> pd.DataFrame:

        """
        Load historical stock data from local CSV fallback.
        """

        clean_symbol = symbol.split(".")[0]

        file_path = os.path.join(self.data_dir, f"{clean_symbol}.csv")


        if not os.path.exists(file_path):

            raise FileNotFoundError(f"Fallback CSV not found at {file_path}")


        return pd.read_csv(file_path)
