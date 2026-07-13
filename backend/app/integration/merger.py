import pandas as pd


class DataMerger:


    def merge(self, stock: pd.DataFrame, macro: pd.DataFrame, trends: pd.DataFrame) -> pd.DataFrame:

        stock = stock.copy()

        macro = macro.copy()

        trends = trends.copy()


        # Normalize dates

        stock["date"] = pd.to_datetime(stock["date"])

        macro["date"] = pd.to_datetime(macro["date"])

        trends["date"] = pd.to_datetime(trends["date"])


        # Sort for merge_asof requirements

        stock.sort_values("date", inplace=True)

        macro.sort_values("date", inplace=True)

        trends.sort_values("date", inplace=True)


        # Merge macroeconomic indicators using backward direction (nearest preceding date)

        result = pd.merge_asof(stock, macro, on="date", direction="backward")


        # Merge search trends using backward direction (nearest preceding date)

        result = pd.merge_asof(result, trends, on="date", direction="backward")


        # Apply backward fill for any indicators prior to the first stock date

        fill_cols = ["inflation", "usd_lkr", "interest_rate", "trend_score"]

        for col in fill_cols:

            if col in result.columns:

                result[col] = result[col].bfill()


        return result
