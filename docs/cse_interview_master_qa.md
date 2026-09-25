# Colombo Stock Exchange (CSE) Market Intelligence Platform
## Complete Technical Interview Master Q&A Guide

> **Note**: A PDF version of this guide has been generated at:  
> [`docs/CSE_Market_Intelligence_Interview_Guide.pdf`](file:///c:/Ongoing%20Projects/New%20folder/docs/CSE_Market_Intelligence_Interview_Guide.pdf)

---

# Table of Contents
1. [Project Understanding & Data Pipeline (14 Questions)](#1-project-understanding--data-pipeline)
2. [Time Series Theory & Econometrics (17 Questions)](#2-time-series-theory--econometrics)
3. [XGBoost Machine Learning Mechanics (12 Questions)](#3-xgboost-machine-learning-mechanics)
4. [Granger Causality & Statistical Inference (7 Questions)](#4-granger-causality--statistical-inference)
5. [Explainable AI (SHAP) Interpretation (8 Questions)](#5-explainable-ai-shap-interpretation)
6. [FastAPI, React & Docker Systems Architecture (12 Questions)](#6-fastapi-react--docker-systems-architecture)

---

# 1. Project Understanding & Data Pipeline

### Q1: Explain your CSE Market Intelligence Platform.
**Answer:**  
The **CSE Market Intelligence Platform** is an end-to-end financial data engineering, machine learning forecasting, and visualization system tailored for the Colombo Stock Exchange (CSE) in Sri Lanka. 

Traditional market analytics rely strictly on historical equity charts. However, in emerging and frontier economies, macroeconomic shocks—such as inflation surges, sovereign debt restructurings, policy interest rate shifts, and currency devaluations—often dominate equity market valuations. 

My platform integrates daily stock market OHLCV data from the CSE with low-frequency macroeconomic datasets from the Central Bank of Sri Lanka (CBSL) and alternative search interest metrics from Google Trends. It applies automated data engineering pipelines with leak-free cross-frequency alignment (`pd.merge_asof`), feeds the data into a tournament of time-series and ML models (Baseline, SARIMAX, and regularized XGBoost), explains the predictions using SHAP (Shapley Additive exPlanations), and presents the insights on an interactive React dashboard backed by a high-performance FastAPI backend.

---

### Q2: What problem were you trying to solve?
**Answer:**  
Two primary problems:
1. **Data Fragmentation & Lack of Macro Integration in Frontier Markets**: In Sri Lanka, retail and institutional investors lacked tools that systematically combine high-frequency equities data with low-frequency macroeconomic indicators without lookahead bias. Standard technical-only models failed to anticipate market drops driven by macroeconomic regime shifts.
2. **The "Black-Box" Problem in Financial ML**: Typical machine learning models output a forecasted price without context or rationale. Traders and portfolio managers do not trust black-box numbers. I solved this by embedding Explainable AI (SHAP and regression parameter attributions) directly into the platform, showing which economic indicators and technical signals drove the forecast.

---

### Q3: Why did you choose the Colombo Stock Exchange dataset?
**Answer:**  
Sri Lanka underwent an unprecedented economic crisis between 2021 and 2024: year-on-year inflation exceeded 69%, the USD/LKR exchange rate doubled from 200 to over 360, and central bank policy interest rates reached 15.5%. 

In developed markets (like the US or UK), macroeconomic factors are relatively stable and micro-level price action dominates. The CSE provided a rare, high-volatility real-world environment to demonstrate the predictive power of macroeconomic features and to evaluate how machine learning handles severe economic regime shifts.

---

### Q4: What data did you use?
**Answer:**  
The platform uses three primary data streams:
1. **CSE Equities Data**: Historical daily OHLCV (Open, High, Low, Close, Volume) data for blue-chip tickers (e.g., Commercial Bank of Ceylon `COMB`, John Keells Holdings `JKH`, Sampath Bank `SAMP`).
2. **Macroeconomic Indicators (CBSL)**: Central Bank of Sri Lanka datasets including:
   - `ExchangeRate_USD_LKR`: Daily/Monthly Sri Lankan Rupee to US Dollar rate.
   - `Inflation_CCPI`: Colombo Consumer Price Index (CCPI) year-on-year inflation rate.
   - `InterestRate_SDFR`: Standing Deposit Facility Rate.
   - `InterestRate_SLFR`: Standing Lending Facility Rate.
3. **Alternative Sentiment Data**: Google Trends weekly search interest scores for corporate tickers and financial keywords in Sri Lanka.

---

### Q5: What were your input features?
**Answer:**  
Over 40 engineered features across five distinct categories:
1. **Price Action & Return Features**: Daily percentage return, Log return, High-Low range percentage `(High - Low) / Low`, and Open-Close difference `(Close - Open) / Open`.
2. **Trend & Moving Averages**: Simple Moving Averages (`SMA_10`, `SMA_20`, `SMA_50`), Exponential Moving Averages (`EMA_10`, `EMA_20`, `EMA_50`), and Average Directional Index (`ADX_14`) for trend strength.
3. **Momentum & Oscillators**: Relative Strength Index (`RSI_14`), Moving Average Convergence Divergence (`MACD` & `MACD Signal`), Rate of Change (`ROC_12`), Stochastic Oscillator (`%K`, `%D`), and Williams `%R`.
4. **Volatility & Volume**: Bollinger Bands (`Upper`, `Middle`, `Lower`), Average True Range (`ATR_14`), On-Balance Volume (`OBV`), Volume Moving Average (`Volume_MA_20`), and 20-day rolling return volatility.
5. **Autoregressive Lags & Rolling Aggregations**: Direct price lags (`Close_lag_1`, `3`, `5`, `10`, `20`), Return lags (`Return_lag_1`, `5`), and rolling windows (7-day, 14-day, 30-day rolling means and volatilities).
6. **Macroeconomic & Sentiment**: `ExchangeRate_USD_LKR`, `Inflation_CCPI`, `InterestRate_SDFR`, `InterestRate_SLFR`, and `trend_score`.
7. **Calendar Signals**: `day_of_week` (0-4) and `month` (1-12) to capture calendar seasonality.

---

### Q6: What was your target variable?
**Answer:**  
The primary target variable was the future Close price shifted across a defined forward horizon:  
$$y[t] = \text{Close}[t + H]$$
where $H = 30$ trading days for monthly outlooks, and $H = 1$ or $7$ days for short-term forecasts. I also derived target percentage return:
$$\text{target\_7d\_return} = \frac{\text{Close}[t+H] - \text{Close}[t]}{\text{Close}[t]}$$
to evaluate expected percentage capital gains or losses.

---

### Q7: How did you collect the data?
**Answer:**  
Through modular, decoupled ingestion clients in `backend/app/data_sources/`:
- **Equities Data**: Ingested via direct CSE REST APIs and Yahoo Finance historical tickers (`.LK` suffix) via `yfinance_client.py` and `CSEClient`.
- **Macroeconomic Data**: Parsed from official Central Bank of Sri Lanka statistical releases and standardized CSV tables.
- **Google Trends Data**: Extracted using the `pytrends` library querying Sri Lanka's country code (`LK`).
All ingestion pipelines are orchestrated by `IngestionService` and audited with runtime statistics in the `job_logs` database table.

---

### Q8: How did you clean the financial data?
**Answer:**  
In `DataCleaner` (`backend/app/preprocessing/cleaner.py`):
1. **Deduplication**: Filtered duplicate entries on `(symbol, date)` pairs.
2. **Date Normalization**: Converted all date strings into standardized ISO-8601 `YYYY-MM-DD` timestamps.
3. **Chronological Sorting**: Sorted the time series strictly in ascending chronological order (`df.sort_values("date")`).
4. **Window Warmup Trimming**: Dropped initial warmup rows produced by rolling statistics (e.g. 50-day SMA) after computation so no NaNs entered the estimators.

---

### Q9: How did you handle missing values?
**Answer:**  
I strictly avoided backward imputation or mean substitution, which causes catastrophic lookahead bias in time series. Missing macroeconomic values were handled via **forward-fill (`ffill`)**, implemented using Pandas `merge_asof` with backward direction. This guarantees that on trading day $t$, the model only sees the *most recently published* CBSL figure. 

For XGBoost, its native histogram tree algorithm automatically handles any remaining sparsity by learning the optimal branch direction for missing values.

---

### Q10: How did you handle outliers?
**Answer:**  
In financial markets during a sovereign crisis, extreme price jumps and currency devaluations are **genuine macroeconomic regime shifts**, not faulty sensor readings. Deleting them would blind the model to the exact crises it was built to analyze. I handled them by:
1. Transforming raw prices into percentage returns and logarithmic returns, which stabilize variance.
2. Using decision-tree-based algorithms (XGBoost), which split on rank order rather than absolute Euclidean distance, making them naturally robust to extreme values compared to Ordinary Least Squares (OLS) regression.

---

### Q11: What features did you engineer?
**Answer:**  
Key engineered features include:
1. **Cross-Frequency Macro Merger**: Merged monthly inflation and interest rates onto daily stock timelines using Pandas `merge_asof`.
2. **Multi-Horizon Lags**: Price lags at $t-1, t-2, t-3, t-5, t-10, t-20$ and return lags at $t-1, t-5$ to capture momentum persistence.
3. **Rolling Volatility Windows**: 7-day, 14-day, 20-day, and 30-day rolling standard deviations to capture volatility clustering.
4. **Intraday Volatility Ratios**: `(High - Low) / Low` and `(Close - Open) / Open`.
5. **Calendar Cyclical Signals**: `day_of_week` (0-4) and `month` (1-12) to capture end-of-week profit taking and end-of-quarter window dressing.

---

### Q12: What technical indicators did you use?
**Answer:**  
Implemented via the `ta` library in `IndicatorBuilder`:
- **Trend**: Simple Moving Averages (`SMA_10`, `SMA_20`, `SMA_50`), Exponential Moving Averages (`EMA_10`, `EMA_20`, `EMA_50`), and Average Directional Index (`ADX_14`).
- **Momentum**: Relative Strength Index (`RSI_14`), Moving Average Convergence Divergence (`MACD` & `MACD Signal`), Rate of Change (`ROC_12`), Stochastic Oscillator (`%K`, `%D`), and Williams `%R`.
- **Volatility**: Bollinger Bands (upper, middle, lower), Average True Range (`ATR_14`), and 20-day return volatility.
- **Volume**: On-Balance Volume (`OBV`) and Volume 20-day Moving Average.

---

### Q13: Why are technical indicators useful?
**Answer:**  
Raw closing prices lack context. Technical indicators transform raw price and volume into mathematical representations of market dynamics:
- **RSI**: Quantifies overbought ($>70$) and oversold ($<30$) extremes.
- **MACD**: Measures changes in the strength, direction, momentum, and duration of a trend.
- **Bollinger Bands**: Provide dynamic volatility envelopes that expand during high volatility and contract during consolidation.
- **ATR**: Measures volatility in absolute terms without directional bias, useful for position sizing.
- **OBV**: Correlates volume flow with price movement to identify institutional accumulation or distribution.

---

### Q14: How did you avoid data leakage?
**Answer:**  
Through three strict architectural controls:
1. **Strict Chronological Train/Test Split**: 80% train / 20% test without random shuffling. The test set always exists in the chronological future.
2. **Point-in-Time Alignment**: Used `pd.merge_asof` with backward matching so daily stock prices only join with macroeconomic indicators published on or before that exact trading day.
3. **No Centered Rolling Windows**: All rolling metrics (SMA, rolling volatility) use trailing historical windows exclusively (`rolling(window)` without `center=True`), ensuring no future data points ever enter feature computations.

---

# 2. Time Series Theory & Econometrics

### Q15: What is time-series forecasting?
**Answer:**  
Time-series forecasting is the mathematical and computational task of predicting future values of a variable based on its historically observed chronological sequence:
$$y_{t+h} = f(y_t, y_{t-1}, \dots, y_{t-k}, \mathbf{X}_t)$$
Unlike cross-sectional machine learning (where samples are assumed independent and identically distributed), time-series forecasting explicitly models temporal dependencies, trends, seasonality, and autocorrelation.

---

### Q16: How is time-series data different from normal tabular data?
**Answer:**  
- **Row Dependency**: Tabular data assumes sample independence (permuting row order does not change the model). Time-series data has strict chronological order where observation $y_t$ is correlated with $y_{t-1}$.
- **Non-Stationarity**: In tabular data, data distributions are assumed stable. In time series, the underlying data-generating distribution frequently shifts over time (concept drift).
- **Validation Constraints**: Shuffling is prohibited in time series because future data must never be used to train past models.

---

### Q17: Why can't you randomly split time-series data?
**Answer:**  
Random k-fold cross-validation or random `train_test_split` scrambles the time dimension. If day $t$ is placed in the test set while day $t-1$ and day $t+1$ are in the training set, the model easily memorizes the surrounding trajectory. This introduces severe **lookahead bias**, resulting in unrealistically high test accuracy that fails completely when deployed to predict the real, unseen future.

---

### Q18: What is SARIMAX?
**Answer:**  
SARIMAX stands for **Seasonal AutoRegressive Integrated Moving Average with eXogenous variables**. It is expressed as $\text{SARIMAX}(p, d, q)(P, D, Q)_s + \mathbf{X}$:
- **$p$ (Autoregression)**: Linear combination of $p$ past lagged values.
- **$d$ (Integration)**: Degree of differencing needed to achieve stationarity.
- **$q$ (Moving Average)**: Linear combination of $q$ past forecast error terms.
- **$(P, D, Q)_s$ (Seasonal components)**: Seasonal AR, differencing, and MA terms over seasonal period $s$.
- **$\mathbf{X}$ (Exogenous Regressors)**: External explanatory covariates (e.g. RSI, inflation, USD/LKR exchange rate).

---

### Q19: What does ARIMA stand for?
**Answer:**  
ARIMA stands for:
- **AR (AutoRegressive)**: The model uses the dependent relationship between an observation and a number of lagged observations.
- **I (Integrated)**: The use of differencing raw observations to make the time series stationary.
- **MA (Moving Average)**: The model incorporates the dependency between an observation and a residual error from a moving average model applied to lagged observations.

---

### Q20: What is seasonality?
**Answer:**  
Seasonality refers to periodic, repetitive, and predictable fluctuations that recur at regular intervals (such as days of the week, months of the year, or quarterly earnings cycles). In our platform, we modeled calendar seasonality using `day_of_week` and `month` indicators.

---

### Q21: What is stationarity?
**Answer:**  
A time series is weakly (covariance) stationary if its statistical properties do not depend on the time at which the series is observed:
1. **Constant Mean**: $\mathbb{E}[y_t] = \mu$ for all $t$.
2. **Constant Variance**: $\text{Var}(y_t) = \sigma^2 < \infty$ for all $t$.
3. **Time-Invariant Autocovariance**: $\text{Cov}(y_t, y_{t-k}) = \gamma_k$, depending only on lag $k$ and not on time $t$.

---

### Q22: Why is stationarity important?
**Answer:**  
Classical statistical time-series models (like ARMA/SARIMAX) assume stationarity so that estimated parameters remain stable over time. If a series has an explosive trend or non-constant variance, standard linear regressions suffer from **spurious correlation**: $t$-statistics and $R^2$ values become misleadingly inflated, and forecasts quickly diverge into nonsense.

---

### Q23: What is differencing?
**Answer:**  
Differencing is the transformation of subtracting the prior observation from the current observation:
$$\Delta y_t = y_t - y_{t-1}$$
First-order differencing removes linear trends; second-order differencing removes quadratic trends. In finance, calculating percentage returns or logarithmic differences $r_t = \ln(P_t / P_{t-1})$ is a standard differencing technique used to convert non-stationary raw stock prices into stationary return series.

---

### Q24: What is autocorrelation?
**Answer:**  
Autocorrelation (serial correlation) is the Pearson correlation between values of the same time series at different points in time:
$$\rho_k = \frac{\text{Cov}(y_t, y_{t-k})}{\text{Var}(y_t)}$$
It measures the degree to which past values persist into future values. While daily stock returns exhibit near-zero autocorrelation (consistent with the Efficient Market Hypothesis), absolute returns and squared returns show strong autocorrelation, indicating **volatility clustering**.

---

### Q25: What is partial autocorrelation?
**Answer:**  
The Partial Autocorrelation Function (PACF) measures the direct correlation between $y_t$ and $y_{t-k}$ after mathematically filtering out the mutual linear influence of all intermediate lags ($y_{t-1}, y_{t-2}, \dots, y_{t-k+1}$). In ARIMA identification, PACF plots help determine the autoregressive lag order $p$.

---

### Q26: What is an exogenous variable?
**Answer:**  
An exogenous variable (the $\mathbf{X}$ in SARIMAX) is an external explanatory input determined outside the target equation whose values provide incremental predictive power for the target series. For example, using the USD/LKR exchange rate or inflation to predict stock prices. In contrast, endogenous variables are explained by the model itself.

---

### Q27: Why did you use SARIMAX?
**Answer:**  
SARIMAX served as a rigorous, interpretable econometric benchmark. Unlike non-parametric machine learning models, SARIMAX provides formal statistical hypothesis tests, parameter coefficients, $p$-values for exogenous features, and mathematical confidence intervals ($\hat{y} \pm 1.96 \times \text{SE}$), allowing us to evaluate classical statistical modeling against gradient boosted decision trees.

---

### Q28: What is multi-step forecasting?
**Answer:**  
Multi-step forecasting is the prediction of values multiple steps into the future (e.g. forecasting prices for $t+1, t+2, \dots, t+30$) rather than predicting only the immediate next time step $t+1$.

---

### Q29: How did you perform multi-step forecasting?
**Answer:**  
In our platform, we used a direct multi-horizon target approach:
- Supervised models were trained directly on target $y[t] = \text{Close}[t+30]$.
- For trajectory visualization, the system projects a linear path from the latest actual close to the predicted terminal price, modulated by our `TechnicalSignalEngine` score and confidence intervals.
- In SARIMAX, dynamic state-space projection was utilized for out-of-sample steps.

---

### Q30: What problems occur with multi-step forecasting?
**Answer:**  
1. **Error Compounding**: In recursive autoregressive models, errors from step $t+1$ feed into the inputs for step $t+2$, causing forecasts to rapidly degrade as the horizon extends.
2. **Missing Future Exogenous Values**: Predicting 30 days ahead requires knowing what exogenous variables (like interest rates or RSI) will be 30 days ahead. In our architecture, we mitigate this by using direct multi-horizon targets and forward-filled latest economic releases.

---

### Q31: How did you evaluate your forecasting models?
**Answer:**  
In `ModelEvaluator` (`backend/app/forecasting/evaluator.py`), we evaluated all models on an identical 20% chronological holdout test set using:
- **RMSE (Root Mean Squared Error)**: Penalizes large error outliers.
- **MAE (Mean Absolute Error)**: Average absolute rupee error.
- **MAPE (Mean Absolute Percentage Error)**: Scale-independent error percentage.
- **Directional Accuracy (%)**: Percentage of days where predicted direction (Up vs. Down) matched actual market direction.
- **$R^2$**: Coefficient of determination.

We selected the winning model using a composite selection score:
$$\text{Score} = 0.4 \times \text{RMSE} + 0.2 \times \text{MAE} + 0.2 \times \text{MAPE} + 0.2 \times (100 - \text{Directional Accuracy})$$

---

### Q32: Why did you include a Naive Baseline?
**Answer:**  
In financial time series, complex models often overfit to noise and fail to outperform simple persistence rules (such as predicting tomorrow's price equals today's price). A Naive Baseline is an indispensable scientific benchmark. In our `ForecastTrainer`, if an ML model's RMSE is more than 10% worse than the baseline, it receives a severe penalty (+1000 points), ensuring we never deploy an over-parameterized model that underperforms a simple moving average.

---

### Q33: What is a naive forecasting model?
**Answer:**  
A naive forecasting model sets the future prediction equal to the most recent observation:
$$\hat{y}_{t+h} = y_t$$
(assuming a pure Random Walk), or sets it equal to a simple historical rolling mean. It represents a zero-complexity persistence benchmark.

---

### Q34: When can a simple baseline outperform ML?
**Answer:**  
1. When the signal-to-noise ratio is extremely low (common in high-frequency trading).
2. When the market is strictly efficient and prices follow an unpredictable random walk.
3. During unprecedented black-swan regime shifts where historical relationships break down.
4. When the machine learning model is overfitted to historical training noise.

---

# 3. XGBoost Machine Learning Mechanics

### Q35: Why did you use XGBoost?
**Answer:**  
XGBoost (Extreme Gradient Boosting) is the leading model for heterogeneous tabular datasets:
1. **Non-linear Feature Interactions**: Captures complex non-linear thresholds between macroeconomic indicators and stock momentum.
2. **Robustness to Outliers & Scale**: Invariant to feature scaling and unaffected by extreme financial spikes.
3. **Missing Value Handling**: Natively routes missing values to default tree split directions.
4. **Fast Training**: Fits in milliseconds, enabling on-demand retraining.
5. **Native SHAP Compatibility**: Fully supports exact TreeSHAP algorithms for Explainable AI.

---

### Q36: How does XGBoost work?
**Answer:**  
XGBoost is an ensemble of decision trees built sequentially. Each new tree fits the negative gradient (pseudo-residuals) of the loss function calculated from all prior trees. It minimizes a regularized objective function:
$$\mathcal{L} = \sum_{i=1}^n l(y_i, \hat{y}_i) + \sum_{k=1}^K \Omega(f_k)$$
where the regularization term $\Omega(f) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2$ penalizes tree complexity and leaf weights to prevent overfitting.

---

### Q37: XGBoost vs Random Forest?
**Answer:**  
- **Ensemble Method**: Random Forest uses **Bagging** (builds deep, independent trees in parallel on bootstrap samples and averages them). XGBoost uses **Boosting** (builds shallow trees sequentially, each correcting the residual errors of the prior ensemble).
- **Variance vs. Bias**: Random Forest primarily reduces variance; XGBoost primarily reduces bias while controlling variance via explicit L1/L2 tree regularization.
- **Performance**: XGBoost generally achieves higher predictive accuracy on structured tabular datasets.

---

### Q38: What is boosting?
**Answer:**  
Boosting is an ensemble learning method where weak learners (typically shallow trees) are added iteratively to a model. Each new learner is trained to predict the errors or pseudo-residuals produced by the existing ensemble, combining many weak models into one highly accurate predictor.

---

### Q39: What is bagging?
**Answer:**  
Bagging (Bootstrap Aggregating) creates multiple independent subsets of the original training data by sampling with replacement. An independent model is trained on each subset, and their individual predictions are aggregated (via averaging for regression or majority voting for classification) to reduce variance without increasing bias.

---

### Q40: What is a decision tree?
**Answer:**  
A decision tree is a non-parametric supervised model that recursively partitions the feature space into orthogonal rectangular regions using binary decision rules (e.g. `Inflation_CCPI > 15.2`). At each node, it selects the feature and threshold that maximizes variance reduction (in regression) or information gain (in classification).

---

### Q41: What is overfitting in XGBoost?
**Answer:**  
Overfitting in XGBoost occurs when trees grow too deep or too numerous, memorizing idiosyncratic market noise and temporary historical anomalies. The model achieves near-zero error on training data but its error spikes on out-of-time test data.

---

### Q42: How did you tune XGBoost?
**Answer:**  
In `backend/app/forecasting/models/xgboost.py`, we configured conservative, regularized hyperparameters tailored for small-to-medium financial time series:
```python
PARAMS = {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "tree_method": "hist"
}
```
Performance was validated on the out-of-time 20% holdout test set.

---

### Q43: Which hyperparameters did you tune?
**Answer:**  
- `n_estimators`: Total number of boosting iterations (trees).
- `max_depth`: Maximum depth allowed for each decision tree.
- `learning_rate` ($\eta$): Step-size shrinkage applied to each tree's leaf weights.
- `subsample`: Fraction of rows randomly sampled per boosting round.
- `colsample_bytree`: Fraction of features (columns) sampled when building each tree.
- `tree_method`: Histogram-based binning (`hist`) for fast, memory-efficient splits.

---

### Q44: What is learning rate?
**Answer:**  
The learning rate ($\eta$, e.g. 0.05) is a shrinkage factor that scales the contribution of each newly added tree:
$$\hat{y}_i^{(m)} = \hat{y}_i^{(m-1)} + \eta \cdot f_m(x_i)$$
Lower learning rates slow down learning and require more trees, but prevent individual trees from dominating the model, leading to superior generalization on unseen data.

---

### Q45: What is number of estimators?
**Answer:**  
Number of estimators (`n_estimators = 200`) is the total number of sequential decision trees built during training. Too few trees leads to underfitting; too many trees can lead to overfitting unless countered by early stopping, shrinkage, and subsampling.

---

### Q46: What is max depth?
**Answer:**  
Max depth (`max_depth = 5`) specifies the maximum number of levels in each tree. Setting `max_depth=5` allows up to $2^5 = 32$ leaf nodes, enabling the model to capture up to 5-way non-linear feature interactions (e.g. Inflation + USD/LKR + RSI + SMA + Volume) while strictly preventing runaway tree memorization.

---

# 4. Granger Causality & Statistical Inference

### Q47: What is Granger causality?
**Answer:**  
Granger causality is an econometric hypothesis test proposed by Nobel laureate Clive Granger. It tests whether past lagged values of time series $X$ contain statistically significant information that helps forecast time series $Y$, beyond the information already contained in past lagged values of $Y$ itself.

---

### Q48: How does Granger causality work?
**Answer:**  
It compares two Vector AutoRegressive (VAR) regression equations:
1. **Restricted Model**:
   $$Y_t = \alpha + \sum_{i=1}^p \beta_i Y_{t-i} + \varepsilon_t$$
2. **Unrestricted Model**:
   $$Y_t = \alpha + \sum_{i=1}^p \beta_i Y_{t-i} + \sum_{j=1}^p \gamma_j X_{t-j} + u_t$$
Using an F-test or Chi-square test (`ssr_chi2test`), it evaluates the null hypothesis $H_0: \gamma_1 = \gamma_2 = \dots = \gamma_p = 0$. If the resulting $p$-value is $< 0.05$, we reject the null hypothesis and conclude that $X$ Granger-causes $Y$.

---

### Q49: What does it mean if X Granger-causes Y?
**Answer:**  
It means that past historical values of $X$ provide statistically significant predictive power for future values of $Y$. It demonstrates **temporal precedence and incremental forecasting value**, not physical or philosophical causation.

---

### Q50: Does Granger causality prove actual causation?
**Answer:**  
**No!** Granger causality only tests for temporal precedence in linear forecasting. A classic counterexample: a rooster crowing Granger-causes the sunrise because the crowing precedes the sunrise, even though the rooster does not cause the sun to rise. Actual causation requires controlled experiments or structural causal modeling.

---

### Q51: Why did you use Granger causality in your project?
**Answer:**  
In `backend/app/analytics/causality.py`, we implemented `GrangerCausalityTester` to empirically verify whether macroeconomic variables (USD/LKR exchange rate, CBSL inflation) and Google Trends search interest statistically lead Colombo Stock Exchange returns. This provided statistical validation for our feature selection instead of assuming macro indicators were predictive.

---

### Q52: What is a lead-lag relationship?
**Answer:**  
A lead-lag relationship occurs when changes in one series (the leading indicator, e.g. Central Bank rate decisions or currency devaluations) consistently precede and predict corresponding changes in another series (the lagging indicator, e.g. banking stock prices) across an observed time horizon (e.g. lag = 2 to 5 trading days).

---

### Q53: How is correlation different from Granger causality?
**Answer:**  
- **Correlation**: Measures static, contemporaneous linear co-movement at the exact same point in time: $\text{Corr}(X_t, Y_t)$. It is completely symmetric: $\text{Corr}(X, Y) = \text{Corr}(Y, X)$ and ignores time direction.
- **Granger Causality**: Tests directional, time-lagged predictive precedence: does $X_{t-k}$ predict $Y_t$? It is strictly asymmetric: $X$ can Granger-cause $Y$ while $Y$ does not Granger-cause $X$.

---

# 5. Explainable AI (SHAP) Interpretation

### Q54: What is SHAP?
**Answer:**  
SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explain the individual predictions of any machine learning model. Grounded in Lloyd Shapley's cooperative game theory (Nobel Prize in Economics), it computes the fair, mathematically optimal marginal contribution of each feature to the final prediction.

---

### Q55: Why did you use SHAP?
**Answer:**  
Financial traders and portfolio managers refuse to trust black-box models. In `backend/app/explainability/`, SHAP breaks the black box by providing mathematical feature attributions, showing investors exactly *which* macroeconomic indicator or technical signal drove a forecasted price movement up or down.

---

### Q56: How does SHAP explain a prediction?
**Answer:**  
SHAP formulates an additive feature attribution model:
$$f(x) = \phi_0 + \sum_{i=1}^M \phi_i$$
where:
- $\phi_0$ is the base value (the average prediction across the training dataset).
- $\phi_i$ is the Shapley value for feature $i$ in that specific prediction.
For example, if the baseline price is 100 LKR and the model predicts 112 LKR, SHAP proves that `USD_LKR` added +9 LKR, `RSI` added +5 LKR, and `Inflation` subtracted -2 LKR.

---

### Q57: What is a SHAP value?
**Answer:**  
A SHAP value $\phi_i$ represents the weighted average marginal contribution of feature $i$ across all possible feature subsets $S \subseteq F \setminus \{i\}$:
$$\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$
It is the only attribution method that simultaneously satisfies 4 fundamental axiomatic properties: **Efficiency, Symmetry, Dummy (Null Player), and Additivity**.

---

### Q58: What is the difference between global and local explanations?
**Answer:**  
- **Local Explanation**: Explains a single, individual prediction for a specific stock on a specific date (e.g. "Why did the model predict a 4% drop for Commercial Bank today?").
- **Global Explanation**: Aggregates local explanations across the entire dataset to reveal general model behavior (e.g. "Across all stocks over 3 years, which features were most influential overall?").

---

### Q59: How would you interpret a SHAP summary plot?
**Answer:**  
In a SHAP beeswarm summary plot:
1. **Y-axis**: Features are ranked from top to bottom by total absolute importance.
2. **X-axis**: Shows the SHAP value (positive values push the forecast higher, negative values push it lower).
3. **Points**: Each dot represents an individual observation.
4. **Color**: Feature value (Red = High, Blue = Low).  
*Example*: If high values (red) for `InterestRate_SLFR` cluster on the negative side of the x-axis, it proves that high interest rates drive down stock price forecasts.

---

### Q60: Why is explainability important in financial ML?
**Answer:**  
1. **Risk Management**: Detects whether the model is learning genuine economic relationships or spurious historical artifacts.
2. **Regulatory Compliance**: Central banks and financial authorities require justifiable audit trails for automated decision-making.
3. **User Adoption**: Institutional investors will only execute trading strategies when the underlying logic aligns with sound macroeconomic theory.

---

### Q61: Can SHAP prove that a feature causes the prediction?
**Answer:**  
**No.** SHAP explains the *internal mechanics of the trained model*, not real-world causation. It reveals which features the model relied upon to produce its output. If the model was trained on data containing spurious correlations, SHAP will faithfully explain that spurious reliance.

---

# 6. FastAPI, React & Docker Systems Architecture

### Q62: Why did you use FastAPI?
**Answer:**  
FastAPI is high-performance, asynchronous, and modern:
1. **Blazing Performance**: Built on Starlette and Pydantic, matching NodeJS and Go speeds.
2. **Type Safety & Automatic Validation**: Automatically validates request parameters via Python type hints, returning clear 422 error responses on bad input.
3. **Asynchronous Concurrency**: Natively supports `async/await` for handling concurrent external API requests and database queries.
4. **Automatic Interactive Documentation**: Generates interactive Swagger UI documentation at `/docs` and ReDoc at `/redoc`.

---

### Q63: What is FastAPI?
**Answer:**  
FastAPI is an asynchronous, high-performance web framework for developing RESTful APIs with Python 3.8+ based on standard Python type hints and ASGI (Asynchronous Server Gateway Interface) standards.

---

### Q64: Why FastAPI instead of Flask?
**Answer:**  
- **Asynchronous vs Synchronous**: Flask is traditionally synchronous WSGI; FastAPI is asynchronous ASGI, enabling high concurrency for I/O-bound data pipelines.
- **Data Validation**: Flask requires manual validation or third-party libraries (like Marshmallow); FastAPI validates requests automatically via Pydantic.
- **Documentation**: Flask requires manual Swagger configuration; FastAPI generates interactive OpenAPI documentation automatically.
- **Execution Speed**: FastAPI is significantly faster due to Starlette core optimizations.

---

### Q65: How does your React frontend communicate with FastAPI?
**Answer:**  
Through asynchronous HTTP REST calls encapsulated in `frontend/src/services/api.js`. The React client uses Fetch or Axios to send HTTP requests to the FastAPI endpoints (e.g. `http://localhost:8000/api/v1/forecasting/{symbol}`). FastAPI validates the request, executes prediction logic, and returns structured JSON responses. Cross-Origin Resource Sharing (CORS) middleware is configured in FastAPI to allow frontend browser access.

---

### Q66: What is an API?
**Answer:**  
An Application Programming Interface (API) is a formalized software intermediary that enables two separate applications to communicate, exchange data, and trigger actions over defined endpoints, protocols, and data schemas without exposing internal code implementation.

---

### Q67: What is REST?
**Answer:**  
REST (Representational State Transfer) is an architectural style for networked hypermedia applications. It adheres to 6 core principles:
1. Client-Server separation
2. Statelessness (no client context stored on server between requests)
3. Cacheability
4. Uniform Interface (standard HTTP verbs: `GET`, `POST`, `PUT`, `DELETE`)
5. Layered System
6. Code on Demand (optional)

---

### Q68: What is JSON?
**Answer:**  
JSON (JavaScript Object Notation) is a lightweight, human-readable, language-independent text format for structured data exchange based on key-value pairs and arrays. It is the universal standard for modern RESTful web APIs.

---

### Q69: Explain the request-response cycle in your application.
**Answer:**  
1. **User Action**: The user selects ticker `COMB` and a 30-day forecast horizon on the React UI.
2. **HTTP Request**: The React client dispatches an HTTP request: `GET /api/v1/forecasting/COMB?horizon=30`.
3. **Routing & Validation**: FastAPI receives the request at `app/api/v1/forecasting.py` and validates query parameters via Pydantic.
4. **Service Orchestration**: `PredictionService` checks cache or queries `cse.db` via SQLAlchemy for historical prices and CBSL indicators.
5. **Model Inference**: `ForecastTrainer` runs the trained XGBoost model and calculates evaluation metrics.
6. **Explainability**: `ExplanationService` computes SHAP attribution values.
7. **JSON Response**: FastAPI serializes the prediction results and SHAP attributions into a typed JSON response.
8. **Client Rendering**: React receives the payload, updates component state, and Chart.js / Recharts dynamically renders the forecast envelope and feature attribution bar charts.

---

### Q70: Why did you use Docker?
**Answer:**  
Docker containerizes the application into lightweight, self-contained images bundling the application code, Python/Node runtime, system libraries, and dependencies. It guarantees environment consistency: the app runs identically in local development, teammate machines, and production cloud containers.

---

### Q71: What problem does Docker solve?
**Answer:**  
Docker completely eliminates the "it works on my machine" problem. In financial machine learning, compiling C-extensions for libraries like `xgboost` and `statsmodels` often fails across different operating systems. Docker packages all OS-level build tools and packages into a uniform, reproducible runtime container.

---

### Q72: How would you deploy this application?
**Answer:**  
Following our `docs/deployment.md` production blueprint:
- **Backend**: Containerized via `backend/Dockerfile` and deployed to **Google Cloud Run** or **Render** as a stateless, autoscaling REST service.
- **Frontend**: Compiled into static assets via `npm run build` and deployed to **Cloudflare Pages** or **Vercel** with global CDN distribution.
- **Database**: SQLite file storage for lightweight research, or seamless migration to managed **Google Cloud SQL (PostgreSQL)** via SQLAlchemy connection strings.
- **Automated CI/CD**: Daily ingestion and model retraining scheduled via **GitHub Actions** (`.github/workflows/daily_ingest.yml`) running at market close (18:30 IST / 13:00 UTC) on weekdays.

---
*End of Master Q&A Guide.*
