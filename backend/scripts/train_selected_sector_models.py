import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.forecasting.prediction_service import PredictionService

SELECTED_STOCKS = [
    "COMB", "JKH", "DIST", "SAMP", "HNB", "LOLC", "AAIC", "CARG", 
    "AHUN", "HAYL", "HEMA", "ACL", "TKYO", "LIOC", "LWL", "EXPO", 
    "UML", "ODEL", "RICH", "OSEA", "KGAL", "MADU", "SEYB", "NDB", 
    "SLTL", "DIAL"
]

def train_all_selected():
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print(f" Pre-training Models for {len(SELECTED_STOCKS)} Selected Sector Stocks")
    print("=" * 60)

    service = PredictionService()
    results = []

    for sym in SELECTED_STOCKS:
        print(f"\n>> Training models for {sym} ...")
        try:
            res = service.get_predictions(sym, horizon=30)
            data_points = res.get("data_points_used", 0)
            best_model = res.get("best_model", "N/A")
            current_price = res.get("current_price")
            best_pred = res.get("best_prediction")
            print(f"   [SUCCESS] Points: {data_points} | Best Model: {best_model} | Current: {current_price} | 30d Forecast: {best_pred}")
            results.append((sym, data_points, best_model, current_price, best_pred))
        except Exception as e:
            print(f"   [ERROR] Failed to train {sym}: {e}")

    print("\n" + "=" * 60)
    print(" Summary of Model Pre-training Across Selected Sector Stocks")
    print("=" * 60)
    for sym, pts, model_name, cur_p, pred_p in results:
        print(f"{sym:<8} | Pts: {pts:<5} | Best Model: {model_name:<10} | Price: {cur_p} -> 30d Pred: {pred_p}")

if __name__ == "__main__":
    train_all_selected()
