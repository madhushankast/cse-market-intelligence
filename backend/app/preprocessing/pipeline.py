import pandas as pd
from app.preprocessing.cleaner import DataCleaner
from app.preprocessing.indicators import IndicatorBuilder


class ProcessingPipeline:


    def __init__(self):

        self.cleaner = DataCleaner()

        self.indicators = IndicatorBuilder()


    def process(self, df: pd.DataFrame) -> pd.DataFrame:

        df = self.cleaner.clean(df)

        df = self.indicators.add_indicators(df)

        return df
