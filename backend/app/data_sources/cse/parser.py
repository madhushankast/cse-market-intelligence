import pandas as pd
import datetime


class CSEParser:


    def parse_api_response(self, symbol: str, json_data: dict) -> pd.DataFrame:

        """
        Convert raw API chartData response into a structured DataFrame.
        """

        chart_list = json_data.get("chartData", [])


        parsed_records = []

        for idx, pt in enumerate(chart_list):

            high = pt.get("h")

            low = pt.get("l")

            close = pt.get("p")

            volume = int(pt.get("q", 0))

            t_ms = pt.get("t")


            # Convert millisecond timestamp to YYYY-MM-DD

            dt = datetime.datetime.fromtimestamp(t_ms / 1000.0).date()


            # Estimate open price if missing

            prev_close = parsed_records[-1]["close"] if idx > 0 else close

            open_price = pt.get("o") if pt.get("o") is not None else prev_close


            parsed_records.append({

                "symbol": symbol,

                "date": str(dt),

                "open": float(open_price),

                "high": float(high) if high is not None else float(close),

                "low": float(low) if low is not None else float(close),

                "close": float(close),

                "volume": int(volume)

            })


        return pd.DataFrame(parsed_records)



    def parse_csv_data(self, symbol: str, df: pd.DataFrame) -> pd.DataFrame:

        """
        Ensure fallback CSV data conforms to the standard schema columns.
        """

        required_cols = ["date", "open", "high", "low", "close", "volume"]

        for col in required_cols:

            if col not in df.columns:

                raise ValueError(f"CSV missing required column: {col}")


        formatted_df = df[required_cols].copy()

        formatted_df["symbol"] = symbol


        cols_order = ["symbol", "date", "open", "high", "low", "close", "volume"]

        return formatted_df[cols_order]
