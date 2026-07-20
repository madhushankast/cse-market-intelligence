import pandas as pd
from app.validation.schema import validate_columns_and_types, validate_numeric_ranges, validate_dates
from app.validation.duplicates import check_duplicates
from app.validation.missing import check_missing_values, check_missing_trading_days


class DataValidator:

    @staticmethod
    def validate_stock_data(df: pd.DataFrame) -> dict:
        if df.empty:
            return {"is_valid": False, "errors": ["DataFrame is empty."]}

        expected_cols = ["symbol", "date", "open", "high", "low", "close", "volume"]
        numeric_cols = ["open", "high", "low", "close", "volume"]

        errors = []
        errors.extend(validate_columns_and_types(df, expected_cols))
        errors.extend(validate_numeric_ranges(df, numeric_cols))
        errors.extend(validate_dates(df, "date"))
        errors.extend(check_duplicates(df, ["symbol", "date"]))
        errors.extend(check_missing_values(df, expected_cols))
        errors.extend(check_missing_trading_days(df, "symbol", "date", 10))

        # Check for future dates
        df_dates = pd.to_datetime(df["date"])
        if (df_dates > pd.Timestamp.now()).any():
            errors.append("Data contains future dates.")

        # Outlier checks: daily return > 35%
        if "close" in df.columns and "open" in df.columns:
            returns = (df["close"] - df["open"]) / df["open"]
            if (returns.abs() > 0.35).any():
                errors.append("Outlier detected: Daily returns exceeded 35%.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate_cbsl_data(df: pd.DataFrame) -> dict:
        if df.empty:
            return {"is_valid": False, "errors": ["DataFrame is empty."]}

        expected_cols = ["date", "inflation", "usd_lkr", "interest_rate"]
        numeric_cols = ["inflation", "usd_lkr", "interest_rate"]

        errors = []
        errors.extend(validate_columns_and_types(df, expected_cols))
        errors.extend(validate_numeric_ranges(df, numeric_cols))
        errors.extend(validate_dates(df, "date"))
        errors.extend(check_duplicates(df, ["date"]))
        errors.extend(check_missing_values(df, expected_cols))

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def validate_trends_data(df: pd.DataFrame) -> dict:
        if df.empty:
            return {"is_valid": False, "errors": ["DataFrame is empty."]}

        expected_cols = ["date", "trend_score"]
        numeric_cols = ["trend_score"]

        errors = []
        errors.extend(validate_columns_and_types(df, expected_cols))
        errors.extend(validate_numeric_ranges(df, numeric_cols))
        errors.extend(validate_dates(df, "date"))
        errors.extend(check_duplicates(df, ["date"]))
        errors.extend(check_missing_values(df, expected_cols))

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
