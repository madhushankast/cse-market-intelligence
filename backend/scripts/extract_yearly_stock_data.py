import os
import glob
import re
import pandas as pd
import numpy as np

def clean_numeric(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def parse_sub_type(sub_type):
    if pd.isna(sub_type):
        return "0000"
    st = str(sub_type).strip()
    if st.isdigit():
        return st.zfill(4)
    return st

SELECTED_STOCKS = [
    "COMB", "JKH", "DIST", "SAMP", "HNB", "LOLC", "AAIC", "CARG", 
    "AHUN", "HAYL", "HEMA", "ACL", "TKYO", "LIOC", "LWL", "EXPO", 
    "UML", "ODEL", "RICH", "OSEA", "KGAL", "MADU", "SEYB", "NDB", 
    "SLTL", "DIAL"
]

def extract_yearly_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yearly_dir = os.path.join(base_dir, "data", "raw", "yearly")
    cse_dir = os.path.join(base_dir, "data", "raw", "cse")
    os.makedirs(cse_dir, exist_ok=True)

    # Clean existing non-selected CSV files from cse_dir
    existing_files = glob.glob(os.path.join(cse_dir, "*.csv"))
    for ef in existing_files:
        stem = os.path.splitext(os.path.basename(ef))[0]
        if stem not in SELECTED_STOCKS:
            try:
                os.remove(ef)
            except Exception:
                pass

    yearly_files = sorted(glob.glob(os.path.join(yearly_dir, "*.csv")))
    print(f"Found {len(yearly_files)} yearly files in {yearly_dir}")

    all_dfs = []

    for file_path in yearly_files:
        print(f"Processing {os.path.basename(file_path)}...")
        df = pd.read_csv(file_path, skipinitialspace=True, dtype=str)
        df.columns = [col.strip() for col in df.columns]
        
        col_company = [c for c in df.columns if "COMPANY ID" in c or "COMPANY" in c][0]
        col_main_type = [c for c in df.columns if "MAIN TYPE" in c][0]
        col_sub_type = [c for c in df.columns if "SUB TYPE" in c][0]
        col_date = [c for c in df.columns if "DATE" in c][0]
        col_high = [c for c in df.columns if "HIGH" in c][0]
        col_low = [c for c in df.columns if "LOW" in c][0]
        col_close = [c for c in df.columns if "CLOSE" in c][0]
        col_open = [c for c in df.columns if "OPEN" in c][0]
        col_volume = [c for c in df.columns if "SHARE VOLUME" in c][0]

        company_ids = df[col_company].str.strip()
        
        # Filter ONLY for selected sector stocks
        mask_selected = company_ids.isin(SELECTED_STOCKS)
        if not mask_selected.any():
            continue

        df_sel = df[mask_selected].copy()
        company_ids = df_sel[col_company].str.strip()
        
        # Standardize symbol format to COMPANY_ID.N0000 (primary voting stock symbol)
        symbols = company_ids + ".N0000"

        dates = pd.to_datetime(df_sel[col_date].str.strip(), format="mixed", dayfirst=True, errors="coerce")

        close_prices = df_sel[col_close].apply(clean_numeric)
        open_prices = df_sel[col_open].apply(clean_numeric).fillna(close_prices)
        high_prices = df_sel[col_high].apply(clean_numeric).fillna(np.maximum(open_prices, close_prices))
        low_prices = df_sel[col_low].apply(clean_numeric).fillna(np.minimum(open_prices, close_prices))
        volumes = df_sel[col_volume].apply(clean_numeric).fillna(0).astype(int)

        valid_mask = dates.notna() & close_prices.notna() & (company_ids != "") & (company_ids != "nan")

        extracted_df = pd.DataFrame({
            "company_id": company_ids[valid_mask],
            "symbol": symbols[valid_mask],
            "date": dates[valid_mask].dt.strftime("%Y-%m-%d"),
            "open": open_prices[valid_mask].round(4),
            "high": high_prices[valid_mask].round(4),
            "low": low_prices[valid_mask].round(4),
            "close": close_prices[valid_mask].round(4),
            "volume": volumes[valid_mask]
        })

        all_dfs.append(extracted_df)

    full_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Total extracted rows across 5 years for selected sector stocks: {len(full_df)}")

    grouped = full_df.groupby("company_id")
    processed_count = 0

    for company_id, comp_df in grouped:
        csv_path = os.path.join(cse_dir, f"{company_id}.csv")
        
        if os.path.exists(csv_path):
            try:
                existing_df = pd.read_csv(csv_path)
                combined = pd.concat([existing_df, comp_df[["symbol", "date", "open", "high", "low", "close", "volume"]]], ignore_index=True)
            except Exception:
                combined = comp_df[["symbol", "date", "open", "high", "low", "close", "volume"]]
        else:
            combined = comp_df[["symbol", "date", "open", "high", "low", "close", "volume"]]

        combined = combined.drop_duplicates(subset=["date"], keep="last")
        combined = combined.sort_values("date").reset_index(drop=True)

        combined.to_csv(csv_path, index=False)
        processed_count += 1

    print(f"Successfully updated/created CSV files for {processed_count} selected sector companies in {cse_dir}")

if __name__ == "__main__":
    extract_yearly_data()
