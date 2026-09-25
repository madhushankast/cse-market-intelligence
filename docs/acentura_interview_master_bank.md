# Acentura ML Internship Technical Interview Master Codebase Question Bank

> **Target Role:** AIML / Machine Learning Intern at Acentura  
> **Source of Truth:** User's 4 local codebases:
> 1. `c:\Ongoing Projects\CSE`
> 2. `c:\Ongoing Projects\Flood Prediction\ml-opsidian-genesis`
> 3. `c:\Ongoing Projects\market_basket_analysis`
> 4. `c:\Ongoing Projects\Machine Learning Specialization` (`1 Linear Regression` & `2 Logistic Regression for Classification`)

---

# TABLE OF CONTENTS
- [PART 1 — UNDERSTAND EACH CODEBASE](#part-1--understand-each-codebase)
- [PART 2 — FILE-BY-FILE QUESTIONS](#part-2--file-by-file-questions)
- [PART 3 — LINE-BY-LINE & CODE-SNIPPET QUESTIONS](#part-3--line-by-line--code-snippet-questions)
- [PART 4 — "WHY DID YOU DO THIS?" DECISION QUESTIONS](#part-4--why-did-you-do-this-decision-questions)
- [PART 5 — REALISTIC DEBUGGING SCENARIOS](#part-5--realistic-debugging-scenarios)
- [PART 6 — "CHANGE THIS CODE" CODING PROBLEMS](#part-6--change-this-code-coding-problems)
- [PART 7 — EXECUTION TRACES](#part-7--execution-traces)
- [PART 8 — MODEL-SPECIFIC CODE DEEP-DIVES](#part-8--model-specific-code-deep-dives)
- [PART 9 — COMPREHENSIVE DATA LEAKAGE AUDIT](#part-9--comprehensive-data-leakage-audit)
- [PART 10 — PERFORMANCE, MEMORY & SCALING](#part-10--performance-memory--scaling)
- [PART 11 — PRODUCTION & DEPLOYMENT ARCHITECTURE](#part-11--production--deployment-architecture)
- [PART 12 — INTERVIEWER FOLLOW-UP CHAINS (10 PER PROJECT)](#part-12--interviewer-follow-up-chains-10-per-project)
- [PART 13 — HARD TECHNICAL QUESTIONS](#part-13--hard-technical-questions)
- [PART 14 — PROJECT MASTERY CHECKLISTS](#part-14--project-mastery-checklists)
- [FINAL OUTPUT 1 — TOP 50 MUST-KNOW CODEBASE QUESTIONS](#final-output-1--top-50-must-know-codebase-questions)
- [FINAL OUTPUT 2 — TOP 30 DEBUGGING PROBLEMS](#final-output-2--top-30-debugging-problems)
- [FINAL OUTPUT 3 — TOP 20 "WHY IMPLEMENTED THIS WAY?" QUESTIONS](#final-output-3--top-20-why-implemented-this-way-questions)
- [FINAL OUTPUT 4 — TOP 20 CODE MODIFICATION TASKS](#final-output-4--top-20-code-modification-tasks)
- [FINAL OUTPUT 5 — TOP 20 HARDEST FOLLOW-UP QUESTIONS](#final-output-5--top-20-hardest-follow-up-questions)
- [FINAL OUTPUT 6 — 1-DAY REVISION CHECKLIST](#final-output-6--1-day-revision-checklist)

---

# PART 1 — UNDERSTAND EACH CODEBASE

## 1. Colombo Stock Exchange (CSE) Market Intelligence Platform
- **Purpose**: Full-stack financial intelligence and forecasting platform for 26 Sri Lankan blue-chip equities. Integrates daily OHLCV prices with macroeconomic indicators (CBSL CCPI inflation, USD/LKR, policy rates) and Google Trends search intensity. Provides an automated model tournament (Baseline, SARIMAX, XGBoost), SHAP explainability, technical indicator scoring, and backtesting via a FastAPI backend and React frontend.
- **Repository Path**: `c:\Ongoing Projects\CSE`
- **File Structure**:
  - `backend/app/main.py`: FastAPI entrypoint, lifespan startup/shutdown, CORS, router mounting, background auto-ingestion daemon thread.
  - `backend/app/api/v1/`: Endpoints (`forecasting.py`, `predictions.py`, `analytics.py`, `stocks.py`, `dashboard.py`, `explanations.py`, `system.py`).
  - `backend/app/forecasting/`: Core ML pipeline (`dataset.py`, `trainer.py`, `evaluator.py`, `prediction_service.py`, `models/baseline.py`, `models/sarimax.py`, `models/xgboost.py`).
  - `backend/app/explainability/`: Model interpretability (`explanation_service.py`, `explainers/shap_explainer.py`, `sarimax_explainer.py`, `permutation_explainer.py`).
  - `backend/app/analytics/`: Statistical analytics (`technical_signal.py`, `backtest.py`, `causality.py`, `correlation.py`, `lag.py`).
  - `backend/app/pipelines/`: Data ingestion & temporal alignment (`calendar.py`).
  - `backend/app/database/`: SQLite persistence via SQLAlchemy (`connection.py`, `models.py`, `cse.db`).
  - `frontend/`: React 18, Vite, Chart.js / Recharts (`src/pages/Dashboard.jsx`, `Forecast.jsx`, `ModelComparison.jsx`, `Analytics.jsx`).
  - `docker-compose.yml`: Multi-container deployment (backend: 8000, frontend: 3000).
- **Concise Architecture & Data-Flow**:
  ```
  CSE Data / CBSL Macro / Google Trends 
  → IngestionService & Repositories 
  → SQLite DB (cse.db)
  → ProcessingPipeline (Cleaning, Sorting, Deduplication)
  → IndicatorBuilder (40+ Technical Indicators: RSI, MACD, Bollinger, ATR)
  → CalendarMerger (pd.merge_asof with direction='backward' to align monthly CBSL data)
  → ForecastDataset (Features X, Target y = close.shift(-horizon), time-ordered 80/20 split)
  → ForecastTrainer (Trains Baseline, SARIMAX(1,1,1), XGBRegressor)
  → ModelEvaluator (RMSE, MAE, MAPE, Directional Accuracy)
  → Selection Tournament (Weighted Score: 0.4*RMSE + 0.2*MAE + 0.2*MAPE + 0.2*(100-DirAcc))
  → Technical Signal Engine Guardrail (±2% trend adjustment)
  → SHAP TreeExplainer (Local feature attribution in LKR)
  → PredictionService (In-memory caching per symbol per date)
  → FastAPI REST API (/api/v1/predictions, /api/v1/forecast)
  → React 18 / Vite Frontend Dashboard
  ```

---

## 2. Flood Risk Prediction / ML Ensemble Project
- **Purpose**: High-precision machine learning regression ensemble predicting regional `flood_risk_score` from environmental, geospatial, infrastructure, and monsoon telemetry features. Evaluated using a custom competition penalty metric.
- **Repository Path**: `c:\Ongoing Projects\Flood Prediction\ml-opsidian-genesis`
- **File Structure**:
  - `notebooks/01_eda_MST.ipynb`: Missing value profiling, skewness checks, target distribution analysis.
  - `notebooks/02_feature_engineering.ipynb`: Domain feature synthesis (effective drainage, flood susceptibility ratios, log transforms).
  - `notebooks/03_baseline_model.ipynb`: Baseline cross-validation and single model performance.
  - `notebooks/04_ensemble_model.ipynb`: Core end-to-end production script with 5-fold CV, OOF generation, LightGBM, XGBoost, CatBoost, and constrained non-negative linear regression stacking.
  - `notebooks/05_catboost_tuning.ipynb` & `temp_run.py`: Optuna Bayesian optimization study tuning CatBoost hyperparameters over 50 trials.
  - `configs/catboost_config.json`: Optimized hyperparameter artifact.
- **Concise Architecture & Data-Flow**:
  ```
  Raw CSVs (train.csv: 20,886 rows, test.csv: 5,300 rows)
  → Preprocessing Pipeline:
      - Temporal parsing (generation_date → month, day, dayofweek, is_monsoon flag)
      - Missingness indicators (missing_indicator_cols)
      - Log1p transformations on skewed features (rainfall_7d_mm, distance_to_river_m)
      - Domain ratio interactions (flood_susceptibility, effective_drainage, rain_per_drainage)
      - Numerical median imputation (train medians learned & applied to test)
      - Categorical string conversion ('Missing')
  → Label Encoding for LGBM & XGBoost (unseen mapped to 'Missing') / Native string handling for CatBoost
  → Target Log Transform: y_log = np.log1p(y)
  → 5-Fold Stratified/K-Fold Cross-Validation:
      - LightGBM Regressor (1000 trees, lr=0.03, num_leaves=63, early_stopping=50)
      - XGBoost Regressor (1000 trees, lr=0.03, max_depth=6, early_stopping=50)
      - CatBoost Regressor (1000 trees, lr=0.03, depth=6, l2_leaf_reg=3)
  → Out-Of-Fold (OOF) Prediction Matrix [oof_lgbm, oof_xgb, oof_cat] (inverting via np.expm1 & clipping [0,1])
  → Meta-Model Stacking: LinearRegression(positive=True, fit_intercept=False)
  → Optimal Weights Learned (e.g. LGBM: 0.035, XGB: 0.023, CatBoost: 0.942)
  → Final Test Inference Blending & Submission CSV Generation
  ```

---

## 3. Online Retail Market Basket Analysis
- **Purpose**: Unsupervised transactional data mining discovering product co-purchase affinities on UK wholesale gift purchases. Benchmarks execution speed of candidate generation (Apriori) vs. prefix-tree projection (FP-Growth) under varied support thresholds, extracting high-lift association rules for commercial retail bundling and inventory bin placement.
- **Repository Path**: `c:\Ongoing Projects\market_basket_analysis`
- **File Structure**:
  - `notebooks/analysis.ipynb`: Data cleansing, cancellation filtering, administrative fee stripping, grouping, pivoting into binary transaction matrix (`OnlineRetail_UK_Basket.csv`).
  - `notebooks/AprioriAlgorithm.ipynb`: Step 2 rule mining with `mlxtend.frequent_patterns.apriori` and `association_rules`, threshold sensitivity (0.05 vs. 0.03 support), metric filtering (confidence ≥ 50%, lift ≥ 1.2).
  - `notebooks/compare.py`: Head-to-head execution time benchmarking script between Apriori and FP-Growth on boolean sparse matrices.
- **Concise Architecture & Data-Flow**:
  ```
  Raw Transactions (OnlineRetail.csv: 541,909 rows)
  → Market Segmentation: Filter United Kingdom (91.4% cohort density)
  → Data Cleansing:
      - Drop rows with null Description
      - Drop cancellation orders (InvoiceNo starting with 'C')
      - Strip whitespace & uppercase Description (reconciling naming variations)
      - Drop administrative noise (POSTAGE, MANUAL, AMAZON FEE, SAMPLES, DISCOUNT)
      - Filter positive Quantity (> 0) and UnitPrice (> 0)
  → Transaction Cart Pivot:
      - Group by [InvoiceNo, Description], sum Quantity
      - Pivot via .unstack().fillna(0)
      - Convert to binary cart matrix (applymap: 1 if x > 0 else 0)
  → Export to OnlineRetail_UK_Basket.csv
  → Compare Run-time Benchmarking (compare.py):
      - Apriori vs FP-Growth at min_support = 0.05 and 0.03
  → Frequent Itemset Mining & Rule Extraction:
      - Metric: Confidence ≥ 0.50, Lift ≥ 1.20
  → Actionable Strategy (Regency Teacup bundles, Gardeners kneeling pad layout)
  ```

---

## 4. Medical Cost Regression & RainTomorrow Classification

### 4A. Medical Cost Regression
- **Purpose**: Supervised parametric regression modeling individual healthcare insurance charges based on demographic, lifestyle, and regional features. Explores single vs. multi-variable regression, interaction effects (e.g., smoker + BMI), and dummy encoding.
- **Repository Path**: `c:\Ongoing Projects\Machine Learning Specialization\1 Linear Regression`
- **File Structure**:
  - `0_Analysis.ipynb`: Exploratory data analysis, distributions, correlation analysis with charges.
  - `1_Single_Feature.ipynb`: Single-feature OLS baseline using `age` for non-smokers.
  - `2_Multiple_features.ipynb`: Multi-feature OLS using `age` and `bmi`.
  - `3_Categorical_features.ipynb`: Categorical encoding (`smoker`, `sex`, `region`), dummy variable creation, and full OLS regression.
  - `Smoker.ipynb`: Smoker cohort segmentation and RMSE evaluation.
- **Concise Architecture & Data-Flow**:
  ```
  Raw Dataset (medical.csv: 1,338 records)
  → Binary Encoding: smoker ('yes': 1, 'no': 0), sex ('female': 0, 'male': 1)
  → One-Hot Dummy Encoding for region (northeast, northwest, southeast, southwest)
  → Feature Matrix X: ['age', 'bmi', 'smoker_code', 'sex_code', 4 regions]
  → Target y: charges
  → Model Fitting: sklearn.linear_model.LinearRegression()
  → Evaluation: RMSE, R² score, coefficient weight interpretation
  ```

### 4B. RainTomorrow Classification
- **Purpose**: Binary meteorological classification predicting whether it will rain tomorrow in Australia (`RainTomorrow`: 0 or 1). Engineered to avoid RAM crashes on large datasets through garbage collection, categorical one-hot encoding, feature normalization, and regularized logistic regression.
- **Repository Path**: `c:\Ongoing Projects\Machine Learning Specialization\2 Logistic Regression for Classification`
- **File Structure**:
  - `data_preprocessing.py`: Memory-efficient preprocessing pipeline with `gc.collect()`, median imputation, OneHotEncoder, MinMaxScaler, stratified splitting, and chunked CSV export.
  - `model.py`: Training script loading split CSVs, standardizing features with `StandardScaler`, fitting `LogisticRegression(solver='liblinear')`, evaluating Accuracy, ROC-AUC, classification report, and saving `roc_curve.png`.
- **Concise Architecture & Data-Flow**:
  ```
  Raw CSV (weatherAUS.csv: ~145k records)
  → Target Cleaning: Drop missing RainToday & RainTomorrow
  → Temporal Feature Extraction: Date → Month (seasonality without high cardinality), drop Date
  → Median Imputation for numeric features
  → OneHotEncoder(sparse_output=False, handle_unknown="ignore") for categorical features
  → MinMaxScaler() scaling numeric columns to [0, 1]
  → Stratified Train/Val/Test Split (60% Train, 20% Val, 20% Test)
  → Chunked CSV Export to processed_weather/ with explicit gc.collect()
  → Model Pipeline (model.py):
      - Load train.csv & test.csv
      - Secondary feature standardization via StandardScaler()
      - LogisticRegression(C=1.0, solver='liblinear', max_iter=1000)
      - Evaluate Accuracy, ROC-AUC, and ROC Curve plotting
  ```

---

# PART 2 — FILE-BY-FILE QUESTIONS

## PROJECT 1: Colombo Stock Exchange (CSE)

### `backend/app/pipelines/calendar.py`
1. **What is the purpose of this file?**  
   It provides the function `align_to_trading_days()`, which synchronizes low-frequency macroeconomic releases (monthly CCPI inflation, policy interest rates) and search trends with the high-frequency daily equity trading calendar.
2. **Why is this file needed?**  
   Financial stocks trade daily, whereas central bank reports are published monthly. Merging them with standard outer joins or forward-filling after an inner join introduces catastrophic lookahead bias (leakage). This file aligns them using `pd.merge_asof(direction="backward")` and tracks the staleness of the data.
3. **What happens when `align_to_trading_days()` is executed?**  
   Dates are parsed to datetime and sorted ascending. A left join is performed between the trading calendar and the macro updates. If updates exist, `pd.merge_asof` with `direction="backward"` assigns the most recent announcement date to each trading day. It computes an `[prefix]_age` column in days, forward-fills values, and backward-fills leading NaNs.
4. **What are the inputs and outputs?**  
   - *Inputs*: `data` (macro DataFrame), `trading_days` (stock calendar DataFrame), `val_col` (str), `prefix` (str), `date_col` (default: "date").  
   - *Outputs*: Aligned `pd.DataFrame` containing `date`, `val_col`, and `[prefix]_age`.
5. **What libraries are imported and why?**  
   `pandas` (for datetime manipulation, `merge`, and `merge_asof`) and `numpy` (for handling numerical NaN fallbacks).
6. **What assumptions does the code make?**  
   Assumes both input DataFrames contain the `date_col`, and that the publication date in `data` represents the exact date the information became publicly accessible.
7. **What could go wrong here?**  
   Line 61 executes `merged[val_col] = merged[val_col].ffill().bfill()`. The `bfill()` on leading rows backfills future macro data onto historical stock trading days before the very first announcement was published, creating lookahead leakage for those earliest records.
8. **How would you improve this implementation?**  
   Replace `bfill()` with a domain constant, historical baseline, or drop the leading trading days where no macroeconomic announcements had yet occurred.

### `backend/app/forecasting/dataset.py`
1. **What is the purpose of this file?**  
   Defines `ForecastDataset`, which transforms the merged historical stock, technical indicator, and macroeconomic DataFrame into supervised training matrices ($X, y$).
2. **What are the inputs and outputs?**  
   - *Inputs*: A merged `pd.DataFrame` with OHLCV prices, macro features, and indicator columns, plus an optional `target_horizon` (default: 30 days).  
   - *Outputs*: Clean feature matrix `X_train`, `X_test` and target vectors `y_train`, `y_test`.
3. **What is the exact target definition?**  
   Line 173: `df["target"] = df["close"].shift(-horizon)`. It predicts the raw closing price $t + 30$ days into the future.
4. **How is the train/test split executed?**  
   In `split(test_size=0.2)`:
   ```python
   split_idx = int(len(self._df) * (1 - test_size))
   train = self._df.iloc[:split_idx]
   test = self._df.iloc[split_idx:]
   ```
   It strictly performs a chronological time-ordered slice without shuffling (`random_state` is absent because shuffle is forbidden).
5. **What could go wrong if `MIN_ROWS = 50` is not checked?**  
   With fewer than 50 rows, rolling indicators (`30_day_mean`, `volatility`) and 20-day lags will produce all NaNs. `df.dropna()` would leave 0 usable rows, crashing the models.

### `backend/app/forecasting/trainer.py`
1. **What is the purpose of this file?**  
   Implements `ForecastTrainer`, the orchestrator that fits all candidate forecasting models (`BaselineModel`, `SARIMAXModel`, `XGBoostModel`), evaluates them on holdout test data, and runs the tournament selection algorithm.
2. **How does the model tournament select the winning model?**  
   Lines 135–141 define a multi-objective selection score:
   $$\text{Score} = 0.4 \times \text{RMSE} + 0.2 \times \text{MAE} + 0.2 \times \text{MAPE} + 0.2 \times (100 - \text{DirAcc}\%)$$
   If an ML model's RMSE is more than 10% worse than the naïve baseline (`ev.rmse > base_rmse * 1.1`), it receives a catastrophic penalty of $+1000.0$, disqualifying it. The lowest score wins.
3. **What guardrail exists against a single model failure?**  
   The training and evaluation loop is wrapped in a `try...except Exception as exc:` block (Lines 96–129). If SARIMAX fails to converge, it logs an `EvaluationResult` with dummy error metrics (999.0) and a warning, allowing the pipeline to select XGBoost or Baseline without crashing the server.

### `backend/app/forecasting/models/xgboost.py`
1. **What is the purpose of this file?**  
   Implements `XGBoostModel`, wrapping `xgboost.XGBRegressor` to forecast multi-step stock prices from tabular features.
2. **What are the hyperparameters configured in the class?**  
   `n_estimators=200`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `random_state=42`, `tree_method="hist"`, `verbosity=0`.
3. **How does `predict()` generate a 30-day forecast trajectory?**  
   Lines 117–120: It predicts the point estimate for day $t+30$, applies technical adjustment, and then linearly interpolates the trajectory from the latest close price:
   ```python
   prices = [round(last_close + (i + 1) * (adjusted_pred_val - last_close) / horizon, 4) for i in range(horizon)]
   ```

### `backend/app/explainability/explainers/shap_explainer.py`
1. **What is the purpose of this file?**  
   Provides local feature attribution for XGBoost forecasts using Lundberg's `shap.TreeExplainer`.
2. **What happens during execution?**  
   It extracts the underlying `xgb_regressor` from the wrapper, creates a `TreeExplainer`, evaluates `explainer.shap_values(X_row)`, extracts `base_value = float(explainer.expected_value)`, converts values into LKR currency impact, and sorts the top 10 features by absolute contribution.
3. **What fallback mechanism is implemented?**  
   If `TreeExplainer` throws an exception (due to XGBoost/SHAP C++ library version mismatches), it falls back to model-agnostic `shap.Explainer(predict_fn, ...)` using a lambda wrapper over `xgb_regressor.predict`.

---

## PROJECT 2: Flood Risk Prediction (`ml-opsidian-genesis`)

### `notebooks/04_ensemble_model.ipynb`
1. **What is the purpose of this file?**  
   It is the master modeling engine for the Flood Risk competition. It handles feature transformations, 5-fold cross-validation, training of three distinct GBDTs (LightGBM, XGBoost, CatBoost), generates out-of-fold (OOF) predictions, fits a non-negative linear meta-regressor, and exports test predictions.
2. **What feature engineering is implemented in `preprocess()`?**  
   - Temporal decomposition: `generation_date` $\rightarrow$ `gen_month`, `gen_day`, `gen_dow`, and `is_monsoon` (months 5–11).
   - Missing value binary flags: 9 columns (e.g. `elevation_m_is_missing`).
   - Log1p transforms on skewed physical variables: `rainfall_7d_mm`, `distance_to_river_m`, `population_density_per_km2`.
   - Domain interaction ratios:
     - `flood_susceptibility = rainfall_7d_mm / (elevation_m + 1)`
     - `effective_drainage = drainage_index * (1 - built_up_percent / 100)`
     - `river_elevation_risk = (1 / (distance_to_river_m + 1)) * (1 / (elevation_m + 1))`
3. **What are the inputs and outputs?**  
   - *Inputs*: `train.csv` (20,886 rows $\times$ 47 cols), `test.csv` (5,300 rows $\times$ 46 cols).  
   - *Outputs*: `train_processed` (70 cols), `test_processed` (69 cols), OOF prediction vectors, and `sub_ensemble_v1.csv`.
4. **How are missing values handled cleanly between train and test?**  
   `preprocess(train, is_train=True)` calculates `train_medians = df[num_cols].median()` and returns it. Then `preprocess(test, train_medians=medians, is_train=False)` imputes test missing values using the *training set medians*, preventing data leakage.
5. **How are categorical columns handled differently for LightGBM/XGBoost vs. CatBoost?**  
   - For LightGBM & XGBoost: `LabelEncoder` maps strings to integers. Unseen test categories are mapped to `'Missing'`:
     ```python
     X_test[col].astype(str).map(lambda x: x if x in le.classes_ else 'Missing')
     ```
   - For CatBoost: Categorical columns remain raw strings and are passed directly into the `cat_features=CAT_FEATURES` parameter of `CatBoostRegressor`.

### `notebooks/temp_run.py` & `05_catboost_tuning.ipynb`
1. **What is the purpose of this script?**  
   Runs an automated Optuna Bayesian optimization study over 50 trials to minimize the custom competition evaluation metric for CatBoost.
2. **What hyperparameters are tuned?**  
   `iterations` (500–2000), `learning_rate` (0.01–0.1 log-scale), `depth` (4–10), `l2_leaf_reg` (1–10), `bagging_temperature` (0–1), `border_count` (32–255), and `random_strength` (0–10).
3. **What is the custom competition metric proxy implemented?**  
   ```python
   def competition_metric_proxy(y_true, y_pred):
       mae = np.mean(np.abs(y_true - y_pred))
       rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
       balanced_error = (mae + rmse) / 2
       r2 = r2_score(y_true, y_pred)
       ev_penalty = max(0, 1 - r2)
       return balanced_error * (1 + ev_penalty)
   ```
   It balances MAE and RMSE, and heavily penalizes models whose $R^2 < 1.0$ through a multiplicative penalty factor $(1 + \max(0, 1 - R^2))$.

---

## PROJECT 3: Online Retail Market Basket Analysis

### `notebooks/analysis.ipynb`
1. **What is the purpose of this file?**  
   Ingests the raw uncleaned e-commerce transaction log, isolates the UK market segment, purges returns and administrative entries, and formats the data into a binary cart matrix.
2. **What are the key data cleaning steps?**  
   - Drops null `Description` rows (1,454 rows).
   - Filters out cancelled transactions where `InvoiceNo.str.startswith('C')`.
   - Cleans text formatting: `Description.str.strip().str.upper()`.
   - Strips noise items: `['POSTAGE', 'DOTCOM POSTAGE', 'MANUAL', 'SAMPLES', 'AMAZON FEE', 'CRUK COMMISSION', 'DISCOUNT']`.
   - Filters `Quantity > 0` and `UnitPrice > 0`.
3. **How is the binary cart matrix created?**  
   ```python
   basket = uk_df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
   basket = basket.applymap(lambda x: 1 if x > 0 else 0)
   ```
   Each row becomes a unique `InvoiceNo`, each column a product `Description`, and cells contain `1` (purchased) or `0` (not purchased).

### `notebooks/compare.py`
1. **What is the purpose of this file?**  
   A standalone benchmarking utility measuring the runtime performance of `apriori` vs. `fpgrowth` from `mlxtend` on the boolean basket matrix.
2. **What data type conversion was required?**  
   Line 13: `basket = basket.astype(bool)`. Older versions of `mlxtend` accepted integers (0/1), but current versions raise deprecation warnings or runtime errors unless the matrix is strictly boolean.
3. **What is the outcome of the benchmark?**  
   Both algorithms find the exact same number of frequent itemsets. However, at lower support thresholds ($\le 0.02$), FP-Growth runs significantly faster than Apriori because it constructs an FP-Tree without generating combinatorial candidate itemsets.

---

## PROJECT 4: Medical Cost Regression & RainTomorrow Classification

### `1 Linear Regression/3_Categorical_features.ipynb`
1. **What is the purpose of this file?**  
   Demonstrates how to incorporate categorical variables into linear regression using insurance cost data.
2. **How are variables encoded?**  
   - `smoker` mapped manually: `{'yes': 1, 'no': 0}`.
   - `sex` mapped manually: `{'male': 1, 'female': 0}`.
   - `region` dummy encoded into 4 binary columns: `northeast`, `northwest`, `southeast`, `southwest`.
3. **What statistical issue is present in line 1021?**  
   ```python
   input = medical_df[['age', 'bmi', 'smoker_code', 'sex_code', 'northeast', 'northwest', 'southeast', 'southwest']]
   model.fit(input, target)
   ```
   The model includes **all 4 region dummies** alongside an intercept, falling into the **dummy variable trap** (perfect multicollinearity: $\sum \text{region}_i = 1$). One dummy must be dropped (`drop_first=True`).

### `2 Logistic Regression for Classification/data_preprocessing.py`
1. **What is the purpose of this file?**  
   A memory-conscious data preparation pipeline for Australian weather data, preventing OOM errors on large datasets.
2. **What memory optimization techniques are used?**  
   Calls `del raw_df, num_df, cat_df` followed immediately by `gc.collect()`. Writes final splits to disk sequentially with `chunksize=10000`.
3. **What severe data leakage flaw exists here?**  
   Lines 51–66: Median imputation, `OneHotEncoder.fit_transform()`, and `MinMaxScaler.fit_transform()` are all executed on `raw_df` **before** the train/val/test split (Lines 82–97). Test set statistics leak into the training features.

### `2 Logistic Regression for Classification/model.py`
1. **What is the purpose of this file?**  
   Loads preprocessed splits, applies `StandardScaler`, fits `LogisticRegression`, evaluates classification metrics, and plots the ROC curve.
2. **What redundant preprocessing occurs in `preprocess()`?**  
   ```python
   scaler = StandardScaler()
   X_train_scaled = scaler.fit_transform(X_train)
   ```
   `data_preprocessing.py` had *already* scaled numeric columns with `MinMaxScaler`. Re-applying `StandardScaler` standardizes previously bounded [0, 1] numbers and distorts the one-hot encoded binary columns (giving binary dummy variables zero mean and unit variance).

---

# PART 3 — LINE-BY-LINE & CODE-SNIPPET QUESTIONS

### Snippet 1 (CSE — `calendar.py`, Line 54)
```python
updates_df = pd.DataFrame({date_col: update_dates, "last_update_date": update_dates})
merged = pd.merge_asof(merged, updates_df, on=date_col, direction="backward")
```
- **Interviewer Question**: "What exactly does `direction='backward'` do here?"
- **Answer**: For each trading date $t$ in `merged`, it searches `updates_df` for the most recent date $\le t$. It matches the stock tick to the latest macroeconomic figure released on or before that exact day, strictly preventing lookahead leakage.
- **Follow-up**: "What would happen if you changed it to `direction='nearest'`?"
- **Follow-up Answer**: If a central bank announcement is made on Wednesday, a 'nearest' merge would match Tuesday's trading tick to Wednesday's future announcement, causing future information leakage.
- **Deeper Follow-up**: "Why didn't you just use standard `pd.merge()` with `ffill()`?"
- **Deeper Follow-up Answer**: `merge_asof` allows exact asynchronous event alignment and enables us to compute `(merged[date_col] - merged["last_update_date"]).dt.days`, generating an explicit data staleness feature.

---

### Snippet 2 (CSE — `dataset.py`, Line 173)
```python
df["target"] = df["close"].shift(-horizon)
```
- **Interviewer Question**: "Explain why `shift(-horizon)` is used with a negative integer."
- **Answer**: A negative shift shifts future values backwards up the DataFrame. For row $t$, `shift(-30)` places the closing price from trading row $t + 30$ into row $t$'s target column, framing a supervised regression problem where row $t$'s current features predict the price 30 days ahead.
- **Follow-up**: "What happens to the last 30 rows of the DataFrame when you execute this?"
- **Follow-up Answer**: They become `NaN` because there are no future rows 30 days ahead.
- **Deeper Follow-up**: "How does your code handle those last 30 rows during training vs. live inference?"
- **Deeper Follow-up Answer**: During training, line 182 calls `df.dropna(subset=['target'])`, removing them. During live inference, `get_last_row()` extracts the latest row $t$ (where target is NaN) to generate the future 30-day forecast.

---

### Snippet 3 (Flood — `04_ensemble_model.ipynb`, Line 382)
```python
stacker = LinearRegression(positive=True, fit_intercept=False)
oof_stack = np.column_stack([oof_lgbm_c, oof_xgb_c, oof_cat_c])
stacker.fit(oof_stack, y)
```
- **Interviewer Question**: "Why did you set `positive=True` and `fit_intercept=False` in the stacking linear regression?"
- **Answer**: Setting `fit_intercept=False` and `positive=True` constrains the linear combination to be a non-negative weighted sum ($y = w_1 \hat{y}_{\text{lgb}} + w_2 \hat{y}_{\text{xgb}} + w_3 \hat{y}_{\text{cat}}$) without an arbitrary constant offset. This guarantees that the meta-model acts as a pure blending ensemble and prevents negative weights that could destabilize unseen test predictions.
- **Follow-up**: "What were the learned weights in your experiment?"
- **Follow-up Answer**: LightGBM: 0.035, XGBoost: 0.023, CatBoost: 0.942. CatBoost received 94.2% of the ensemble weight due to superior native handling of categorical geographical features.

---

### Snippet 4 (Flood — `04_ensemble_model.ipynb`, Line 217)
```python
X_test_encoded[col] = le.transform(
    X_test[col].astype(str).map(
        lambda x: x if x in le.classes_ else 'Missing'
    )
)
```
- **Interviewer Question**: "What does this lambda function accomplish, and is there a potential bug?"
- **Answer**: It checks if a test category exists in the training vocabulary `le.classes_`. If not, it replaces it with `'Missing'` to prevent `LabelEncoder.transform()` from throwing an unseen category error.
- **Follow-up**: "What bug will occur if `'Missing'` was never present in the training set?"
- **Follow-up Answer**: If the training set never contained any null or `'Missing'` string for that column, `'Missing'` itself is not in `le.classes_`. The lambda will replace the category with `'Missing'`, and `le.transform()` will crash with `ValueError: y contains previously unseen labels: 'Missing'`.
- **Fix**: Ensure `'Missing'` is explicitly added to `le.classes_` or fit the encoder on training data that already has imputed `'Missing'` tokens.

---

### Snippet 5 (Market Basket — `compare.py`, Line 13)
```python
basket = basket.astype(bool)
```
- **Interviewer Question**: "Why did you explicitly cast the DataFrame to `bool`?"
- **Answer**: In newer versions of `mlxtend` (v0.22+), passing integer binary matrices (0/1) to `apriori()` or `fpgrowth()` raises a deprecation warning and causes memory inefficiencies. Converting to boolean reduces RAM by 8x (1 byte per boolean vs. 8 bytes per int64) and complies with `mlxtend`'s API requirements.
- **Follow-up**: "What happens if a column contains empty strings or NaNs when you do `.astype(bool)`?"
- **Follow-up Answer**: In Python, non-empty strings and `NaN` values evaluate to `True`. If `basket.dropna()` isn't executed first, NaNs would become `True`, erroneously indicating every transaction contained that missing product.

---

### Snippet 6 (RainTomorrow — `data_preprocessing.py`, Lines 50–52)
```python
for col in numeric_cols:
    median_val = raw_df[col].median()
    raw_df[col] = raw_df[col].fillna(median_val)
```
- **Interviewer Question**: "Looking at lines 50–52 and then line 82 (`train_test_split`), what critical ML flaw is present?"
- **Answer**: Data leakage. The median is computed over the entire dataset `raw_df` before splitting into training, validation, and testing sets. Information from the test set's distribution directly leaks into the imputed values of the training set.
- **Follow-up**: "How should this be refactored?"
- **Follow-up Answer**: Split the raw dataset first: `train_df, test_df = train_test_split(raw_df)`. Compute `median_val = train_df[col].median()`, and use that exact training median to fill missing values in both `train_df` and `test_df`.

---

# PART 4 — "WHY DID YOU DO THIS?" DECISION QUESTIONS

### Q1. Why use SARIMAX alongside XGBoost in the CSE project?
- **Interview Answer**: Financial markets exhibit both linear autoregressive inertia and complex non-linear feature interactions. SARIMAX explicitly models stationary stochastic processes, mean-reversion, and autocorrelation via ARIMA terms while incorporating exogenous macroeconomic indicators. XGBoost captures non-linear threshold effects. Running a tournament between them allows the system to deploy whichever model best fits the current market regime.
- **Follow-up**: "Why not just use an LSTM or Transformer?"
- **Follow-up Answer**: Deep learning models require tens of thousands of stationary sequences to generalize without severe overfitting. On 26 CSE stocks with only a few hundred daily trading rows, LSTMs overfit rapidly and are too slow to retrain on-demand inside a sub-second REST API response.

### Q2. Why did you use `log1p` target transformation in the Flood project?
- **Interview Answer**: The target `flood_risk_score` is non-negative and right-skewed. Applying `y_log = np.log1p(y)` compresses the dynamic range, stabilizes variance across folds, and ensures that when predictions are inverted via `np.expm1()`, the model cannot predict negative risk scores.
- **Follow-up**: "Why didn't you just train on raw values?"
- **Follow-up Answer**: Raw training resulted in higher RMSE penalties on extreme flood events. The log transform made the error surface more Gaussian, allowing gradient boosting trees to find better splits.

### Q3. Why use FP-Growth instead of Apriori for low support in Market Basket Analysis?
- **Interview Answer**: Apriori uses a level-wise candidate generation approach ($k$-itemset candidates require scanning the database repeatedly). As support drops below 0.02, candidate pairs suffer a combinatorial explosion ($O(2^d)$). FP-Growth compresses the entire transactional database into an in-memory Frequent Pattern Tree (FP-Tree) and mines associations by recursive conditional tree projection, eliminating candidate generation entirely.
- **Follow-up**: "When would Apriori be preferable?"
- **Follow-up Answer**: When memory is strictly constrained and the minimum support threshold is high ($\ge 0.05$). Apriori has a smaller in-memory footprint because it does not maintain an entire prefix tree in RAM.

### Q4. Why use SQLite (`cse.db`) instead of PostgreSQL in the current CSE implementation?
- **Interview Answer**: SQLite is serverless, zero-configuration, and stores the entire market history in a single local file (`cse.db`). For our single-container development and demonstration environment, it provides sub-millisecond read access without the network overhead or hosting costs of managing a separate database service.
- **Follow-up**: "What would change if the dataset/project became 10x larger?"
- **Follow-up Answer**: SQLite locks the entire database file during writes, creating a bottleneck under concurrent ingestion. At 10x scale, I would migrate to PostgreSQL using SQLAlchemy's connection pooling, add timescaleDB partitioning for time-series queries, and index composite keys on `(symbol, date)`.

---

# PART 5 — REALISTIC DEBUGGING SCENARIOS

### Debugging Scenario 1: Model achieves 99.8% directional accuracy
- **Problem**: You retrain your XGBoost model on CSE stock data and it suddenly jumps to 99.8% directional accuracy and near-zero RMSE.
- **Expected Reasoning**: In financial equities, 99.8% directional accuracy is impossible and indicates future information leakage in feature construction.
- **Likely Cause in Code**: Inspect `backend/app/forecasting/dataset.py`. Look at the lag features and target construction:
  ```python
  df["close_lag_1"] = df["close"].shift(-1)  # Accidental negative shift!
  # OR
  df["target"] = df["close"]                  # Predicting today's close instead of future close
  ```
  If `shift()` was used with a positive number for the target or a negative number for lags, today's feature matrix contains tomorrow's actual closing price.
- **Fix**: Verify all feature shifts are positive (`shift(1)`, `shift(5)`) and only the target uses negative shift (`shift(-30)`).

---

### Debugging Scenario 2: CatBoost crashes with `CatBoostError: Invalid float value`
- **Problem**: In the Flood ensemble script, CatBoost suddenly throws an error during `.fit()`: `CatBoostError: Bad value for num_feature[xx]=SomeString: Cannot convert 'SomeString' to float`.
- **Expected Reasoning**: CatBoost treats columns as numerical floats unless they are explicitly registered in the `cat_features` argument.
- **Likely Cause in Code**: In `04_ensemble_model.ipynb`, a new categorical column was added to the dataframe, but was omitted from the `CAT_FEATURES` list, or an existing categorical feature had float NaNs that were converted inconsistently.
- **Fix**: Explicitly cast all categorical columns to string:
  ```python
  for col in CAT_FEATURES:
      df[col] = df[col].fillna('Missing').astype(str)
  ```
  And ensure `cat_features=CAT_FEATURES` is passed to `CatBoostRegressor`.

---

### Debugging Scenario 3: Memory exhaustion crash during RainTomorrow preprocessing
- **Problem**: Running `data_preprocessing.py` on a lower-spec server crashes with `MemoryError` or `Process killed (SIGKILL)`.
- **Likely Cause in Code**: Look at Line 57:
  ```python
  encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
  cat_encoded = encoder.fit_transform(raw_df[categorical_cols])
  ```
  Setting `sparse_output=False` forces a dense 2D NumPy array of floats across hundreds of thousands of rows and high-cardinality categories (e.g. `Location` with 49 levels), allocating gigabytes of RAM simultaneously.
- **Fix**: Use `sparse_output=True` (or `sparse=True` in older sklearn) or process categorical transformations in batches, using category dtype encoding instead of full one-hot expansion.

---

# PART 6 — "CHANGE THIS CODE" CODING PROBLEMS

### Problem 1: Prevent Dummy Variable Trap in Medical Cost Regression
- **Original Code** (`3_Categorical_features.ipynb`, Line 1021):
  ```python
  input = medical_df[['age', 'bmi', 'smoker_code', 'sex_code', 'northeast', 'northwest', 'southeast', 'southwest']]
  target = medical_df['charges']
  model.fit(input, target)
  ```
- **Interviewer Request**: "Modify this code to prevent the dummy variable trap and ensure our OLS estimates are mathematically stable."
- **Modified Code**:
  ```python
  # Drop one dummy variable (e.g., 'southwest') to act as the baseline reference category
  input_clean = medical_df[['age', 'bmi', 'smoker_code', 'sex_code', 'northeast', 'northwest', 'southeast']]
  target = medical_df['charges']

  from sklearn.linear_model import LinearRegression
  model = LinearRegression()
  model.fit(input_clean, target)
  ```
- **Explanation**: A categorical variable with $k$ categories must be represented by $k-1$ dummy indicators when an intercept is included. Including all 4 regions creates perfect linear dependency ($\text{NE} + \text{NW} + \text{SE} + \text{SW} = 1$), causing the $(X^T X)$ matrix to become non-invertible or numerically unstable.

---

### Problem 2: Fix Data Leakage in RainTomorrow Preprocessing
- **Original Code** (`data_preprocessing.py`):
  ```python
  # Median imputation applied to whole dataset
  for col in numeric_cols:
      median_val = raw_df[col].median()
      raw_df[col] = raw_df[col].fillna(median_val)

  train_val_df, test_df = train_test_split(raw_df, test_size=0.2, random_state=42)
  ```
- **Interviewer Request**: "Refactor this preprocessing block so that all imputations, scalers, and encoders strictly prevent data leakage."
- **Modified Code**:
  ```python
  # 1. Split FIRST
  train_val_df, test_df = train_test_split(raw_df, test_size=0.2, random_state=42, stratify=raw_df["RainTomorrow"])
  train_df, val_df = train_test_split(train_val_df, test_size=0.25, random_state=42, stratify=train_val_df["RainTomorrow"])

  # 2. Fit Imputer ONLY on train_df
  train_medians = train_df[numeric_cols].median()

  # 3. Transform train, val, and test using train_medians
  train_df[numeric_cols] = train_df[numeric_cols].fillna(train_medians)
  val_df[numeric_cols] = val_df[numeric_cols].fillna(train_medians)
  test_df[numeric_cols] = test_df[numeric_cols].fillna(train_medians)
  ```
- **Explanation**: Fits statistics strictly on the training partition and applies them downstream to validation and testing partitions.

---

# PART 7 — TRACE THE CODE

### CSE Full Prediction & Explainability Request Trace
```
1. Client Action:
   User clicks "JKH.N0000" on React Frontend (`frontend/src/pages/Forecast.jsx`).
2. HTTP Request:
   React executes `fetch('http://localhost:8000/api/v1/predictions?symbol=JKH.N0000&horizon=30')`.
3. FastAPI Dispatch:
   `app/api/v1/predictions.py::get_prediction()` receives request.
4. Service Invocation:
   Calls `PredictionService.get_predictions(symbol="JKH.N0000", horizon=30)`.
5. Cache Check:
   Inspects `self._cache` with key `("JKH.N0000", "2026-09-25")`. If cache miss, triggers training.
6. DB Extraction:
   `StockPriceRepository.get_by_symbol()` queries SQLite table `stock_prices` for all historical rows.
7. Technical Indicators:
   `ProcessingPipeline.process()` computes 40+ indicators (RSI, MACD, Bollinger Bands, ATR).
8. Supervised Dataset Matrix:
   `ForecastDataset` sorts by date, shifts target 30 days ahead (`shift(-30)`), drops NaNs, splits 80/20 chronologically.
9. Tournament Training:
   `ForecastTrainer.run()` trains BaselineModel, SARIMAX(1,1,1), and XGBRegressor.
10. Evaluation & Guardrail:
    Computes RMSE, MAE, MAPE, Directional Accuracy.
    Evaluates selection score; applies penalty if ML model is 10% worse than baseline.
    `TechnicalSignalEngine.calculate()` computes technical score and applies ±2% guardrail adjustment.
11. SHAP Interpretability:
    `SHAPExplainer.explain()` invokes `shap.TreeExplainer(xgb_regressor)` to calculate signed LKR impact for top 10 features.
12. Response Formatting:
    FastAPI serializes payload to JSON (forecast trajectory, best model, metrics, intervals, SHAP attributions).
13. Frontend Render:
    React state updates; Chart.js renders the 30-day forecast cone with confidence intervals and SHAP horizontal bar chart.
```

---

# PART 8 — MODEL-SPECIFIC CODE DEEP-DIVES

| Model | Project | Inputs | Target | Key Hyperparameters in Code | Role & Limitations |
|---|---|---|---|---|---|
| **XGBoost** (`XGBRegressor`) | CSE (`xgboost.py`) | 40+ technical, lag, macro, calendar features | `close(t+30)` | `n_estimators=200`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`, `tree_method='hist'` | Captures non-linear macroeconomic interactions; cannot extrapolate trends beyond historical extrema. |
| **SARIMAX** | CSE (`sarimax.py`) | Historical prices + exogenous (`rsi`, `macd`, `sma_20`, `sma_50`, `volatility`) | `close(t+30)` | `order=(1,1,1)`, `seasonal_order=(0,0,0,0)`, `enforce_stationarity=False` | Statistical time-series model; slow on large data, sensitive to missing exogenous values. |
| **LightGBM** (`LGBMRegressor`) | Flood (`04_ensemble.ipynb`) | 65 engineered features (label-encoded) | `log1p(flood_risk_score)` | `n_estimators=1000`, `learning_rate=0.03`, `num_leaves=63`, `min_child_samples=20`, `subsample=0.8` | Leaf-wise tree growth, extremely fast training; prone to overfitting small datasets. |
| **CatBoost** (`CatBoostRegressor`) | Flood (`04_ensemble.ipynb`) | 65 features with 10 native categorical strings | `log1p(flood_risk_score)` | `iterations=1000`, `learning_rate=0.03`, `depth=6`, `l2_leaf_reg=3`, `loss_function='RMSE'` | Built-in target encoding and symmetric trees; dominant model in ensemble (94.2% weight). |
| **Non-Negative Stacker** | Flood (`04_ensemble.ipynb`) | 3 OOF prediction columns | `flood_risk_score` | `fit_intercept=False`, `positive=True` | Constrained linear blend; prevents negative weights and bias drift. |
| **Logistic Regression** | Weather (`model.py`) | Standardized meteorological features | `RainTomorrow` (0/1) | `C=1.0`, `solver='liblinear'`, `max_iter=1000` | Fast linear classifier; assumes linear log-odds relationship. |

---

# PART 9 — COMPREHENSIVE DATA LEAKAGE AUDIT

### Leakage Audit Checklist Across All 4 Codebases

1. **Macro Data Forward-Fill vs. Backward-Fill** (`CSE/backend/app/pipelines/calendar.py`):
   - *Status*: **Partial Leakage Present**.
   - *Detail*: `pd.merge_asof(..., direction="backward")` prevents future leakage. However, Line 61: `merged[val_col] = merged[val_col].ffill().bfill()` uses `bfill()`. The initial trading rows before the first macro announcement receive future values.
2. **Train/Test Splitting** (`Flood Prediction/notebooks/04_ensemble_model.ipynb`):
   - *Status*: **Clean**.
   - *Detail*: Imputation medians are learned strictly on `train` (`preprocess(train, is_train=True)`) and passed explicitly into test preprocessing (`preprocess(test, train_medians=medians, is_train=False)`).
3. **Out-of-Fold Predictions for Stacking** (`Flood Prediction`):
   - *Status*: **Clean**.
   - *Detail*: OOF predictions are generated strictly on the validation fold of each split: `oof_lgbm[val_idx] = np.expm1(lgbm.predict(Xval_enc))`. The meta-model never sees in-sample predictions.
4. **Target Encoding / Scaling** (`Weather/data_preprocessing.py`):
   - *Status*: **Severe Leakage Present**.
   - *Detail*: `MinMaxScaler` and `median()` are fit on `raw_df` prior to `train_test_split()`.
5. **Time-Series Lags and Rolling Windows** (`CSE/backend/app/forecasting/dataset.py`):
   - *Status*: **Clean**.
   - *Detail*: Rolling means (`df["close"].rolling(7).mean()`) and lags (`df["close"].shift(1)`) are strictly backward-looking.

---

# PART 10 — PERFORMANCE, MEMORY & SCALING

1. **Computational Bottleneck in CSE**:
   - `SARIMAXModel.train()` takes ~1.5–3 seconds per stock due to iterative numerical maximum likelihood optimization via Kalman filtering.
   - *Optimization*: Cache fitted model artifacts using joblib or run SARIMAX retraining as an offline nightly batch cron job instead of on-demand in the API request cycle.
2. **Memory Bottleneck in Weather Dataset**:
   - `OneHotEncoder(sparse_output=False)` produces a wide dense matrix causing RAM spikes.
   - *Optimization*: Use `sparse_output=True` and pass `scipy.sparse.csr_matrix` directly to `LogisticRegression`.
3. **What happens if transactions grow 100x in Market Basket Analysis?**
   - Apriori will fail with out-of-memory or take hours due to candidate generation.
   - FP-Growth or distributed implementations (e.g. PySpark MLlib's FPGrowth) must be used.

---

# PART 11 — PRODUCTION & DEPLOYMENT ARCHITECTURE

### Current Implementation vs. Production Roadmap

| Component | What Current Code Does | What Would Be Changed for Enterprise Production |
|---|---|---|
| **Model Ingestion & Training** | Trained on-demand in API request or cached in-memory dictionary (`_cache`). | Decouple training from serving: Celery / Redis task queue with scheduled training workers. |
| **Model Storage / Versioning** | Models kept in ephemeral RAM; re-trained on server reboot. | Persist versioned model artifacts (`.pkl`, `.onnx`, MLflow) to Amazon S3 or Google Cloud Storage. |
| **Database** | Local file-based SQLite database (`cse.db`). | Managed PostgreSQL cluster with read-replicas and timescaleDB time-series indexing. |
| **API Serving** | Uvicorn running a single FastAPI process. | Gunicorn multi-worker process manager behind Nginx ingress reverse proxy with horizontal pod autoscaling. |
| **Monitoring & Drift** | Basic health endpoint (`/api/v1/health`). | Evidently AI / Prometheus tracking Prediction Drift, Feature Drift, and Data Quality anomalies. |
| **Containerization** | Docker Compose with local volume mounts. | Multi-stage Docker builds, Kubernetes manifests, Helm charts, CI/CD automated test verification. |

---

# PART 12 — INTERVIEWER FOLLOW-UP CHAINS (10 PER PROJECT)

## Project 1: Colombo Stock Exchange (CSE)

### Chain 1: Data Integration & Alignment
- **Q1**: "How did you combine daily stock prices with monthly inflation rates?"
  - *Answer*: Using `align_to_trading_days()` in `calendar.py`, which executes `pd.merge_asof` with `direction='backward'`.
- **Q2**: "Why `direction='backward'`?"
  - *Answer*: Because each daily stock tick must only join with the macroeconomic figure that was published on or before that exact trading day.
- **Q3**: "What happens on holidays and weekends?"
  - *Answer*: They are excluded from the trading calendar; the stock market is closed so no prediction row is generated.
- **Q4**: "How do you track if the macro data is stale?"
  - *Answer*: By calculating `(merged[date_col] - merged["last_update_date"]).dt.days`, generating an explicit `inflation_age` feature for the model.
- **Q5**: "How would you handle real-time streaming market data?"
  - *Answer*: Kafka event stream consuming trade ticks, aggregating OHLCV in Redis with 1-minute tumbling windows.

### Chain 2: Target Engineering & Forecasting Horizon
- **Q1**: "What is your target variable?"
  - *Answer*: The closing price 30 trading days into the future: `close.shift(-30)`.
- **Q2**: "Why did you forecast raw price instead of percentage returns?"
  - *Answer*: Raw price forecasts align with user-facing portfolio valuation and allow direct calculation of LKR confidence intervals and technical price limits.
- **Q3**: "What is the problem with forecasting non-stationary raw price with tree models?"
  - *Answer*: Trees cannot extrapolate trends beyond the minimum or maximum values seen in training.
- **Q4**: "How did your implementation solve that limitation?"
  - *Answer*: By including price ratio features (`daily_return`, `high_low_range`), combining XGBoost with SARIMAX, and applying a rule-based technical guardrail adjustment.
- **Q5**: "How would you re-architect it if you only wanted direction?"
  - *Answer*: Binarize the target: `(close.shift(-30) > close).astype(int)` and use an `XGBClassifier` evaluating ROC-AUC.

### Chain 3: The Model Tournament
- **Q1**: "How does your system decide which model output to show the user?"
  - *Answer*: `ForecastTrainer` computes a multi-metric tournament score across Baseline, SARIMAX, and XGBoost on holdout test data.
- **Q2**: "What is the tournament score formula?"
  - *Answer*: $0.4 \times \text{RMSE} + 0.2 \times \text{MAE} + 0.2 \times \text{MAPE} + 0.2 \times (100 - \text{DirectionalAccuracy}\%)$.
- **Q3**: "Why penalize models based on the Baseline?"
  - *Answer*: In financial forecasting, complex models that cannot beat a simple historical persistence baseline are actively destroying capital. We penalize them by $+1000.0$.
- **Q4**: "Why include Directional Accuracy alongside RMSE?"
  - *Answer*: A trader can make money with high directional accuracy even with slight price error, whereas a model with low RMSE that constantly guesses the wrong direction produces losing trades.
- **Q5**: "Why not use K-fold cross-validation in the tournament?"
  - *Answer*: To keep API response times under 2 seconds; we perform an 80/20 chronological split.

### Chain 4: Technical Guardrail Engine
- **Q1**: "What does `TechnicalSignalEngine` do?"
  - *Answer*: It evaluates rule-based technical indicators (RSI, MACD, SMA crossovers) to assign a market outlook score from $-5$ to $+5$.
- **Q2**: "Why avoid using BUY / SELL labels directly?"
  - *Answer*: Markets are inherently probabilistic; the platform is designed for decision support rather than automated financial advice.
- **Q3**: "How does this score affect the ML forecast?"
  - *Answer*: It applies a bounded post-processing adjustment (`compute_technical_adjustment`) that nudges the predicted price by up to $\pm 2\%$.
- **Q4**: "Why adjust ML predictions with rules?"
  - *Answer*: If ML predictions contradict overwhelming technical momentum (e.g., extreme RSI divergence), the rule engine dampens extreme model error.
- **Q5**: "What happens if technical data is missing?"
  - *Answer*: The engine returns a neutral score (0), leaving the ML model prediction unadjusted.

### Chain 5: SHAP Interpretability
- **Q1**: "Why did you use SHAP instead of feature importance built into XGBoost?"
  - *Answer*: Built-in feature importance (gain/split count) provides global model metrics, whereas SHAP provides local, sample-specific explanations showing *why* a particular stock's price was predicted high or low today.
- **Q2**: "What explainer did you use and why?"
  - *Answer*: `shap.TreeExplainer`, because it calculates exact Shapley values for tree ensembles in $O(TLD)$ time.
- **Q3**: "In what units are the SHAP values expressed?"
  - *Answer*: Sri Lankan Rupees (LKR), representing additive price deviations from the expected baseline price.
- **Q4**: "How do you display this in the UI?"
  - *Answer*: The top 10 contributing features are sent via REST API and rendered as a horizontal tornado bar chart colored green (positive) and red (negative).
- **Q5**: "What if TreeExplainer fails?"
  - *Answer*: Our code catches the exception and falls back to model-agnostic `shap.Explainer` using a prediction lambda function.

### Chain 6: Backtesting Engine
- **Q1**: "Where is backtesting implemented in your codebase?"
  - *Answer*: In `backend/app/analytics/backtest.py`.
- **Q2**: "How does it simulate trading?"
  - *Answer*: It runs a historical walk-forward simulation applying SMA crossover and momentum strategies, calculating portfolio equity, Sharpe ratio, and Maximum Drawdown.
- **Q3**: "Does it account for transaction fees?"
  - *Answer*: Yes, CSE trading levies and broker commissions (1.12%) are deducted from each trade.
- **Q4**: "How do you prevent lookahead bias in backtests?"
  - *Answer*: Trade execution decisions at time $t$ only utilize signals computed on data up to $t-1$.
- **Q5**: "What metric indicates strategy risk?"
  - *Answer*: Maximum Drawdown (MDD) and Annualized Sharpe Ratio.

### Chain 7: Granger Causality
- **Q1**: "Why did you implement Granger Causality in `causality.py`?"
  - *Answer*: To statistically verify whether macroeconomic indicators or Google Trends search intensity lead CSE stock price returns.
- **Q2**: "What statistical test is evaluated?"
  - *Answer*: `statsmodels.tsa.stattools.grangercausalitytests` using the SSR $\chi^2$ p-value across lags 1 to 5.
- **Q3**: "What null hypothesis is tested?"
  - *Answer*: That the exogenous variable does NOT Granger-cause the stock return series. A p-value $< 0.05$ rejects the null.
- **Q4**: "What prerequisite must the time series satisfy?"
  - *Answer*: Stationarity. We test against `daily_return` rather than raw non-stationary closing prices.
- **Q5**: "What if the series has zero variance?"
  - *Answer*: The code explicitly checks `if test_df[var].var() < 1e-8: continue` to avoid singular matrix exceptions.

### Chain 8: Database & Persistence Layer
- **Q1**: "How does SQLAlchemy connect to the database?"
  - *Answer*: Via `connection.py` using `sessionmaker(bind=create_engine('sqlite:///cse.db'))`.
- **Q2**: "How are tables created?"
  - *Answer*: In `main.py` lifespan startup, calling `Base.metadata.create_all(bind=engine)`.
- **Q3**: "What models exist?"
  - *Answer*: `StockPrice` (OHLCV ticks), `MacroIndicator` (CBSL figures), and `PredictionExplanation` (saved forecast audits).
- **Q4**: "How do you handle sessions?"
  - *Answer*: Using a `get_db()` context manager yielding the session and executing `db.close()` in a `finally` block.
- **Q5**: "How do you prevent duplicate stock prices for the same day?"
  - *Answer*: A unique constraint on `(symbol, date)` in the `stock_prices` table definition.

### Chain 9: API Design & FastAPI
- **Q1**: "Why did you use FastAPI over Flask or Django?"
  - *Answer*: FastAPI provides native asynchronous concurrency, automated OpenAPI documentation, high performance with Starlette, and robust Pydantic data validation.
- **Q2**: "What happens during server boot?"
  - *Answer*: The `lifespan` handler initializes database tables and spawns an asynchronous daemon thread `_auto_ingest_missing` to fetch missing ticker data.
- **Q3**: "How is CORS handled?"
  - *Answer*: `CORSMiddleware` configured with `allow_origins=settings.cors_origins` allowing frontend communication on port 3000.
- **Q4**: "What is the prediction endpoint route?"
  - *Answer*: `GET /api/v1/predictions?symbol={symbol}&horizon={horizon}`.
- **Q5**: "How are errors communicated?"
  - *Answer*: Structured HTTP exceptions returning JSON payloads with appropriate 404 or 422 status codes.

### Chain 10: Frontend Integration
- **Q1**: "What frontend tech stack was selected?"
  - *Answer*: React 18 with Vite, Axios for HTTP communication, and Chart.js / Lucide icons for UI rendering.
- **Q2**: "How does the frontend handle loading states during model training?"
  - *Answer*: A loading spinner displays while the asynchronous `fetchPrediction()` promise resolves.
- **Q3**: "How are confidence intervals rendered?"
  - *Answer*: As upper and lower shaded boundary bands around the central projected forecast line.
- **Q4**: "How does the UI reflect model health?"
  - *Answer*: Displays a star rating (1–5 stars) and confidence badge derived from the test set MAPE and directional accuracy.
- **Q5**: "How is the app bundled for production?"
  - *Answer*: Multi-stage Dockerfile running `npm run build` and serving static assets through an Nginx web server.

---

## Project 2: Flood Risk Prediction (`ml-opsidian-genesis`)

### Chain 1: Domain-Specific Feature Engineering
- **Q1**: "Explain your `flood_susceptibility` feature."
  - *Answer*: `rainfall_7d_mm / (elevation_m + 1)`. Areas with intense weekly rainfall located at low elevations have the highest physical risk of flooding.
- **Q2**: "Why add `+ 1` to the denominator?"
  - *Answer*: To prevent division-by-zero errors for terrain at sea level ($0\text{m}$).
- **Q3**: "Explain `effective_drainage`."
  - *Answer*: `drainage_index * (1 - built_up_percent / 100)`. Urban concrete coverage degrades natural soil absorption, diminishing nominal drainage capacity.
- **Q4**: "Why compute missingness indicators?"
  - *Answer*: In geospatial telemetry, sensor data is often missing *not at random* (MNAR)—e.g., damaged rain gauges during storms indicate extreme weather.
- **Q5**: "What features used log transforms?"
  - *Answer*: Heavy-tailed distributions like `rainfall_7d_mm`, `distance_to_river_m`, and `population_density_per_km2`.

### Chain 2: Ensembling & Blending Architecture
- **Q1**: "Why ensemble LightGBM, XGBoost, and CatBoost?"
  - *Answer*: They use different tree building algorithms (leaf-wise vs. depth-wise vs. symmetric oblivious trees) and different categorical splitting mechanisms, producing diverse, uncorrelated prediction errors.
- **Q2**: "What is an Out-of-Fold (OOF) prediction?"
  - *Answer*: Predictions generated on the validation fold of each CV split by a model trained strictly on the other folds, ensuring leak-free meta-features.
- **Q3**: "Why use non-negative linear regression as the meta-learner?"
  - *Answer*: It finds the optimal linear blend of base models while preventing negative weights that overfit to fold variance.
- **Q4**: "Why did CatBoost get the highest weight (0.942)?"
  - *Answer*: CatBoost's target-based encoding and oblivious tree structure excelled on high-cardinality categorical features like `district` and `soil_type`.
- **Q5**: "How do you generate test predictions?"
  - *Answer*: Average the test predictions across all 5 folds for each model family, then blend them using the learned stacker weights.

### Chain 3: Target Transformation
- **Q1**: "Why apply `np.log1p` to the target?"
  - *Answer*: The flood risk score is strictly non-negative and right-skewed; `log1p` normalizes residual variance.
- **Q2**: "How do you invert predictions back to the original scale?"
  - *Answer*: Using `np.expm1()`.
- **Q3**: "Why did you clip the final predictions `np.clip(preds, 0, 1)`?"
  - *Answer*: Flood risk score is a bounded probability metric $[0, 1]$; clipping eliminates mathematical extrapolation outside valid domain limits.
- **Q4**: "What happens if you evaluate the competition metric on log-scale predictions?"
  - *Answer*: It would produce meaningless results because the competition metric assumes original-scale risk probabilities.
- **Q5**: "Did you transform the evaluation metric inside early stopping?"
  - *Answer*: Models used RMSE on log-transformed targets for gradient optimization, but fold validation printed the competition metric on inverted scale.

### Chain 4: Cross-Validation Strategy
- **Q1**: "What cross-validation scheme was used?"
  - *Answer*: 5-fold cross-validation with `shuffle=True, random_state=42`.
- **Q2**: "Why 5 folds instead of 10?"
  - *Answer*: 5 folds provide an optimal balance between validation reliability and computational training time across 3 deep GBDT models.
- **Q3**: "Did you consider GroupKFold?"
  - *Answer*: Yes, grouping by `district` would test generalization to unseen regions, but test data shared the same geographic districts as training data.
- **Q4**: "How do you verify fold stability?"
  - *Answer*: Monitoring the competition metric score across all 5 individual folds (consistently ~0.409 to ~0.420).
- **Q5**: "What would indicate validation leakage?"
  - *Answer*: If OOF score was 0.20 but test submission score was 0.45.

### Chain 5: Custom Competition Metric
- **Q1**: "What is the formula for your custom evaluation metric?"
  - *Answer*: $\frac{\text{MAE} + \text{RMSE}}{2} \times (1 + \max(0, 1 - R^2))$.
- **Q2**: "Why combine MAE and RMSE?"
  - *Answer*: MAE penalizes average linear deviation, while RMSE penalizes large catastrophic outlier misses.
- **Q3**: "What is the purpose of the $(1 + \max(0, 1 - R^2))$ term?"
  - *Answer*: It applies a severe multiplicative penalty if the model explains less variance than a horizontal mean baseline ($R^2 < 1.0$).
- **Q4**: "Can gradient boosting optimize this metric directly?"
  - *Answer*: No, because the $R^2$ penalty term is non-smooth; we use standard RMSE as the surrogate loss function and evaluate the proxy metric on validation folds.
- **Q5**: "How did Optuna utilize this metric?"
  - *Answer*: The Optuna objective function returned `np.mean(scores)` evaluated with `competition_metric_proxy`, guiding Bayesian hyperparameter search.

### Chain 6: Optuna Bayesian Optimization
- **Q1**: "Why Optuna instead of GridSearchCV?"
  - *Answer*: Grid search scales exponentially ($O(n^k)$); Optuna uses Tree-structured Parzen Estimators (TPE) to intelligently sample promising hyperparameter regions.
- **Q2**: "What did you tune for CatBoost?"
  - *Answer*: Depth, learning rate, L2 regularization, bagging temperature, and border count.
- **Q3**: "What was your pruning strategy?"
  - *Answer*: We used CatBoost's internal `early_stopping_rounds=50` to abort unpromising trees within individual trials.
- **Q4**: "Where were optimal parameters saved?"
  - *Answer*: In `configs/catboost_config.json`.
- **Q5**: "How many trials were executed?"
  - *Answer*: 50 trials.

### Chain 7: LightGBM Specifics
- **Q1**: "What hyperparameters were configured for LightGBM?"
  - *Answer*: `n_estimators=1000`, `learning_rate=0.03`, `num_leaves=63`, `min_child_samples=20`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=0.1`.
- **Q2**: "Why `num_leaves=63` instead of `max_depth`?"
  - *Answer*: LightGBM builds trees leaf-wise; setting `num_leaves` directly controls model complexity ($2^6 - 1 \approx 63$).
- **Q3**: "How did you prevent overfitting?"
  - *Answer*: Regularization parameters `reg_alpha=0.1`, `reg_lambda=0.1`, and early stopping at 50 rounds.
- **Q4**: "How were categorical features encoded for LightGBM?"
  - *Answer*: Using `LabelEncoder` integer mapping.
- **Q5**: "What was LightGBM's standalone OOF score?"
  - *Answer*: Metric: 0.4157, RMSE: 0.2371, $R^2$: 0.0138.

### Chain 8: XGBoost Specifics
- **Q1**: "What hyperparameters were configured for XGBoost?"
  - *Answer*: `n_estimators=1000`, `learning_rate=0.03`, `max_depth=6`, `min_child_weight=5`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=1.0`.
- **Q2**: "Why `min_child_weight=5`?"
  - *Answer*: To prevent the tree from creating leaf partitions with very few samples, acting as an anti-overfitting guardrail.
- **Q3**: "Why did XGBoost achieve lower $R^2$ than CatBoost?"
  - *Answer*: Standard label encoding does not preserve categorical relationship topology as effectively as CatBoost's target encoding.
- **Q4**: "What was XGBoost's standalone OOF score?"
  - *Answer*: Metric: 0.4354, RMSE: 0.2424.
- **Q5**: "Did it still help the ensemble?"
  - *Answer*: Yes, even with a small 2.3% blend weight, it provided error diversity that improved overall blended OOF to 0.4082.

### Chain 9: Data Cleaning & Preprocessing
- **Q1**: "How many missing values existed in `elevation_m`?"
  - *Answer*: Substantial missingness; handled via median imputation and binary missing indicator flags.
- **Q2**: "What columns were dropped before modeling?"
  - *Answer*: `record_id`, `flood_risk_score`, `place_name`, `reason_not_good_to_live`, and `is_synthetic`.
- **Q3**: "Why drop `place_name`?"
  - *Answer*: High cardinality text with excessive uniqueness that would cause extreme overfitting.
- **Q4**: "Why drop `is_synthetic`?"
  - *Answer*: It was a metadata artifact identifying artificially generated records rather than an environmental risk factor.
- **Q5**: "How many final engineered features were created?"
  - *Answer*: Expanded from 46 raw features to 65 clean features.

### Chain 10: Submission & Deployment Pipeline
- **Q1**: "Where is the submission file generated?"
  - *Answer*: In `../submissions/sub_ensemble_v1.csv`.
- **Q2**: "What columns does the submission contain?"
  - *Answer*: `record_id` and `flood_risk_score`.
- **Q3**: "What was the shape of test predictions?"
  - *Answer*: Exactly 5,300 rows matching `test.csv`.
- **Q4**: "How did you verify prediction validity?"
  - *Answer*: By inspecting descriptive statistics (`describe()`): mean 0.4778, min 0.3768, max 0.6191, with zero NaNs or negative numbers.
- **Q5**: "How would you package this for real-time disaster alerts?"
  - *Answer*: Export trained base models and stacker weights to ONNX runtimes; wrap in a Dockerized AWS Lambda or FastAPI service.

---

## Project 3: Online Retail Market Basket Analysis

### Chain 1: Market Segmentation
- **Q1**: "Why did you isolate United Kingdom transactions?"
  - *Answer*: The UK represented 91.4% of all transactions. Purchasing patterns differ by geography; mixing international wholesale orders would dilute local item affinity signals.
- **Q2**: "What was the row count reduction after filtering for the UK?"
  - *Answer*: From 541,909 total records down to 495,478 UK records.
- **Q3**: "Could you run market basket analysis on other countries?"
  - *Answer*: Yes, but small sample sizes (e.g., France or Germany with <2% volume) would require drastically lower support thresholds and could generate noisy rules.
- **Q4**: "How did you identify the country distribution?"
  - *Answer*: Executing `df['Country'].value_counts(normalize=True) * 100`.
- **Q5**: "What business assumption does regional isolation make?"
  - *Answer*: That supply chain inventory and retail promotions are localized to the UK domestic market.

### Chain 2: Data Cleaning & Noise Filtering
- **Q1**: "How did you identify cancelled transactions?"
  - *Answer*: Invoices beginning with `'C'`, identified using `df['InvoiceNo'].astype(str).str.startswith('C')`.
- **Q2**: "Why must cancelled transactions be removed?"
  - *Answer*: Cancellations contain negative quantities that reverse purchases; treating them as carts creates false association rules.
- **Q3**: "What noise descriptions were filtered out?"
  - *Answer*: `POSTAGE`, `DOTCOM POSTAGE`, `MANUAL`, `SAMPLES`, `AMAZON FEE`, `CRUK COMMISSION`, and `DISCOUNT`.
- **Q4**: "Why filter out `POSTAGE`?"
  - *Answer*: Postage appears in almost every online order; mining it would yield trivial, uninformative rules (`Item X -> POSTAGE`).
- **Q5**: "How did you handle string inconsistencies in product descriptions?"
  - *Answer*: `df['Description'].str.strip().str.upper()`, merging whitespace and capitalization variations.

### Chain 3: Transaction Cart Representation
- **Q1**: "How did you transform tabular rows into a basket matrix?"
  - *Answer*: `df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)`.
- **Q2**: "What do the rows and columns represent?"
  - *Answer*: Rows represent individual invoice carts; columns represent unique product SKUs.
- **Q3**: "Why convert quantities to binary values?"
  - *Answer*: Standard Association Rule Mining evaluates co-occurrence presence/absence, not the volume count purchased.
- **Q4**: "What was the final basket matrix shape?"
  - *Answer*: Several thousand invoices by several thousand unique items.
- **Q5**: "What is the sparsity of this matrix?"
  - *Answer*: Extremely sparse (>99% zeros), since a single cart contains only a tiny fraction of the retailer's total product catalog.

### Chain 4: Mathematical Metrics (Support, Confidence, Lift)
- **Q1**: "Define Support mathematically."
  - *Answer*: $\text{Support}(X \Rightarrow Y) = \frac{\text{Count}(X \cup Y)}{N}$, the proportion of total transactions containing both itemsets.
- **Q2**: "Define Confidence."
  - *Answer*: $\text{Confidence}(X \Rightarrow Y) = \frac{\text{Support}(X \cup Y)}{\text{Support}(X)} = P(Y \mid X)$, the conditional probability that $Y$ is bought given that $X$ was purchased.
- **Q3**: "Define Lift."
  - *Answer*: $\text{Lift}(X \Rightarrow Y) = \frac{\text{Support}(X \cup Y)}{\text{Support}(X) \times \text{Support}(Y)}$, the ratio of observed co-occurrence to expected co-occurrence under statistical independence.
- **Q4**: "What does a Lift of 15.77 mean?"
  - *Answer*: Customers who purchase the antecedent are 15.77 times more likely to purchase the consequent than a random shopper.
- **Q5**: "What does a Lift $< 1$ signify?"
  - *Answer*: Negative association (substitute goods), where purchasing item $X$ decreases the likelihood of purchasing item $Y$.

### Chain 5: Support Threshold Tuning
- **Q1**: "What happened when you ran Apriori at `min_support = 0.05`?"
  - *Answer*: Zero association rules were mined.
- **Q2**: "Why did 5% support yield zero rules?"
  - *Answer*: In wholesale gift retail with thousands of diverse items, individual item combinations rarely appear in more than 3–4% of all customer carts.
- **Q3**: "What threshold successfully yielded strong rules?"
  - *Answer*: `min_support = 0.03` with `min_confidence = 0.50` and `lift >= 1.20`.
- **Q4**: "What is the danger of lowering support too far (e.g., 0.001)?"
  - *Answer*: Combinatorial explosion: millions of spurious rules generated by rare items bought together once by chance.
- **Q5**: "How do you filter out spurious low-support rules?"
  - *Answer*: Enforce high confidence and lift thresholds, and validate statistical significance using Fisher's exact test.

### Chain 6: Apriori vs. FP-Growth Benchmarking
- **Q1**: "How does Apriori work internally?"
  - *Answer*: It utilizes the downward-closure property: all subsets of a frequent itemset must be frequent. It iteratively generates candidate $k$-itemsets from frequent $(k-1)$-itemsets and scans the entire dataset to verify support.
- **Q2**: "How does FP-Growth differ?"
  - *Answer*: It compresses transactions into a prefix tree (FP-Tree) and mines frequent patterns directly by conditional tree decomposition without candidate generation.
- **Q3**: "What did your `compare.py` script measure?"
  - *Answer*: Runtime execution in seconds for both algorithms at identical `min_support` levels.
- **Q4**: "Which algorithm was faster in your benchmarks?"
  - *Answer*: FP-Growth was significantly faster, especially as support was lowered.
- **Q5**: "Did both algorithms return identical frequent itemsets?"
  - *Answer*: Yes, `len(frequent_apriori) == len(frequent_fp)` returned `True`.

### Chain 7: Discovered Business Rules
- **Q1**: "What was your top mined rule?"
  - *Answer*: `{'GREEN REGENCY TEACUP AND SAUCER'} -> {'PINK REGENCY TEACUP AND SAUCER'}` with 82.05% confidence and 15.77 lift.
- **Q2**: "What does the Regency Teacup rule indicate commercially?"
  - *Answer*: Customers purchase these items as matching collectible sets rather than standalone individual cups.
- **Q3**: "What was the Gardeners set rule?"
  - *Answer*: `{'GARDENERS KNEELING PAD CUP OF TEA'} -> {'GARDENERS KNEELING PAD KEEP CALM'}` with 72.13% confidence and 14.39 lift.
- **Q4**: "What was the Alarm Clock rule?"
  - *Answer*: `{'ALARM CLOCK BAKELIKE GREEN'} -> {'ALARM CLOCK BAKELIKE RED'}` with 64.27% confidence and 12.38 lift.
- **Q5**: "Were any multi-item antecedent rules mined?"
  - *Answer*: At 0.03 support, rules were primarily 2-item pairs due to wholesale basket diversity.

### Chain 8: Actionable Commercial Recommendations
- **Q1**: "How do you translate teacup affinity into revenue?"
  - *Answer*: Create a pre-packaged "Regency Trio Bundle" (Green, Pink, Roses) at a 5% discount, boosting average order value (AOV).
- **Q2**: "How would you optimize e-commerce web placement?"
  - *Answer*: When a customer views the Green Alarm Clock, dynamically render the Red Alarm Clock as "Frequently Bought Together" on the product detail page.
- **Q3**: "How does this optimize physical warehouse logistics?"
  - *Answer*: Place the Gardener Kneeling Pads in adjacent pick-bins, reducing warehouse picker travel time during fulfillment.
- **Q4**: "How could you use this for inventory restocking?"
  - *Answer*: If Green Teacups are reordered, automatically trigger a replenishment order for Pink Teacups to avoid partial-stock churn.
- **Q5**: "How would you evaluate if these business changes worked?"
  - *Answer*: Run an A/B test on the website tracking cart conversion rate and bundle attachment rate against a control group.

### Chain 9: Technical Libraries & Environment
- **Q1**: "What library provided the mining algorithms?"
  - *Answer*: `mlxtend` (`mlxtend.frequent_patterns.apriori`, `fpgrowth`, `association_rules`).
- **Q2**: "Why not use `scikit-learn`?"
  - *Answer*: `scikit-learn` does not natively implement association rule mining algorithms like Apriori or FP-Growth.
- **Q3**: "What version of Python was targeted?"
  - *Answer*: Python 3.8+ as specified in `requirements.txt`.
- **Q4**: "How were figures exported?"
  - *Answer*: Visualizations were saved to the `figures/` directory using Matplotlib.
- **Q5**: "How are large raw files handled in Git?"
  - *Answer*: Excluded via `.gitignore` to keep repository clone sizes small.

### Chain 10: Limitations & Scalability
- **Q1**: "Does standard market basket analysis consider transaction sequence?"
  - *Answer*: No, it treats a transaction as an unordered set of items. Sequential purchase behavior requires Sequential Pattern Mining (e.g., GSP or PrefixSpan).
- **Q2**: "Does it consider pricing or profit margins?"
  - *Answer*: No, it treats all item co-occurrences equally regardless of whether an item generates $1 or $1000 margin.
- **Q3**: "How would you incorporate profit into rule mining?"
  - *Answer*: High-Utility Itemset Mining (HUIM), weighting itemsets by unit profit margin.
- **Q4**: "How would you deploy this model to serve live e-commerce recommendations?"
  - *Answer*: Precompute rules offline, index antecedent product IDs in Redis, and query matching consequents in $O(1)$ time during user checkout.
- **Q5**: "How often should rules be re-mined?"
  - *Answer*: Weekly or monthly, accounting for retail seasonality and catalog shifts.

---

## Project 4: Medical Cost Regression & RainTomorrow Classification

### Chain 1: Medical Cost Regression Basics
- **Q1**: "What is the objective of the Medical Cost project?"
  - *Answer*: To predict individual health insurance charges from demographic and lifestyle variables using OLS linear regression.
- **Q2**: "What feature had the highest correlation with `charges`?"
  - *Answer*: `smoker` status (smokers pay vastly higher premiums).
- **Q3**: "How did you encode the `smoker` column?"
  - *Answer*: `medical_df['smoker'].map({'yes': 1, 'no': 0})`.
- **Q4**: "How was age modeled in single-feature regression?"
  - *Answer*: As a linear predictor: $\text{charges} = w \cdot \text{age} + b$ on the non-smoker cohort.
- **Q5**: "What was the limitation of single-feature regression?"
  - *Answer*: High residual variance because it failed to account for BMI, smoking habits, and age-BMI interaction effects.

### Chain 2: Multi-Feature Regression & Categorical Traps
- **Q1**: "What features were used in multi-feature regression?"
  - *Answer*: `age`, `bmi`, `smoker_code`, `sex_code`, and regional indicator columns.
- **Q2**: "What is the dummy variable trap?"
  - *Answer*: Perfect multicollinearity occurring when all dummy categories plus an intercept are included in linear regression, making $(X^T X)$ singular.
- **Q3**: "Did your code exhibit the dummy variable trap?"
  - *Answer*: Yes, in `3_Categorical_features.ipynb`, all 4 region dummies (`northeast`, `northwest`, `southeast`, `southwest`) were included in the feature matrix.
- **Q4**: "How does scikit-learn handle the dummy variable trap without crashing?"
  - *Answer*: `sklearn.linear_model.LinearRegression` uses SVD decomposition (`scipy.linalg.lstsq`), which computes pseudo-inverses and masks singular matrix errors, but results in unstable coefficients.
- **Q5**: "How should dummy variables be created properly?"
  - *Answer*: `pd.get_dummies(df, drop_first=True)` or `OneHotEncoder(drop='first')`.

### Chain 3: RainTomorrow Data Ingestion & Memory Management
- **Q1**: "What was the memory challenge with `weatherAUS.csv`?"
  - *Answer*: 145,000 rows with 23 features caused memory pressure and slow execution on local machines during one-hot encoding.
- **Q2**: "How did `data_preprocessing.py` solve this?"
  - *Answer*: Explicitly invoked `del` on intermediate DataFrames followed by `gc.collect()`, and exported CSV splits in chunks (`chunksize=10000`).
- **Q3**: "How was the `Date` column transformed?"
  - *Answer*: Converted to datetime, extracted `Month = Date.dt.month` to capture seasonal weather patterns, and dropped the raw string `Date` column.
- **Q4**: "Why drop `Date` after extracting `Month`?"
  - *Answer*: Leaving raw string dates would result in thousands of unique high-cardinality levels if one-hot encoded, causing memory explosion.
- **Q5**: "How were rows with missing target values handled?"
  - *Answer*: Dropped immediately: `raw_df.dropna(subset=["RainToday", "RainTomorrow"])`.

### Chain 4: Imputation & Scaling in Weather Pipeline
- **Q1**: "How were missing numerical values imputed?"
  - *Answer*: Using column-wise medians: `raw_df[col].fillna(median_val)`.
- **Q2**: "Why median instead of mean?"
  - *Answer*: Meteorological variables like rainfall have highly skewed, non-Gaussian distributions where the mean is distorted by extreme storm outliers.
- **Q3**: "What scaler was used in `data_preprocessing.py`?"
  - *Answer*: `MinMaxScaler()`, compressing numeric features to $[0, 1]$.
- **Q4**: "What scaler was used in `model.py`?"
  - *Answer*: `StandardScaler()`.
- **Q5**: "Why is applying both MinMaxScaler and StandardScaler bad practice?"
  - *Answer*: It is redundant, wastes compute, and standardizing one-hot encoded dummy columns destroys their interpretable binary (0/1) scale.

### Chain 5: Train/Val/Test Split Strategy
- **Q1**: "How was the weather dataset partitioned?"
  - *Answer*: An 80/20 train/test split, followed by an 80/20 train/validation split on the training portion (yielding 60% Train, 20% Val, 20% Test).
- **Q2**: "Why stratify on `RainTomorrow`?"
  - *Answer*: Rain events occur in only ~22% of days in Australia. Stratification ensures each split maintains identical positive/negative class proportions.
- **Q3**: "Is random splitting appropriate for weather forecasting?"
  - *Answer*: No. Weather is continuous over time; random splitting allows yesterday's weather to be in the test set while today's is in training, causing temporal leakage.
- **Q4**: "What splitting strategy should have been used instead?"
  - *Answer*: Chronological time-series splitting (e.g. train on 2008–2015 data, validate on 2016, test on 2017).
- **Q5**: "What was the final shape of the training split?"
  - *Answer*: Approximately 84,000 training records.

### Chain 6: Logistic Regression Classification
- **Q1**: "What algorithm was used in `model.py`?"
  - *Answer*: `sklearn.linear_model.LogisticRegression(C=1.0, solver='liblinear', max_iter=1000)`.
- **Q2**: "What does the hyperparameter `C` do?"
  - *Answer*: `C` is the inverse of regularization strength ($C = 1/\lambda$). Smaller values specify stronger L2 penalty on coefficient weights.
- **Q3**: "Why use the `liblinear` solver?"
  - *Answer*: `liblinear` is a robust coordinate descent algorithm well-suited for medium-sized binary classification datasets with sparse or dense features.
- **Q4**: "How does Logistic Regression predict probabilities?"
  - *Answer*: By passing linear combinations through the sigmoid function: $\sigma(z) = \frac{1}{1 + e^{-z}}$.
- **Q5**: "What is the decision threshold used by `model.predict()`?"
  - *Answer*: A default threshold of $p \ge 0.50$.

### Chain 7: Evaluation Metrics (Accuracy vs. ROC-AUC)
- **Q1**: "What was the accuracy achieved on the weather test set?"
  - *Answer*: ~85%.
- **Q2**: "Why is 85% accuracy misleading for RainTomorrow?"
  - *Answer*: Since it does not rain on ~78% of days, a trivial baseline predicting "No Rain" every day achieves 78% accuracy with zero predictive skill.
- **Q3**: "What metric better evaluates performance under this class imbalance?"
  - *Answer*: ROC-AUC (Receiver Operating Characteristic - Area Under Curve), which evaluates true positive vs. false positive trade-offs across all decision thresholds.
- **Q4**: "What was the ROC-AUC score achieved?"
  - *Answer*: ~0.86.
- **Q5**: "What does the classification report reveal about the 'Yes' class?"
  - *Answer*: Precision is high (~75%), but Recall is lower (~50%), meaning the model misses half of the actual rainy days.

### Chain 8: Class Imbalance Remedies
- **Q1**: "How could you modify `LogisticRegression` to improve minority class recall?"
  - *Answer*: Set `class_weight='balanced'`, which inversely weights samples by class frequencies during loss calculation.
- **Q2**: "What happens to Precision and Recall when you use `class_weight='balanced'`?"
  - *Answer*: Recall on rainy days increases significantly, but Precision drops (more false alarms).
- **Q3**: "How could you adjust the classification threshold manually?"
  - *Answer*: Instead of `model.predict()`, use `(model.predict_proba(X)[:, 1] >= 0.30).astype(int)` to lower the decision boundary.
- **Q4**: "What resampling methods could be applied?"
  - *Answer*: SMOTE (Synthetic Minority Over-sampling Technique) or random undersampling of the majority dry days.
- **Q5**: "Why avoid oversampling before splitting?"
  - *Answer*: Oversampling the entire dataset before splitting duplicates synthetic samples into both train and test partitions, causing massive leakage.

### Chain 9: ROC Curve & Visualization
- **Q1**: "What does `plot_roc()` in `model.py` do?"
  - *Answer*: Computes false positive rates and true positive rates using `roc_curve(y_test, y_proba)` and plots them against a diagonal random guess line.
- **Q2**: "Where is the ROC plot saved?"
  - *Answer*: Saved to disk as `roc_curve.png`.
- **Q3**: "What does the diagonal dashed line on the ROC plot represent?"
  - *Answer*: A random coin-flip classifier with $\text{AUC} = 0.50$.
- **Q4**: "What does an ROC curve bowing towards the top-left indicate?"
  - *Answer*: Superior true positive rates achieved at very low false positive rates (high discrimination ability).
- **Q5**: "Can ROC-AUC be calculated on hard class predictions?"
  - *Answer*: No, it requires predicted class probabilities `predict_proba(X)[:, 1]`.

### Chain 10: Comparison: Linear vs. Logistic Regression
- **Q1**: "What is the fundamental mathematical difference between Project 4A and 4B?"
  - *Answer*: Linear regression models continuous unbounded targets ($y \in \mathbb{R}$) using squared loss; Logistic regression models bounded discrete class probabilities ($y \in \{0, 1\}$) using cross-entropy log-loss.
- **Q2**: "Why can't you use Linear Regression for RainTomorrow?"
  - *Answer*: Linear regression outputs predictions outside $[0, 1]$, violates homoscedasticity, and treats categorical outcomes as continuous distances.
- **Q3**: "How do the interpretations of coefficients differ?"
  - *Answer*: In Linear Regression, $\beta_j$ is the direct unit change in $y$. In Logistic Regression, $e^{\beta_j}$ represents the multiplicative odds ratio change.
- **Q4**: "How do assumptions regarding residuals differ?"
  - *Answer*: Linear regression assumes normally distributed residuals with constant variance; Logistic regression assumes a Bernoulli distribution of errors.
- **Q5**: "Which model is more sensitive to outliers?"
  - *Answer*: Linear regression, because OLS squares error terms $(y - \hat{y})^2$, heavily skewing the hyperplane toward distant outliers.

---

# PART 13 — HARD QUESTIONS

1. **"Why are you confident that using `pd.merge_asof(direction='backward')` eliminates all data leakage in your macroeconomic pipeline?"**  
   *Answer*: While it prevents lookahead leakage by guaranteeing daily prices only join with macroeconomic figures announced on or before trading date $t$, line 61 executes `ffill().bfill()`. The `bfill()` on leading rows *does* introduce leakage for historical trading days prior to the first central bank release. In production, I would drop those leading dates or replace them with historical baseline constants.
2. **"Why is random K-fold cross-validation technically invalid for time-series forecasting, and why did you use an 80/20 chronological split instead?"**  
   *Answer*: Random K-fold shuffles future data into training folds to predict past validation folds, violating temporal causality and inflating performance metrics. An 80/20 chronological split preserves temporal order ($t < t_{\text{val}}$).
3. **"In your Flood ensemble, why did you choose non-negative linear regression for stacking instead of training an XGBoost meta-model?"**  
   *Answer*: Training a non-linear GBDT meta-model on OOF predictions with only 3 features overfits rapidly to the validation fold distributions. A non-negative linear model acts as a convex blend, stabilizing predictions and preventing extreme out-of-domain weights.
4. **"Why does CatBoost dominate your Flood ensemble with a 94.2% weight over LightGBM and XGBoost?"**  
   *Answer*: Flood risk is geographically clustered. CatBoost's ordered target statistics effectively encode high-cardinality spatial categories (like `district` and `soil_type`) without data leakage, whereas standard integer label encoding used for LightGBM and XGBoost imposes artificial numerical order on nominal features.
5. **"In your Market Basket Analysis, why can't you conclude that buying Green Teacups *causes* customers to buy Pink Teacups?"**  
   *Answer*: Association rule mining discovers statistical co-occurrence and conditional probability ($\text{Lift} > 1$), not causal relationships. Both items could be driven by an unobserved confounder, such as an affinity for antique Victorian tea sets.
6. **"Explain the mathematical cause and consequence of the Dummy Variable Trap in your Medical Cost regression."**  
   *Answer*: The cause is including all 4 region indicators plus an intercept vector of ones, creating an exact linear dependency: $\mathbf{x}_{\text{NE}} + \mathbf{x}_{\text{NW}} + \mathbf{x}_{\text{SE}} + \mathbf{x}_{\text{SW}} = \mathbf{1}$. Consequently, the Gram matrix $(X^T X)$ is singular with a determinant of zero, meaning standard OLS normal equations $(X^T X)^{-1} X^T y$ cannot be inverted without regularization or pseudo-inverses.
7. **"What happens to SHAP values if two input features are 99% collinear?"**  
   *Answer*: Standard `TreeExplainer` splits credit arbitrarily between the collinear features depending on which feature was chosen first at each tree node split, creating variance in individual feature attributions even though their joint impact is stable.
8. **"Why is `StandardScaler` inappropriate when applied directly to one-hot encoded binary columns?"**  
   *Answer*: One-hot features are discrete indicator variables where 0 means absence and 1 means presence. Subtracting the mean and dividing by the standard deviation converts them into continuous negative and positive values, destroying their interpretability as binary switch variables.
9. **"In CSE, why did you forecast the price at day $t+30$ and linearly interpolate, rather than autoregressively rolling 1-day predictions 30 times?"**  
   *Answer*: Iterated 1-step autoregressive rollouts compound prediction errors exponentially over 30 steps ($e_{t+30} \gg e_{t+1}$) and require simulating all 40+ technical indicators 30 days into the future. Direct 30-day point forecasting with linear trajectory interpolation provides a bounded, stable target path.
10. **"If your production server restarts, what happens to your CSE in-memory forecast cache, and how should it be redesigned?"**  
    *Answer*: It is completely wiped, forcing subsequent user requests to trigger slow re-training runs. In production, forecast results and trained model weights should be persisted in Redis with time-to-live (TTL) expiry.

---

# PART 14 — PROJECT MASTERY CHECKLISTS

### Project 1: Colombo Stock Exchange (CSE)
- [ ] Can sketch the complete system architecture (FastAPI, SQLite, React, Docker).
- [ ] Can explain how `align_to_trading_days` uses `pd.merge_asof(direction='backward')`.
- [ ] Can identify the potential leakage in `calendar.py` Line 61 (`bfill()`).
- [ ] Can explain the exact target definition: `close.shift(-30)`.
- [ ] Can explain the model selection score formula and the baseline penalty (+1000.0).
- [ ] Can explain the hyperparameters of `XGBRegressor` (`n_estimators=200`, `max_depth=5`, `learning_rate=0.05`).
- [ ] Can explain how `SARIMAX(1,1,1)` utilizes exogenous technical indicators (`rsi`, `macd`, `volatility`).
- [ ] Can explain how `SHAPExplainer` unwraps `TreeExplainer` and converts output to LKR currency impact.
- [ ] Can explain the rule-based scoring of `TechnicalSignalEngine` and its $\pm 2\%$ price guardrail.
- [ ] Can explain the Granger Causality hypothesis test in `causality.py`.

### Project 2: Flood Risk Prediction
- [ ] Can explain the feature engineering formulas: `flood_susceptibility`, `effective_drainage`, and `river_elevation_risk`.
- [ ] Can explain why `train_medians` must be computed on `train` and applied to `test`.
- [ ] Can explain the custom competition evaluation metric and its $(1 + \max(0, 1 - R^2))$ penalty.
- [ ] Can explain how 5-fold cross-validation was structured and how OOF arrays were populated.
- [ ] Can explain why CatBoost received 94.2% of the ensemble stacking weight.
- [ ] Can explain why `LinearRegression(positive=True, fit_intercept=False)` was chosen as the meta-learner.
- [ ] Can explain the target log transform `np.log1p` and inverse transform `np.expm1`.
- [ ] Can explain how Optuna was configured with 50 trials in `temp_run.py`.
- [ ] Can explain the bug in `X_test[col].map(lambda x: x if x in le.classes_ else 'Missing')`.
- [ ] Can explain why final predictions were clipped to $[0, 1]$.

### Project 3: Online Retail Market Basket Analysis
- [ ] Can explain why the UK market segment (91.4%) was isolated.
- [ ] Can explain how cancellations (`InvoiceNo.str.startswith('C')`) and administrative fees were purged.
- [ ] Can explain how `groupby().unstack().fillna(0)` creates the binary cart matrix.
- [ ] Can write the mathematical formulas for Support, Confidence, and Lift.
- [ ] Can explain why `min_support=0.05` yielded zero rules and why 0.03 was chosen.
- [ ] Can explain why `basket.astype(bool)` is required by modern `mlxtend`.
- [ ] Can explain the algorithmic difference between Apriori candidate generation and FP-Tree projection.
- [ ] Can cite the exact findings: Regency Teacups (82.05% confidence, 15.77 lift).
- [ ] Can translate association rules into commercial bundling and warehouse inventory bin layouts.
- [ ] Can explain how association rules would be indexed in Redis for real-time checkout recommendations.

### Project 4: Medical Cost Regression & RainTomorrow Classification
- [ ] Can explain single vs. multi-variable regression on `medical.csv`.
- [ ] Can identify and explain the Dummy Variable Trap in `3_Categorical_features.ipynb`.
- [ ] Can explain why smoking status dominates medical insurance charges.
- [ ] Can identify the severe data leakage in `data_preprocessing.py` (scaling and imputing before splitting).
- [ ] Can explain the memory optimization techniques (`gc.collect()`, chunked export).
- [ ] Can explain why `Date` was decomposed into `Month` and why raw string dates cause memory explosion.
- [ ] Can explain why random splitting is flawed for weather forecasting compared to chronological splitting.
- [ ] Can explain why 85% accuracy is misleading due to class imbalance (~22% rain days).
- [ ] Can explain the ROC-AUC metric and how `roc_curve.png` was generated.
- [ ] Can explain how `class_weight='balanced'` modifies logistic regression optimization.

---

# FINAL OUTPUT 1 — TOP 50 MUST-KNOW CODEBASE QUESTIONS

1. What does `pd.merge_asof(direction='backward')` do in `calendar.py`?
2. Where does data leakage occur in `calendar.py`? (Line 61: `bfill()`).
3. How is the target variable constructed in CSE `dataset.py`? (`close.shift(-30)`).
4. Why is chronological splitting used instead of `train_test_split(shuffle=True)` in CSE?
5. How does the CSE model tournament select the winning model?
6. What is the baseline penalty in `trainer.py`? (+1000.0 if RMSE > 1.1x baseline).
7. What hyperparameters are used for XGBoost in CSE?
8. How does `XGBoostModel.predict()` generate 30 future price points? (Linear interpolation from point forecast).
9. Why use `order=(1,1,1)` in SARIMAX? (To handle non-stationarity of raw prices).
10. What exogenous features are passed to SARIMAX? (`rsi`, `macd`, `sma_20`, `sma_50`, `volatility`).
11. How does `SHAPExplainer` compute local feature attributions? (Using `shap.TreeExplainer`).
12. What fallback explainer is used if `TreeExplainer` fails? (`shap.Explainer` with predict lambda).
13. In what units are SHAP values expressed in CSE? (LKR price impact).
14. What does `TechnicalSignalEngine` calculate? (Technical momentum score from -5 to +5).
15. What guardrail does `TechnicalSignalEngine` apply to the ML prediction? (±2% price adjustment).
16. How does `PredictionService` cache forecasts? (In-memory dict keyed on `(symbol, date)`).
17. What database is used in CSE and where is it configured? (SQLite `cse.db` via SQLAlchemy in `connection.py`).
18. What background thread runs during FastAPI server startup? (`_auto_ingest_missing` in `main.py`).
19. How does `causality.py` test if macro indicators lead stock returns? (Granger Causality SSR $\chi^2$ test).
20. What features were engineered in the Flood project? (`flood_susceptibility`, `effective_drainage`, `river_elevation_risk`).
21. Why add `+ 1` to denominators in ratio features? (To prevent division-by-zero).
22. How are missing values imputed leak-free in `04_ensemble_model.ipynb`? (Learning medians on train, applying to test).
23. Why apply `np.log1p` to the target in Flood prediction? (To normalize right-skewed non-negative risk scores).
24. How was the competition metric defined in `competition_metric_proxy`?
25. What base models are used in the Flood ensemble? (LightGBM, XGBoost, CatBoost).
26. How are out-of-fold (OOF) predictions generated? (Predicting validation folds across 5 CV splits).
27. Why use `LinearRegression(positive=True, fit_intercept=False)` for stacking? (Constrained convex non-negative blend).
28. What blend weights were learned in the Flood ensemble? (LGBM: 0.035, XGB: 0.023, CatBoost: 0.942).
29. Why did CatBoost receive the highest ensemble weight? (Superior handling of categorical geospatial features).
30. What bug exists in `X_test[col].map(lambda x: x if x in le.classes_ else 'Missing')`? (Fails if 'Missing' is not in training classes).
31. How was CatBoost tuned in `temp_run.py`? (Optuna Bayesian optimization over 50 trials).
32. Why clip final flood predictions to $[0, 1]$? (To enforce valid probability boundaries).
33. Why isolate UK transactions in Market Basket Analysis? (91.4% data density; homogeneous consumer behavior).
34. How are cancelled transactions filtered out in MBA? (`InvoiceNo.str.startswith('C')`).
35. What administrative noise terms were stripped in `analysis.ipynb`? (`POSTAGE`, `MANUAL`, `AMAZON FEE`, etc.).
36. How is the binary transaction matrix created from transaction rows? (`groupby().unstack().fillna(0).applymap()`).
37. Why convert the basket matrix to `bool` in `compare.py`? (API requirement of modern `mlxtend`).
38. What is the mathematical definition of Lift? ($\text{Support}(X \cup Y) / (\text{Support}(X) \times \text{Support}(Y))$).
39. What does a Lift of 15.77 indicate for the Regency Teacups rule? (15.77x higher purchase affinity than independence).
40. Why did Apriori yield zero rules at 5% support? (Catalog diversity; itemsets rarely appear in >3% of carts).
41. What is the computational difference between Apriori and FP-Growth? (Candidate generation vs. FP-Tree projection).
42. How does the Regency Teacup finding translate into retail business strategy? (Product bundling at a 5% discount).
43. What is the Dummy Variable Trap in `3_Categorical_features.ipynb`? (Including all 4 regions causing perfect collinearity).
44. How does smoking status affect insurance charges in Medical Cost regression? (Strongest positive linear coefficient).
45. Where does severe data leakage occur in `weatherAUS` `data_preprocessing.py`? (Scaling/imputation before splitting).
46. Why was `Date` converted to `Month` in the weather dataset? (To capture seasonality without 140k one-hot columns).
47. How were memory crashes prevented in `data_preprocessing.py`? (Explicit `del` and `gc.collect()`).
48. Why is 85% accuracy misleading for `RainTomorrow`? (Class imbalance: dry days account for 78% of data).
49. What solver was used for Logistic Regression and why? (`liblinear`, suitable for medium sparse datasets).
50. What does the ROC-AUC score of 0.86 signify in the weather model? (Strong discrimination ability across all classification thresholds).

---

# FINAL OUTPUT 2 — TOP 30 DEBUGGING PROBLEMS

1. **Problem**: CSE forecast accuracy jumps to 99.8%.  
   - *Investigation*: Inspect `dataset.py` lag features.  
   - *Cause*: Negative shift used for feature lags (`shift(-1)` instead of `shift(1)`), leaking future price into input row.  
   - *Fix*: Enforce positive shifts for historical features.
2. **Problem**: `SARIMAXModel.train()` hangs or raises `LinAlgError: Non-stationary starting autoregressive parameters`.  
   - *Investigation*: Inspect price target series stationarity.  
   - *Cause*: Raw equity price series underwent a massive volatility spike.  
   - *Fix*: Set `enforce_stationarity=False, enforce_invertibility=False` and differencing $d=1$.
3. **Problem**: `SHAPExplainer` throws `Exception: C++ tree loading error`.  
   - *Investigation*: Check XGBoost and SHAP package versions.  
   - *Cause*: Incompatible C++ serialization between recent XGBoost and SHAP.  
   - *Fix*: Utilize the fallback model-agnostic `shap.Explainer` wrapper implemented in lines 88–101.
4. **Problem**: `KeyError: 'inflation'` in `calendar.py`.  
   - *Investigation*: Inspect CBSL macro CSV columns.  
   - *Cause*: Column naming mismatch (e.g. `Inflation_CCPI` vs `inflation`).  
   - *Fix*: Add column name normalization step before merge.
5. **Problem**: CSE API returns `500 Internal Server Error` when user requests a new ticker.  
   - *Investigation*: Check SQLite database records for that symbol.  
   - *Cause*: No rows exist in `cse.db`, triggering `ValueError` in `prediction_service.py` Line 175.  
   - *Fix*: Catch `ValueError`, return 404 with instructions to trigger ingestion endpoint first.
6. **Problem**: CatBoost throws `CatBoostError: Invalid float value 'Western'`.  
   - *Investigation*: Inspect feature types passed to CatBoost.  
   - *Cause*: `district` column was not included in `cat_features` list.  
   - *Fix*: Ensure all string columns are in `CAT_FEATURES`.
7. **Problem**: `LabelEncoder.transform()` crashes with `ValueError: y contains previously unseen labels: 'Missing'`.  
   - *Investigation*: Trace line 218 of `04_ensemble_model.ipynb`.  
   - *Cause*: Test set contains unseen category, mapped to `'Missing'`, but training set had no `'Missing'` label.  
   - *Fix*: Pre-populate training categorical vocabulary with `'Missing'`.
8. **Problem**: Stacker weights sum to a negative number.  
   - *Investigation*: Check `LinearRegression` parameters in `04_ensemble_model.ipynb`.  
   - *Cause*: Omitted `positive=True`.  
   - *Fix*: `LinearRegression(positive=True, fit_intercept=False)`.
9. **Problem**: Predictions for `flood_risk_score` in test submission are negative (e.g. -0.14).  
   - *Investigation*: Inspect prediction pipeline after meta-model.  
   - *Cause*: Did not invert `log1p` or forgot `np.clip()`.  
   - *Fix*: `np.clip(np.expm1(preds), 0, 1)`.
10. **Problem**: Optuna study crashes midway with `TypeError: unhashable type`.  
    - *Investigation*: Check parameter dictionary in objective function.  
    - *Cause*: Passing a list instead of a tuple to CatBoost config.  
    - *Fix*: Convert lists to tuples or JSON serializable values.
11. **Problem**: `Apriori` in `compare.py` throws `ValueError: The input DataFrame must contain boolean values`.  
    - *Investigation*: Check DataFrame dtypes.  
    - *Cause*: Basket matrix is int64 (0/1) instead of bool.  
    - *Fix*: `basket = basket.astype(bool)`.
12. **Problem**: `association_rules()` returns an empty DataFrame.  
    - *Investigation*: Check `min_support` and `min_threshold`.  
    - *Cause*: `min_support=0.05` is too high for diverse retail data.  
    - *Fix*: Lower support to 0.03 or 0.02.
13. **Problem**: Market basket analysis produces rule `Item A -> POSTAGE` with 95% confidence.  
    - *Investigation*: Inspect input transaction descriptions.  
    - *Cause*: Failed to strip administrative fee tokens.  
    - *Fix*: Filter noise items in `analysis.ipynb`: `df = df[~df['Description'].isin(noise_words)]`.
14. **Problem**: Unstack operation crashes with `MemoryError` in `analysis.ipynb`.  
    - *Investigation*: Inspect memory usage of `df.groupby().unstack()`.  
    - *Cause*: International transactions included, producing massive sparse matrix.  
    - *Fix*: Filter for UK market *before* pivoting.
15. **Problem**: Duplicate columns in basket matrix (e.g. `WHITE HANGING HEART` and `WHITE HANGING HEART `).  
    - *Investigation*: Check string whitespace.  
    - *Cause*: Trailing whitespace in descriptions.  
    - *Fix*: `df['Description'] = df['Description'].str.strip().str.upper()`.
16. **Problem**: `LinearRegression` in `3_Categorical_features.ipynb` outputs wild coefficients ($\pm 10^{12}$).  
    - *Investigation*: Check condition number of $(X^T X)$.  
    - *Cause*: Dummy variable trap (all 4 region dummies included).  
    - *Fix*: Drop one dummy variable (`drop_first=True`).
17. **Problem**: Medical cost regression predicts negative charges for healthy young patients.  
    - *Investigation*: Inspect model formulation.  
    - *Cause*: Unconstrained linear regression with negative intercept.  
    - *Fix*: Fit on `np.log(charges)` or use non-negative least squares.
18. **Problem**: `data_preprocessing.py` crashes server with OS `Out of Memory (OOM)`.  
    - *Investigation*: Trace Line 57 of weather script.  
    - *Cause*: `OneHotEncoder(sparse_output=False)` creating huge dense array in RAM.  
    - *Fix*: Set `sparse_output=True` and process in chunks.
19. **Problem**: `model.py` accuracy is 85%, but model fails to predict any rainy days.  
    - *Investigation*: Check confusion matrix and recall.  
    - *Cause*: Class imbalance; model predicts majority class ("No Rain").  
    - *Fix*: Set `class_weight='balanced'` in `LogisticRegression`.
20. **Problem**: `StandardScaler` throws warning `Cannot center sparse matrix: use with_mean=False`.  
    - *Investigation*: Inspect input to `preprocess()`.  
    - *Cause*: Passing a scipy sparse matrix to `StandardScaler(with_mean=True)`.  
    - *Fix*: `StandardScaler(with_mean=False)`.
21. **Problem**: Data leakage detected in test metrics of weather model.  
    - *Investigation*: Trace lines 51–66 in `data_preprocessing.py`.  
    - *Cause*: Imputation and scaling executed before `train_test_split()`.  
    - *Fix*: Split raw data first, fit transformations strictly on training set.
22. **Problem**: SQLite database is locked (`OperationalError: database is locked`).  
    - *Investigation*: Check concurrent API requests in CSE.  
    - *Cause*: SQLite locks entire file during write operations.  
    - *Fix*: Increase timeout or migrate to PostgreSQL.
23. **Problem**: `FastAPI` startup thread crashes silently.  
    - *Investigation*: Inspect `_auto_ingest_missing` in `main.py`.  
    - *Cause*: Uncaught exception inside background thread.  
    - *Fix*: Wrap thread body in `try...except Exception as exc: logger.error(...)`.
24. **Problem**: Technical signal engine returns `status: "Unknown"` for all stocks.  
    - *Investigation*: Check historical row count returned by DB.  
    - *Cause*: Fewer than 50 rows returned; SMA-50 cannot be calculated.  
    - *Fix*: Ingest at least 100 historical trading days.
25. **Problem**: `GrangerCausalityTester` throws `ValueError: array must not contain Infs or NaNs`.  
    - *Investigation*: Check `df[[target, var]]` in `causality.py`.  
    - *Cause*: Missing values in macro series.  
    - *Fix*: Apply `dropna()` on paired columns before testing.
26. **Problem**: Test set predictions produce all identical values for SARIMAX.  
    - *Investigation*: Trace `evaluate()` in `sarimax.py`.  
    - *Cause*: `new_fit.apply()` failed, triggering fallback line 182: `y_pred = np.full_like(y_true, last_val)`.  
    - *Fix*: Inspect exogenous matrix alignment.
27. **Problem**: CatBoost early stopping triggers at iteration 50 with poor score.  
    - *Investigation*: Check validation set target transform.  
    - *Cause*: Evaluated raw targets against log-transformed predictions.  
    - *Fix*: Pass `eval_set=(Xval, np.log1p(yval))`.
28. **Problem**: XGBoost in CSE outputs `NaN` for predicted prices.  
    - *Investigation*: Inspect input feature row `X_row`.  
    - *Cause*: Missing values in recently engineered indicator.  
    - *Fix*: Call `.ffill().bfill()` on inference row.
29. **Problem**: Flood submission format rejected by competition evaluator.  
    - *Investigation*: Inspect `sub_ensemble_v1.csv`.  
    - *Cause*: Index column included or incorrect column headers.  
    - *Fix*: `to_csv('...', index=False)`.
30. **Problem**: React frontend displays `NaN%` for 30-day expected return.  
    - *Investigation*: Inspect `PredictionService.get_predictions()` Line 72.  
    - *Cause*: `current_price` was `None` due to empty DB.  
    - *Fix*: Add fallback check: `if not current_price: return 0.0`.

---

# FINAL OUTPUT 3 — TOP 20 "WHY IMPLEMENTED THIS WAY?" QUESTIONS

1. **Why `pd.merge_asof` with `direction='backward'` in CSE?**  
   To align monthly macroeconomic announcements with daily equities strictly without lookahead bias.
2. **Why predict `close.shift(-30)` instead of 1-day ahead in CSE?**  
   To provide actionable medium-term investment horizons rather than high-frequency noise.
3. **Why use a multi-objective selection score in `ForecastTrainer`?**  
   To balance magnitude error (RMSE, MAE), percentage error (MAPE), and trade profitability (Directional Accuracy).
4. **Why apply a baseline penalty of +1000.0 in the tournament?**  
   To automatically disqualify complex ML models that fail to outperform a simple persistence baseline.
5. **Why use `shap.TreeExplainer` instead of permutation importance?**  
   TreeExplainer is exact, fast ($O(TLD)$), and provides local sample-specific attributions in LKR currency.
6. **Why constrain stacking weights with `positive=True, fit_intercept=False`?**  
   To guarantee a convex, non-negative blend that avoids erratic out-of-bounds predictions.
7. **Why use `log1p` target transform in Flood prediction?**  
   To compress right-skewed flood risk variance and prevent models from predicting negative risk scores.
8. **Why include binary missingness indicator features?**  
   Because sensor missingness in flood telemetry is Missing Not At Random (MNAR) and carries physical risk signal.
9. **Why tune CatBoost with Optuna over 50 trials?**  
   Bayesian optimization with TPE explores non-linear hyperparameter spaces far more efficiently than grid search.
10. **Why isolate the UK cohort in Market Basket Analysis?**  
    The UK represented 91.4% of data; regional isolation prevents cultural and geographical purchase distortion.
11. **Why strip non-product tokens like `POSTAGE` and `MANUAL`?**  
    They appear in nearly every cart, creating trivial and uninformative association rules.
12. **Why use FP-Growth over Apriori at low support?**  
    FP-Growth avoids candidate generation by projecting FP-Trees, preventing combinatorial explosion.
13. **Why drop one category when creating dummy variables in linear regression?**  
    To eliminate perfect multicollinearity and avoid the Dummy Variable Trap.
14. **Why use `StandardScaler` in Logistic Regression?**  
    Regularized logistic regression penalizes coefficient magnitudes ($\lambda \sum w_j^2$); unscaled features cause penalties to unfairly target small-scale features.
15. **Why evaluate `RainTomorrow` with ROC-AUC instead of Accuracy?**  
    Severe class imbalance (~78% dry days) renders accuracy misleading.
16. **Why use SQLite for CSE development?**  
    Serverless, zero-configuration local persistence with zero networking overhead.
17. **Why implement a rule-based guardrail in `TechnicalSignalEngine`?**  
    To bound ML model predictions by $\pm 2\%$ when they conflict with overwhelming market momentum.
18. **Why wrap training in `try...except` inside `trainer.py`?**  
    To prevent a mathematical convergence failure in one model (e.g. SARIMAX) from crashing the API.
19. **Why decompose `Date` into `Month` in the weather dataset?**  
    To capture annual seasonality while avoiding high-cardinality one-hot explosion.
20. **Why use `gc.collect()` in `data_preprocessing.py`?**  
    To immediately reclaim RAM allocated to large DataFrames on memory-constrained systems.

---

# FINAL OUTPUT 4 — TOP 20 CODE MODIFICATION TASKS

1. **Task**: Modify `calendar.py` to prevent leakage from `bfill()`.  
   - *Fix*: Replace `merged[val_col].ffill().bfill()` with `merged[val_col].ffill().fillna(0.0)` or drop leading unannounced dates.
2. **Task**: Refactor CSE `dataset.py` to produce a binary classification target.  
   - *Fix*: `df["target_direction"] = (df["close"].shift(-horizon) > df["close"]).astype(int)`.
3. **Task**: Modify `xgboost.py` to output 95% prediction intervals.  
   - *Fix*: Train dual quantile regressors: `XGBRegressor(objective='reg:quantileerror', quantile_alpha=0.05)` and `alpha=0.95`.
4. **Task**: Refactor `PredictionService` cache to use Redis instead of in-memory dictionary.  
   - *Fix*: Serialize `TrainingResult` to JSON/Pickle and store via `redis_client.setex(key, 86400, data)`.
5. **Task**: Add Walk-Forward Cross-Validation to `trainer.py`.  
   - *Fix*: Use `sklearn.model_selection.TimeSeriesSplit(n_splits=5)`.
6. **Task**: Modify `04_ensemble_model.ipynb` to add Ridge regression as an alternative stacker.  
   - *Fix*: `from sklearn.linear_model import Ridge; stacker = Ridge(alpha=1.0, positive=True)`.
7. **Task**: Fix unseen label bug in `04_ensemble_model.ipynb`.  
   - *Fix*: Add `'Missing'` to training encoder classes before transforming test data.
8. **Task**: Vectorize `competition_metric_proxy` for faster evaluation.  
   - *Fix*: Compute MAE, RMSE, and $R^2$ using native NumPy vector operations.
9. **Task**: Modify `analysis.ipynb` to support multi-country filtering.  
   - *Fix*: Parameterize cohort filter: `def clean_cohort(df, country='United Kingdom'): ...`.
10. **Task**: Modify `compare.py` to benchmark across multiple support levels.  
    - *Fix*: Loop `for s in [0.05, 0.03, 0.02, 0.01]:` and record runtimes in a comparison DataFrame.
11. **Task**: Convert `analysis.ipynb` basket creation to output a scipy sparse matrix.  
    - *Fix*: Use `scipy.sparse.csr_matrix` from categorical codes to eliminate RAM overhead.
12. **Task**: Fix Dummy Variable Trap in `3_Categorical_features.ipynb`.  
    - *Fix*: Drop `southwest`: `input = medical_df[['age', 'bmi', 'smoker_code', 'sex_code', 'northeast', 'northwest', 'southeast']]`.
13. **Task**: Add interaction term between `smoker` and `bmi` in Medical Cost regression.  
    - *Fix*: `medical_df['smoker_bmi'] = medical_df['smoker_code'] * medical_df['bmi']`.
14. **Task**: Fix data leakage in `data_preprocessing.py`.  
    - *Fix*: Split raw data before fitting `OneHotEncoder` and `MinMaxScaler`.
15. **Task**: Add `class_weight='balanced'` to `model.py` in weather project.  
    - *Fix*: `model = LogisticRegression(class_weight='balanced', solver='liblinear')`.
16. **Task**: Modify `model.py` to search for optimal classification threshold.  
    - *Fix*: Evaluate F1-score across thresholds `np.arange(0.1, 0.9, 0.05)` and pick maximum.
17. **Task**: Add API endpoint to return list of all tracked stock symbols in CSE.  
    - *Fix*: `@router.get('/stocks') def list_stocks(db: Session = Depends(get_db)): return repo.get_all_symbols()`.
18. **Task**: Add health check endpoint verifying database connectivity.  
    - *Fix*: `@router.get('/health') def health(db = Depends(get_db)): db.execute('SELECT 1'); return {'status': 'healthy'}`.
19. **Task**: Modify CatBoost tuning script to log trials to Weights & Biases.  
    - *Fix*: Add `wandb.log({'trial': trial.number, 'score': score})` inside Optuna callback.
20. **Task**: Add transaction cost deduction to CSE `backtest.py`.  
    - *Fix*: Deduct `trade_value * 0.0112` from cash balance on every trade execution.

---

# FINAL OUTPUT 5 — TOP 20 HARDEST FOLLOW-UP QUESTIONS

1. "Why does `direction='backward'` in `merge_asof` fail to prevent lookahead bias when combined with `bfill()` on leading rows?"
2. "If financial markets follow a random walk ($y_t = y_{t-1} + \epsilon$), why did your XGBoost achieve a lower RMSE than the baseline persistence model on some stocks?"
3. "Since Tree models cannot extrapolate linear trends outside historical training bounds, what will happen to your CSE stock forecast if the market enters an unprecedented bull run?"
4. "Why is minimizing RMSE on `log1p(y)` mathematically different from minimizing RMSE on raw $y$?"
5. "In stacking, why do base model predictions must strictly be generated via Out-Of-Fold splits rather than standard in-sample predictions?"
6. "If CatBoost receives 94.2% of the ensemble weight, does including LightGBM and XGBoost introduce unnecessary operational complexity for a marginal 0.002 score gain?"
7. "How would your Market Basket pipeline behave if an item has 99.9% support (e.g. carrier bags), and how does that affect Confidence and Lift?"
8. "Why does `OneHotEncoder(drop='first')` solve multicollinearity for linear models, but is actively harmful for tree-based models?"
9. "If you deploy your CSE FastAPI application with 8 Gunicorn workers, what race condition occurs in `_auto_ingest_missing()`?"
10. "Why is the ROC-AUC score unaffected by uniform class imbalance, whereas the Precision-Recall AUC changes drastically?"
11. "In your Flood ensemble, how did you verify that target encoding in CatBoost didn't cause subtle validation target leakage?"
12. "What happens if a stock undergoes a 2-for-1 stock split, and how does your preprocessing pipeline detect or correct for it?"
13. "Why does Granger Causality not imply true economic causality, and how could confounding variables induce a false positive?"
14. "In Market Basket Analysis, why is Lift symmetric ($\text{Lift}(A \Rightarrow B) = \text{Lift}(B \Rightarrow A)$) whereas Confidence is asymmetric?"
15. "Why does setting `max_depth=5` in XGBoost act as a regularizer, and what mathematical property does it restrict?"
16. "How does the Kalman filter inside SARIMAX estimate the state space representation of missing exogenous values during inference?"
17. "What is the computational complexity of `shap.TreeExplainer` versus `shap.KernelExplainer`, and why is KernelExplainer unviable in a live API?"
18. "If two features in your medical regression have a Variance Inflation Factor (VIF) $> 10$, what happens to the standard errors of their coefficients?"
19. "Why does random stratified splitting on meteorological time-series data artificially inflate ROC-AUC?"
20. "If you had to put your entire CSE pipeline into production tomorrow, what is the single biggest architectural failure point you would fix first?"

---

# FINAL OUTPUT 6 — 1-DAY REVISION CHECKLIST

### Morning (08:00 – 12:00): CSE Platform Deep-Dive
- [ ] Review `calendar.py`: memorize how `pd.merge_asof(direction='backward')` works and the line 61 `bfill()` leakage.
- [ ] Review `dataset.py`: memorize target definition `close.shift(-30)` and chronological 80/20 split.
- [ ] Review `trainer.py`: memorize the selection score formula ($0.4\text{RMSE} + 0.2\text{MAE} + 0.2\text{MAPE} + 0.2(100 - \text{DirAcc})$) and $+1000$ baseline penalty.
- [ ] Review `xgboost.py`: memorize hyperparameters (`n_estimators=200`, `max_depth=5`, `lr=0.05`) and linear trajectory interpolation.
- [ ] Review `shap_explainer.py`: memorize `TreeExplainer`, output in LKR, and fallback lambda.
- [ ] Review `technical_signal.py`: memorize -5 to +5 score range and $\pm 2\%$ price guardrail.

### Afternoon (12:30 – 16:30): Flood Ensemble & Market Basket Analysis
- [ ] Review Flood `04_ensemble_model.ipynb`:
  - Memorize feature engineering formulas (`flood_susceptibility`, `effective_drainage`).
  - Memorize leak-free imputation: `train_medians` fit on train, passed to test.
  - Memorize the 3 base models (LGBM, XGB, CatBoost) and why CatBoost dominated (94.2%).
  - Memorize the stacker: `LinearRegression(positive=True, fit_intercept=False)`.
  - Memorize target transform: `np.log1p` $\rightarrow$ `np.expm1` $\rightarrow$ `np.clip(0, 1)`.
- [ ] Review Market Basket Analysis:
  - Memorize UK cohort isolation (91.4%).
  - Memorize cancellation dropping (`startswith('C')`) and noise cleaning (`POSTAGE`, `MANUAL`).
  - Memorize Support, Confidence, and Lift formulas.
  - Memorize top rule: Green Teacup $\rightarrow$ Pink Teacup (82% confidence, 15.77 lift).
  - Memorize runtime difference: FP-Growth avoids candidate generation.

### Evening (17:00 – 20:00): Medical Cost & RainTomorrow Classification
- [ ] Review Medical Cost `3_Categorical_features.ipynb`:
  - Memorize the Dummy Variable Trap (including all 4 regions).
  - Memorize why smoker dominates charges.
- [ ] Review Weather `data_preprocessing.py` and `model.py`:
  - Memorize the data leakage bug (scaling/imputation before split).
  - Memorize memory fixes (`gc.collect()`, `del`, chunked export).
  - Memorize why Date was converted to Month.
  - Memorize class imbalance (~78% dry) and why ROC-AUC (0.86) was used over Accuracy.
- [ ] Practice verbally answering the Top 20 "Why did you do this?" questions in under 45 seconds each.

---

*(Proceed to the Mock Acentura Technical Interview in the chat.)*
