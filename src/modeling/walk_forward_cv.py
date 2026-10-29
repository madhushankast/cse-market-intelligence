"""
Purged & Embargoed Walk-Forward Time-Series Cross-Validation Engine
-------------------------------------------------------------------
Prevents informational and multi-step label leakage when validating forward return models.
Based on Marcos López de Prado (2018), 'Advances in Financial Machine Learning'.
"""

from __future__ import annotations

import logging
from typing import Generator, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PurgedWalkForwardCV:
    """
    Time-series Walk-Forward Cross-Validation with Purging and Embargo.

    Guarantees:
      1. Forward target overlap purging: When predicting h-step forward returns (h=30),
         training samples within the last 30 days prior to validation are purged to prevent
         forward price leakage into the evaluation window.
      2. Serial autocorrelation embargo: An explicit embargo gap separates the end of the
         training window and the start of the validation window.
         Condition: max(train_indices) + embargo_period <= min(test_indices).

    Parameters:
      n_splits: Number of walk-forward evaluation folds (default 5).
      embargo_period: Embargo buffer gap in trading days (default 30).
      min_train_size: Minimum number of trading days required in the initial train fold (default 250).
      test_size: Number of trading days in each sequential test window (default 60).
    """

    def __init__(
        self,
        n_splits: int = 5,
        embargo_period: int = 30,
        min_train_size: int = 250,
        test_size: int = 60,
        # Backwards compatible alias parameters
        embargo_window: Optional[int] = None,
        test_window: Optional[int] = None,
    ):
        self.n_splits = n_splits
        self.embargo_period = embargo_window if embargo_window is not None else embargo_period
        self.min_train_size = min_train_size
        self.test_size = test_window if test_window is not None else test_size

    # Alias properties
    @property
    def embargo_window(self) -> int:
        return self.embargo_period

    @property
    def test_window(self) -> int:
        return self.test_size

    def split(
        self,
        df: Union[pd.DataFrame, np.ndarray, int],
        date_col: Optional[str] = "date",
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Yields (train_indices, test_indices) tuples across chronological walk-forward splits.
        Guarantees: max(train_indices) + self.embargo_period <= min(test_indices).
        """
        if isinstance(df, int):
            n_samples = df
        else:
            n_samples = len(df)

        required_min_samples = self.min_train_size + self.embargo_period + self.test_size
        if n_samples < required_min_samples:
            raise ValueError(
                f"Insufficient data length ({n_samples}) for min_train_size={self.min_train_size}, "
                f"embargo={self.embargo_period}, test_size={self.test_size} (requires >= {required_min_samples})"
            )

        # Calculate stride between successive test folds across available evaluation horizon
        available_eval_space = n_samples - self.min_train_size - self.embargo_period
        step = max(self.test_size, available_eval_space // self.n_splits)

        for fold in range(self.n_splits):
            # Test window starts sequentially
            test_start = n_samples - (self.n_splits - fold) * step
            test_end = min(test_start + self.test_size, n_samples)

            if test_start < self.min_train_size + self.embargo_period:
                continue

            # Enforce strictly: max(train) + embargo_period <= test_start
            train_end = test_start - self.embargo_period
            train_indices = np.arange(0, train_end)
            test_indices = np.arange(test_start, test_end)

            if len(train_indices) < self.min_train_size or len(test_indices) == 0:
                continue

            # Verify embargo condition
            assert train_indices[-1] + self.embargo_period <= test_indices[0], (
                f"Embargo violation: train_end={train_indices[-1]}, test_start={test_indices[0]}, embargo={self.embargo_period}"
            )

            yield train_indices, test_indices

    def get_split_dates(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
    ) -> List[dict]:
        """
        Returns human-readable date ranges and sample counts for each cross-validation fold.
        """
        dates = pd.to_datetime(df[date_col]).values
        splits_info = []

        for fold_idx, (train_idx, test_idx) in enumerate(self.split(df, date_col=date_col)):
            embargo_start_idx = train_idx[-1] + 1
            embargo_end_idx = test_idx[0] - 1

            splits_info.append({
                "fold": fold_idx + 1,
                "train_start": str(pd.to_datetime(dates[train_idx[0]]).date()),
                "train_end": str(pd.to_datetime(dates[train_idx[-1]]).date()),
                "train_size": len(train_idx),
                "embargo_gap_days": self.embargo_period,
                "embargo_start": str(pd.to_datetime(dates[embargo_start_idx]).date()),
                "embargo_end": str(pd.to_datetime(dates[embargo_end_idx]).date()) if embargo_end_idx >= embargo_start_idx else "N/A",
                "test_start": str(pd.to_datetime(dates[test_idx[0]]).date()),
                "test_end": str(pd.to_datetime(dates[test_idx[-1]]).date()),
                "test_size": len(test_idx),
            })
        return splits_info

    def log_split_summary(self, df: pd.DataFrame, date_col: str = "date") -> None:
        """Prints a structured summary of cross-validation folds."""
        splits = self.get_split_dates(df, date_col=date_col)
        print(f"PurgedWalkForwardCV (Folds: {len(splits)}, Embargo: {self.embargo_period}d, Test Size: {self.test_size}d)")
        for s in splits:
            print(f"  Fold {s['fold']}: Train [{s['train_start']} -> {s['train_end']}] ({s['train_size']} bars) | "
                  f"Embargo Gap ({s['embargo_gap_days']}d) | "
                  f"Test [{s['test_start']} -> {s['test_end']}] ({s['test_size']} bars)")
