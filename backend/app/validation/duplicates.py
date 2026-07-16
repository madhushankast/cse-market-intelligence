import pandas as pd


def check_duplicates(df: pd.DataFrame, subset: list[str]) -> list[str]:
    errors = []
    if all(col in df.columns for col in subset):
        dupes = df[df.duplicated(subset=subset, keep=False)]
        if not dupes.empty:
            errors.append(f"Duplicate records found for subset {subset}: {len(dupes)} rows.")
    return errors
