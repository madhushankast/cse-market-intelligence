import sys, os
# Make sure 'app' package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
warnings.filterwarnings('ignore')
import logging
logging.disable(logging.CRITICAL)

from app.forecasting.prediction_service import PredictionService
svc = PredictionService()

for sym in ['COMB', 'JKH', 'DIST', 'SAMP', 'HNB']:
    try:
        result = svc.get_predictions(sym, horizon=7)
        fv = result.get('forecast_values', [])
        pct = [round(v*100, 2) for v in fv] if fv else []
        print(sym + " OK")
        print("  current_price   : " + str(result.get('current_price')))
        print("  best_model      : " + str(result.get('best_model')))
        print("  data_points_used: " + str(result.get('data_points_used')))
        print("  forecast_pct    : " + str(pct))
        print()
    except Exception as e:
        print(sym + " ERROR: " + str(e))
        print()
