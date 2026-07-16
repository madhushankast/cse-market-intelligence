import pandas as pd


def check_missing_values(df: pd.DataFrame, columns: list[str]) -> list[str]:
    errors = []
    for col in columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' contains {null_count} missing (NaN/None) values.")
    return errors


def check_missing_trading_days(df: pd.DataFrame, symbol_col: str = "symbol", date_col: str = "date", threshold_days: int = 10) -> list[str]:
    errors = []
    if symbol_col in df.columns and date_col in df.columns:
        df_sorted = df.copy()
        try:
            df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
            df_sorted.sort_values([symbol_col, date_col], inplace=True)

            for symbol, group in df_sorted.groupby(symbol_col):
                dates = group[date_col].values
                if len(dates) > 1:
                    diffs = pd.Series(dates).diff()
                    large_gaps = diffs[diffs > pd.Timedelta(days=threshold_days)]
                    if not large_gaps.empty:
                        errors.append(f"Symbol '{symbol}' has {len(large_gaps)} gap(s) larger than {threshold_days} days in sequence.")
        except Exception as e:
            errors.append(f"Failed to check missing trading days: {str(e)}")
    return errors
