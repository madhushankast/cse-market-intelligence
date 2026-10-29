"""
Batch Training & Cross-Validation Benchmarking Script
------------------------------------------------------
Trains and evaluates Multi-Quantile LightGBM models against Level 0 (Naive)
and Level 1 (Prophet) benchmarks across all 26 CSE equities using Purged Walk-Forward CV.
Serializes final models into models/{symbol}/ and outputs reports/cv_benchmark_summary.csv.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
import time
from typing import List, Optional

# Force UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.modeling.train_lightgbm import QuantileLightGBMTrainer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train_all_models")


def get_available_symbols(processed_dir: Path) -> List[str]:
    """Finds all processed equity parquet files, excluding benchmark index."""
    files = sorted(processed_dir.glob("*.parquet"))
    symbols = [f.stem for f in files if f.stem != "ASPI"]
    return symbols


def run_batch_training(
    processed_dir: Path = Path("data/processed"),
    models_dir: Path = Path("models"),
    reports_dir: Path = Path("reports"),
    symbols_filter: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Executes cross-validation and final model training across equities.
    """
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    all_symbols = get_available_symbols(processed_dir)
    target_symbols = [s for s in all_symbols if s in symbols_filter] if symbols_filter else all_symbols

    logger.info("Found %d equities to process for Phase 3 Model Training.", len(target_symbols))

    summary_records = []
    start_time = time.time()

    for idx, symbol in enumerate(target_symbols, 1):
        print(f"\n[{idx:02d}/{len(target_symbols):02d}] Processing {symbol}...")
        stock_start = time.time()

        try:
            trainer = QuantileLightGBMTrainer()
            feature_df, feature_names = trainer.prepare_data(
                symbol=symbol,
                data_dir=processed_dir,
                aspi_path=processed_dir / "ASPI.parquet",
            )

            # 1. Purged Walk-Forward Cross-Validation
            cv_metrics = trainer.evaluate_walk_forward(feature_df, feature_cols=feature_names)

            # 2. Retrain final model on all valid data
            trainer.fit_final_models(feature_df, feature_cols=feature_names)

            # 3. Persist model artifacts
            saved_dir = trainer.save_artifacts(output_dir=models_dir, symbol=symbol)

            stock_elapsed = time.time() - stock_start
            print(
                f"    [+] LGB Dir Acc: {cv_metrics['lgb_directional_accuracy']:.1f}% "
                f"(vs Naive: {cv_metrics['naive_directional_accuracy']:.1f}% | Prophet: {cv_metrics['prophet_directional_accuracy']:.1f}%) | "
                f"RMSE: {cv_metrics['lgb_rmse']:.4f} | Pinball: {cv_metrics['lgb_mean_pinball']:.4f} | "
                f"Cov: {cv_metrics['lgb_coverage_80']:.1f}% [{stock_elapsed:.1f}s]"
            )

            record = {
                "symbol": symbol,
                "n_folds": cv_metrics["n_folds"],
                "total_test_samples": cv_metrics["total_test_samples"],
                "lgb_dir_acc": cv_metrics["lgb_directional_accuracy"],
                "naive_dir_acc": cv_metrics["naive_directional_accuracy"],
                "prophet_dir_acc": cv_metrics["prophet_directional_accuracy"],
                "dir_acc_edge_vs_naive": round(cv_metrics["lgb_directional_accuracy"] - 50.0, 2),
                "lgb_rmse": cv_metrics["lgb_rmse"],
                "naive_rmse": cv_metrics["naive_rmse"],
                "prophet_rmse": cv_metrics["prophet_rmse"],
                "lgb_mae": cv_metrics["lgb_mae"],
                "naive_mae": cv_metrics["naive_mae"],
                "prophet_mae": cv_metrics["prophet_mae"],
                "lgb_mean_pinball": cv_metrics["lgb_mean_pinball"],
                "lgb_pinball_p10": cv_metrics["lgb_pinball_p10"],
                "lgb_pinball_p50": cv_metrics["lgb_pinball_p50"],
                "lgb_pinball_p90": cv_metrics["lgb_pinball_p90"],
                "lgb_coverage_80": cv_metrics["lgb_coverage_80"],
            }
            summary_records.append(record)

        except Exception as exc:
            logger.error("Failed training for symbol %s: %s", symbol, exc, exc_info=True)

    total_elapsed = time.time() - start_time
    summary_df = pd.DataFrame(summary_records)

    # Save summary report
    report_file = reports_dir / "cv_benchmark_summary.csv"
    summary_df.to_csv(report_file, index=False)
    logger.info("Saved executive summary report to %s", report_file)

    # Print Executive Summary Table
    print("\n" + "=" * 95)
    print("           CSE MARKET INTELLIGENCE: PHASE 3 BENCHMARK EXECUTIVE SUMMARY")
    print("=" * 95)
    print(
        f"{'Symbol':<12} | {'LGB Dir %':<10} | {'Naive Dir %':<11} | {'LGB Edge':<9} | "
        f"{'LGB RMSE':<9} | {'Naive RMSE':<10} | {'Mean Pinball':<12} | {'Cov 80%':<8}"
    )
    print("-" * 95)
    for _, row in summary_df.iterrows():
        edge_sign = "+" if row["dir_acc_edge_vs_naive"] >= 0 else ""
        print(
            f"{row['symbol']:<12} | {row['lgb_dir_acc']:<10.2f} | {row['naive_dir_acc']:<11.2f} | "
            f"{edge_sign}{row['dir_acc_edge_vs_naive']:<8.2f}% | {row['lgb_rmse']:<9.4f} | "
            f"{row['naive_rmse']:<10.4f} | {row['lgb_mean_pinball']:<12.4f} | {row['lgb_coverage_80']:<7.1f}%"
        )
    print("=" * 95)

    # Aggregates across market
    if not summary_df.empty:
        avg_lgb_acc = summary_df["lgb_dir_acc"].mean()
        avg_prophet_acc = summary_df["prophet_dir_acc"].mean()
        avg_edge = summary_df["dir_acc_edge_vs_naive"].mean()
        avg_lgb_rmse = summary_df["lgb_rmse"].mean()
        avg_naive_rmse = summary_df["naive_rmse"].mean()
        avg_pinball = summary_df["lgb_mean_pinball"].mean()
        avg_coverage = summary_df["lgb_coverage_80"].mean()

        print(
            f"MACRO MARKET AVERAGE (26 EQUITIES):\n"
            f"  - LightGBM Directional Accuracy: {avg_lgb_acc:.2f}% (Edge vs Naive 50%: +{avg_edge:.2f}%)\n"
            f"  - FB Prophet Baseline Directional Accuracy: {avg_prophet_acc:.2f}%\n"
            f"  - LightGBM RMSE: {avg_lgb_rmse:.4f} vs Naive Persistence RMSE: {avg_naive_rmse:.4f}\n"
            f"  - Average Pinball Loss: {avg_pinball:.4f}\n"
            f"  - Empirical 80% Confidence Interval Coverage: {avg_coverage:.2f}%\n"
            f"  - Total Elapsed Training Time: {total_elapsed:.1f}s"
        )
        print("=" * 95 + "\n")

    return summary_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch train LightGBM quantile models across CSE stocks.")
    parser.add_argument("--data-dir", type=str, default="data/processed", help="Directory with processed parquet files.")
    parser.add_argument("--models-dir", type=str, default="models", help="Directory to persist trained models.")
    parser.add_argument("--reports-dir", type=str, default="reports", help="Directory to save metric reports.")
    parser.add_argument("--symbols", nargs="*", default=None, help="Optional subset of symbols to evaluate.")

    args = parser.parse_args()

    run_batch_training(
        processed_dir=Path(args.data_dir),
        models_dir=Path(args.models_dir),
        reports_dir=Path(args.reports_dir),
        symbols_filter=args.symbols,
    )
