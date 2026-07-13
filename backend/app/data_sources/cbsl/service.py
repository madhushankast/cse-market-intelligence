import pandas as pd
from app.data_sources.cbsl.client import CBSLClient
from app.data_sources.cbsl.parser import CBSLParser


class CBSLService:


    def __init__(self):

        self.client = CBSLClient()

        self.parser = CBSLParser()


    def get_macro_indicators(self) -> pd.DataFrame:

        raw_data = self.client.fetch()

        return self.parser.parse(raw_data)
