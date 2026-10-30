# Quantitative Modeling Strategy & Validation Rigor

## 1. The Target Formulation Problem

### The Nominal Price Anti-Pattern
In naive financial machine learning implementations, practitioners frequently formulate forecasting as predicting the future raw price:
$$\hat{P}_{t+h} = f(P_t, P_{t-1}, \dots)$$
Because raw asset prices are non-stationary $I(1)$ processes (unit root stochastic trends), standard loss functions like Mean Squared Error (MSE) heavily penalize any deviation from the latest known price. Consequently, unconstrained gradient boosters or neural networks learn a trivial identity persistence model:
$$\hat{P}_{t+h} \approx P_t$$
While such models achieve deceptive evaluation metrics ($R^2 > 0.98$, directional accuracy ~50%), they possess **zero forecasting alpha** and lag actual turning points by exactly $h$ periods.

### Stationarity via Forward Cumulative Log Returns
To enforce covariance stationarity and force the estimator to learn true cyclical and momentum dynamics, our platform defines the target variable as the **30-trading-day ahead cumulative log return**:

$$y_t = \ln\left(\frac{P_{t+30}}{P_t}\right)$$

Properties of this target formulation:
1. **Time-Additive**: Multi-period log returns can be aggregated linearly across intermediate time horizons.
2. **Scale Invariant**: Normalized across equities trading at LKR 10 vs. LKR 1,500.
3. **Stationary**: Statistical properties (mean, variance, auto-covariance) do not drift systematically with nominal index inflation.

---

## 2. Multi-Quantile Loss Optimization

Rather than estimating the conditional expectation $E[y \mid X]$ (which discards distributional uncertainty), the platform optimizes asymmetric **Pinball Loss** (Quantile Regression) across three critical investment quantiles:

$$\mathcal{L}_q(y, \hat{y}) = \max\Big(q(y - \hat{y}), (1 - q)(\hat{y} - y)\Big)$$

Where $q \in \{0.10, 0.50, 0.90\}$:
- **$P_{10}$ (Downside Risk / Value-at-Risk Floor)**: $q = 0.10$. Penalizes underestimating extreme drawdowns 9 times more heavily than overestimating returns. Represents the 90% confidence downside risk boundary.
- **$P_{50}$ (Median Trajectory Expectation)**: $q = 0.50$. Equivalent to Mean Absolute Error (MAE). Yields the robust median return trajectory less susceptible to outlier spikes than MSE.
- **$P_{90}$ (Bullish Ceiling / Upper Resistance)**: $q = 0.90$. Represents the 90th percentile bullish expansion envelope.

### Trajectory Mapping
From the predicted forward log return quantiles $\hat{r}_{10}, \hat{r}_{50}, \hat{r}_{90}$, the terminal maps price coordinates across the 30-day horizon:

$$P_{t+h, q} = P_t \times \exp\left(\hat{r}_q \times \frac{h}{30}\right), \quad \forall h \in [1, 30]$$

Monotonicity is strictly enforced in post-processing: $\hat{r}_{10} \le \hat{r}_{50} \le \hat{r}_{90}$.

---

## 3. Purged & Embargoed Walk-Forward Cross-Validation

Standard $K$-Fold cross-validation destroys temporal sequence and causes severe lookahead leakage. Furthermore, because our target spans 30 forward trading days, any training bar within 30 days of the test window contains labels that overlap with the test set.

Our custom `PurgedWalkForwardCV` (`src/modeling/train_lightgbm.py`) enforces strict leakage elimination across 5 expanding splits:

```text
Historical Timeline ────────────────────────────────────────────────────────►
Fold 1: [██████ Train Window ██████] [Purge: 30d] [Test: 60d] [Embargo: 30d]
Fold 2: [██████████ Train Window ██████████] [Purge: 30d] [Test: 60d] [Embargo: 30d]
Fold 3: [██████████████ Train Window ██████████████] [Purge: 30d] [Test: 60d] ...
```

### Protocol Specifications
1. **Minimum Training Samples**: 250 trading days (~1 calendar year).
2. **Out-of-Sample Test Window**: 60 trading days (~1 quarter).
3. **Purge Window (30 days)**: Strips training records immediately preceding the test split whose forward 30-day horizon overlaps with test timestamps.
4. **Embargo Gap (30 days)**: Imposes a 30-trading-day buffer following test splits before training data can be expanded, eliminating serial correlation spillover.

---

## 4. Benchmark Tournament & Empirical Validation

Every model is benchmarked against two rigorous baselines:
1. **Level 0 Baseline: Naive Random Walk with Zero Return Drift**:
   $$\hat{y}_{\text{naive}} = 0 \implies \hat{P}_{t+30} = P_t$$
2. **Level 1 Baseline: Facebook Prophet Time-Series Decomposition**:
   Decomposes price history into piecewise linear trend, weekly seasonality, and yearly seasonality.

### Summary Metrics Across 26 CSE Equities (`reports/cv_benchmark_summary.csv`)

| Metric | Multi-Quantile LightGBM | FB Prophet Baseline | Naive Zero Baseline | Alpha Edge |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Directional Accuracy** | **58.30%** | 55.25% | 50.00% | **+8.30% vs Naive** |
| **Root Mean Squared Error (RMSE)** | **0.0812** | 0.0964 | 0.1042 | **-22.1% error reduction** |
| **Mean Absolute Error (MAE)** | **0.0615** | 0.0748 | 0.0819 | **-24.9% error reduction** |
| **80% Quantile Coverage ($P_{10} \le y \le P_{90}$)** | **79.40%** | N/A | N/A | **Within 0.6% of theoretical 80%** |
| **Mean Pinball Loss** | **0.0241** | N/A | N/A | **Optimal quantile calibration** |

---

## 5. Dual-Layer Explainability Architecture

```text
                          Predicted 30-Day Return
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
┌───────────────────────────┐                       ┌───────────────────────────┐
│ Layer 1: TreeSHAP Engine  │                       │ Layer 2: Domain Heuristics│
│ (Exact Shapley Values)    │                       │ (Signal Alignment Cards)  │
├───────────────────────────┤                       ├───────────────────────────┤
│ • Math Attribution in Log │                       │ • RSI(14) Momentum        │
│   Return Units:           │                       │ • 20/50 SMA Cross Trend   │
│   y_hat = phi_0 + sum(phi)│                       │ • Parkinson Volatility    │
│ • Isolates top positive & │                       │ • MACD Histogram Diverg.  │
│   negative drivers        │                       │ • ASPI Benchmark Relative │
│ • Validated by exact addi-│                       │ • Outputs: Supporting vs. │
│   tivity test in pytest   │                       │   Rejecting/Risk Alert    │
└───────────────────────────┘                       └───────────────────────────┘
```

1. **TreeSHAP Mathematical Attribution**: Computes exact Shapley values directly over tree ensemble paths (`src/explainability/shap_service.py`), decomposing each technical indicator's exact basis-point contribution to predicted log returns.
2. **Domain Heuristics Validation Engine**: Rules engine (`src/explainability/heuristics_engine.py`) cross-verifies whether standard technical patterns confirm or warn against the quantitative model's direction.
