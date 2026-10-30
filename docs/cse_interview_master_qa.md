# Engineering Master Q&A & Architecture Defense Guide

This guide compiles senior-level engineering defenses, algorithmic justifications, and technical design rationale for the **Colombo Stock Exchange (CSE) Market Intelligence Platform**.

---

## 1. Quantitative Finance & Modeling Rationale

### Q1: Why predict 30-day forward cumulative log return instead of next-day nominal price?
**Answer**:
Predicting next-day raw prices ($P_{t+1}$) is a well-known financial machine learning anti-pattern. Nominal asset prices are non-stationary $I(1)$ series with strong auto-regressive persistence. An unconstrained model optimizing standard MSE learns the identity mapping $\hat{P}_{t+1} \approx P_t$. This produces misleadingly high $R^2$ values (>0.98), but zero economic alpha: the model merely acts as a one-step lag filter that misses every market turning point.

By transforming prices into forward cumulative log returns:
$$y_t = \ln\left(\frac{P_{t+30}}{P_t}\right)$$
we achieve covariance stationarity, eliminate unit-root persistence, and force the gradient booster to learn genuine mean-reversion, momentum, and cyclical patterns.

---

### Q2: Why use Multi-Quantile Loss ($P_{10}, P_{50}, P_{90}$) instead of standard MSE?
**Answer**:
Financial returns are asymmetric, leptokurtic, and fat-tailed. Standard regression estimates the conditional mean $E[y \mid X]$, which provides zero insight into downside risk or distributional variance.

By training three separate LightGBM models minimizing Pinball Loss:
$$\mathcal{L}_q(y, \hat{y}) = \max\Big(q(y - \hat{y}), (1 - q)(\hat{y} - y)\Big)$$
the platform outputs an institutional-grade forecast cone:
1. **$P_{10}$**: Downside risk boundary (Value-at-Risk floor).
2. **$P_{50}$**: Robust median trajectory (minimizing MAE, resistant to price spikes).
3. **$P_{90}$**: Bullish growth expansion ceiling.

The empirical coverage rate across 5 walk-forward folds is **79.40%**, adhering almost perfectly to the theoretical 80% confidence interval.

---

### Q3: Why is standard $K$-Fold cross-validation invalid for this problem?
**Answer**:
Because our target variable spans a forward 30-trading-day window, standard $K$-Fold CV introduces catastrophic lookahead bias. Any training sample occurring within 30 days of the test window will have forward-looking return labels that overlap with the test set.

We implemented a custom **Purged & Embargoed Walk-Forward Cross-Validation** engine (`PurgedWalkForwardCV`):
1. **Expanding Window**: Folds only train on past data.
2. **Purging (30 days)**: Explicitly drops training samples whose 30-day forward returns overlap with the test set.
3. **Embargo Gap (30 days)**: Enforces a 30-day post-test buffer before training resumes in subsequent folds, eliminating auto-regressive leakage.

---

## 2. System Architecture & Engineering Trade-Offs

### Q4: Why did you choose LightGBM over Deep Learning (LSTM / Transformers)?
**Answer**:
For frontier financial tabular time series, LightGBM consistently outperforms Deep Learning:
1. **Data Efficiency**: Daily time series for 26 equities yield ~1,000–2,000 rows per stock. Deep neural architectures overfit heavily on small tabular sample regimes.
2. **Native Pinball Loss Optimization**: LightGBM supports fast, exact quantile objective functions (`objective="quantile"`, `alpha=q`).
3. **Inference Latency & Portability**: Serialized LightGBM booster models (`lgb_p*.txt`) are under 200 KB each, load in under 5 ms, and run without GPU dependencies in a 512 MB container.

---

### Q5: How does the dual-layer explainability (TreeSHAP + Heuristics) work?
**Answer**:
1. **Layer 1 (Mathematical)**: Uses TreeSHAP to calculate exact additive Shapley values directly over tree ensemble paths. It guarantees local additivity:
   $$\hat{y} = \phi_0 + \sum_{i=1}^M \phi_i$$
   This decomposes predicted returns into exact basis-point contributions from features like `parkinson_vol_20d` or `aspi_return_30d`.
2. **Layer 2 (Domain Heuristics)**: An institutional validation engine translates classical technical indicators (RSI-14, 20/50 SMA trend, MACD histogram, and Parkinson volatility) into **Supporting** vs. **Rejecting / Risk Alert** badges. This gives retail and institutional investors immediate clarity on whether classical technical setups align with the ML model's prediction.

---

### Q6: Why use a hybrid storage layer (Parquet + PostgreSQL)?
**Answer**:
1. **Apache Parquet (`data/processed/`)**: Provides zero-copy columnar reads with sub-millisecond scan times, allowing FastAPI to generate forecast cones instantaneously without database query overhead.
2. **PostgreSQL (Supabase)**: Serves as the system of record with strict ACID guarantees, composite primary key constraints `(symbol, date)` to prevent duplicate bars, and structured tables for audit history (`forecast_predictions` and `pipeline_runs`).
