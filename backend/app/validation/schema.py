import pandas as pd
from datetime import datetime, timezone


def validate_columns_and_types(df: pd.DataFrame, expected_cols: dict) -> list[str]:
    errors = []
    for col in expected_cols:
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
    return errors


def validate_numeric_ranges(df: pd.DataFrame, numeric_cols: list[str]) -> list[str]:
    errors = []
    for col in numeric_cols:
        if col in df.columns:
            try:
                # Convert to numeric to ensure clean comparison
                vals = pd.to_numeric(df[col])
                negatives = df[vals < 0]
                if not negatives.empty:
                    errors.append(f"Column '{col}' contains {len(negatives)} negative values.")
            except Exception as e:
                errors.append(f"Column '{col}' has non-numeric values: {str(e)}")
    return errors


def validate_dates(df: pd.DataFrame, date_col: str = "date") -> list[str]:
    errors = []
    if date_col in df.columns:
        try:
            dates = pd.to_datetime(df[date_col])
            # Handle tz-naive and tz-aware comparison safely
            now = datetime.now(timezone.utc)
            future_dates = df[dates.apply(lambda d: d.tz_localize(timezone.utc) if d.tzinfo is None else d) > now]
            if not future_dates.empty:
                errors.append(f"Future dates detected in '{date_col}': {len(future_dates)} rows.")
        except Exception as e:
            errors.append(f"Failed to parse or validate dates in column '{date_col}': {str(e)}")
    return errors
