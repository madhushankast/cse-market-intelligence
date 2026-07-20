import pandas as pd
import numpy as np


def align_to_trading_days(
    data: pd.DataFrame,
    trading_days: pd.DataFrame,
    val_col: str,
    prefix: str,
    date_col: str = "date"
) -> pd.DataFrame:
    """
    Aligns an alternative or macroeconomic series to the stock trading calendar,
    forward-filling values while explicitly tracking 'days_since_update' to prevent leakage.
    
    Args:
        data:         DataFrame containing date and value columns.
        trading_days: DataFrame containing date column (stock calendar).
        val_col:      Name of the value column in `data` (e.g. "inflation").
        prefix:       Prefix for the new age feature (e.g. "inflation").
        date_col:     Date column name.
        
    Returns:
        DataFrame aligned to trading_days with value and days_since_update.
    """
    data = data.copy()
    trading_days = trading_days.copy()
    
    # Normalize dates
    data[date_col] = pd.to_datetime(data[date_col])
    trading_days[date_col] = pd.to_datetime(trading_days[date_col])
    
    # Sort
    data = data.sort_values(date_col).reset_index(drop=True)
    trading_days = trading_days.sort_values(date_col).reset_index(drop=True)
    
    # Select date and val_col
    data = data[[date_col, val_col]].dropna(subset=[val_col])
    
    # Left merge trading days with data
    merged = pd.merge(trading_days, data, on=date_col, how="left")
    
    # Calculate days since last update
    is_updated = merged[val_col].notna()
    update_dates = merged.loc[is_updated, date_col]
    
    if update_dates.empty:
        # Fallback if no data present
        merged[val_col] = 0.0
        merged[f"{prefix}_age"] = 999
        return merged
        
    updates_df = pd.DataFrame({date_col: update_dates, "last_update_date": update_dates})
    merged = pd.merge_asof(merged, updates_df, on=date_col, direction="backward")
    
    # Calculate age in days
    merged[f"{prefix}_age"] = (merged[date_col] - merged["last_update_date"]).dt.days
    merged[f"{prefix}_age"] = merged[f"{prefix}_age"].fillna(999).astype(int)
    
    # Forward-fill value and backward-fill remaining leading NaNs
    merged[val_col] = merged[val_col].ffill().bfill()
    
    return merged.drop(columns=["last_update_date"])
