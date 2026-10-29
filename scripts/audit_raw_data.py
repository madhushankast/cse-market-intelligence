"""
Historical Data Diagnostic & Audit Script
-----------------------------------------
Scans raw files in data/raw/, inspects schemas, evaluates date formatting,
checks for numerical formatting anomalies (commas, string types, missing values),
and audits for the presence of broad market indices (ASPI, S&P SL20).
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import pandas as pd

# Safe terminal encoding on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def audit_file(file_path: Path) -> Dict[str, Any]:
    """Audits an individual CSV or Parquet file."""
    info: Dict[str, Any] = {
        "file_name": file_path.name,
        "relative_path": str(file_path),
        "extension": file_path.suffix.lower(),
        "size_kb": round(file_path.stat().st_size / 1024, 2),
        "row_count": 0,
        "col_count": 0,
        "columns": [],
        "sample_rows": [],
        "date_column": None,
        "date_min": None,
        "date_max": None,
        "date_format_sample": None,
        "has_commas_in_numeric": False,
        "comma_columns": [],
        "null_counts": {},
        "symbols_detected": set(),
        "is_index_detected": False,
    }

    try:
        if file_path.suffix.lower() == ".csv":
            df_head = pd.read_csv(file_path, nrows=50)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                info["row_count"] = max(0, sum(1 for _ in f) - 1)
            df = df_head
        elif file_path.suffix.lower() == ".parquet":
            df = pd.read_parquet(file_path)
            info["row_count"] = len(df)
        else:
            return info

        info["col_count"] = len(df.columns)
        info["columns"] = list(df.columns)
        info["sample_rows"] = df.head(2).to_dict(orient="records")

        # Detect date column
        date_candidates = [c for c in df.columns if any(k in c.lower() for k in ["date", "time", "day"])]
        if date_candidates:
            date_col = date_candidates[0]
            info["date_column"] = date_col
            sample_val = str(df[date_col].iloc[0]) if len(df) > 0 else ""
            info["date_format_sample"] = sample_val
            try:
                dt_series = pd.to_datetime(df[date_col], errors="coerce")
                info["date_min"] = str(dt_series.min().date()) if pd.notna(dt_series.min()) else None
                info["date_max"] = str(dt_series.max().date()) if pd.notna(dt_series.max()) else None
            except Exception:
                pass

        # Check for commas or quotes in numeric fields
        comma_cols = []
        for col in df.columns:
            if df[col].dtype == object:
                sample_strings = df[col].dropna().astype(str)
                if sample_strings.str.contains(r"\d,\d").any():
                    comma_cols.append(col)
        if comma_cols:
            info["has_commas_in_numeric"] = True
            info["comma_columns"] = comma_cols

        # Null value checks
        info["null_counts"] = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}

        # Symbol / Index detection
        symbol_candidates = [c for c in df.columns if any(k in c.lower() for k in ["symbol", "ticker", "company", "short name"])]
        for sym_col in symbol_candidates:
            unique_syms = df[sym_col].dropna().astype(str).unique()
            info["symbols_detected"].update(unique_syms)

        # Check for ASPI or S&P SL20
        all_text = " ".join([str(c) for c in df.columns] + [str(s) for s in info["symbols_detected"]] + [file_path.name]).upper()
        if any(idx in all_text for idx in ["ASPI", "S&P", "SL20", "INDEX"]):
            info["is_index_detected"] = True

    except Exception as exc:
        info["error"] = str(exc)

    return info


def run_audit(raw_dir_path: str = "data/raw") -> None:
    raw_path = Path(raw_dir_path)
    if not raw_path.exists():
        print(f"[!] Error: Raw data directory not found at: {raw_path.resolve()}")
        return

    print("=" * 80)
    print(f"[AUDIT] CSE HISTORICAL DATA AUDIT: Scanning '{raw_path.resolve()}'")
    print("=" * 80)

    all_files = sorted(list(raw_path.rglob("*.csv")) + list(raw_path.rglob("*.parquet")))
    print(f"\n[+] Total Historical Files Found: {len(all_files)}")

    if not all_files:
        print("[!] No .csv or .parquet files detected in directory.")
        return

    results = []
    aspi_detected_files = []
    comma_files = []

    for f in all_files:
        audit = audit_file(f)
        results.append(audit)
        if audit.get("is_index_detected"):
            aspi_detected_files.append(audit["file_name"])
        if audit.get("has_commas_in_numeric"):
            comma_files.append((audit["file_name"], audit["comma_columns"]))

    # Summary table by subfolder
    subfolders: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        p = Path(r["relative_path"])
        sub = p.parent.name or "root"
        subfolders.setdefault(sub, []).append(r)

    print("\n--- 1. DIRECTORY BREAKDOWN ---")
    for sub, files in subfolders.items():
        total_rows = sum(f["row_count"] for f in files)
        print(f"[*] [{sub}] : {len(files)} files (~{total_rows:,} total records)")

    print("\n--- 2. DETAILED SAMPLE AUDIT (INDIVIDUAL STOCKS & YEARLY ARCHIVES) ---")
    for r in results[:4]:
        print(f"\n[FILE] {r['file_name']} ({r['size_kb']} KB, ~{r['row_count']:,} rows)")
        print(f"   Columns ({r['col_count']}): {r['columns']}")
        print(f"   Date Column: {r['date_column']} (Sample: '{r['date_format_sample']}', Range: {r['date_min']} to {r['date_max']})")
        if r["has_commas_in_numeric"]:
            print(f"   [!] Numbers formatted with commas in columns: {r['comma_columns']}")
        if r["null_counts"]:
            print(f"   [!] Missing values detected: {r['null_counts']}")
        print(f"   Sample Row 1: {r['sample_rows'][0] if r['sample_rows'] else 'N/A'}")
        if len(r['sample_rows']) > 1:
            print(f"   Sample Row 2: {r['sample_rows'][1]}")

    # Inspect a yearly file specifically if present
    yearly_files = [r for r in results if "202" in r["file_name"]]
    if yearly_files:
        yr = yearly_files[0]
        print(f"\n[FILE - YEARLY ARCHIVE] {yr['file_name']} ({yr['size_kb']} KB, ~{yr['row_count']:,} rows)")
        print(f"   Columns: {yr['columns']}")
        print(f"   Date Format Sample: '{yr['date_format_sample']}'")
        print(f"   Commas in numeric: {yr['comma_columns']}")
        print(f"   Sample Row 1: {yr['sample_rows'][0] if yr['sample_rows'] else 'N/A'}")

    print("\n--- 3. DATA QUALITY & FORMATTING VERIFICATION ---")
    if comma_files:
        print(f"[!] Files requiring string sanitization (commas in numbers like '1,250.00'): {len(comma_files)} files")
        for fname, cols in comma_files[:3]:
            print(f"   - {fname}: columns {cols}")
    else:
        print("[OK] No comma-formatted numeric strings detected.")

    print("\n--- 4. BROAD MARKET INDEX VERIFICATION (ASPI & S&P SL20) ---")
    if aspi_detected_files:
        print(f"[OK] Market Index occurrences detected in: {aspi_detected_files}")
    else:
        print("[INFO] No dedicated ASPI or S&P SL20 index files detected in data/raw/.")
        print("       Historical files consist of individual equity tickers (e.g. JKH, COMB, SAMP) and yearly bulk transaction dumps.")

    print("\n" + "=" * 80)
    print("[DONE] Audit complete.")
    print("=" * 80)


if __name__ == "__main__":
    run_audit()
