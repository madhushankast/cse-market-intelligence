# Modeling Strategy & Evaluation Framework (Strictly Historical OHLCV)

This document details the quantitative foundation, target formulation, technical indicator mechanics, and validation protocols powering the **Colombo Stock Exchange (CSE) Market Intelligence Platform**.

---

## 1. Target Formulation: Avoiding Nominal Price Traps

A common failure mode in financial machine learning is training models to forecast nominal prices ($y_t = P_{t+h}$). This approach suffers from critical statistical defects:

1. **Unit Roots & Non-Stationarity ($I(1)$)**:
   Asset prices follow stochastic non-stationary trends. Models trained on raw price levels degenerate into trivial lag followers:
   $$\hat{P}_{t+1} \approx P_t$$
   This produces artificial $R^2 > 0.95$ metrics while offering zero predictive capability.
2. **Scale Invariance Across Equities**:
   CSE equities trade at widely different nominal prices (e.g., JKH at ~LKR 160 vs. CARG at ~LKR 380 vs. DIAL at ~LKR 11). Standardizing to continuous returns eliminates scale sensitivity.
3. **Compound Return Additivity**:
   Continuous logarithmic returns are strictly additive across time horizons:
   $$r_{t, t+k} = \sum_{i=1}^k r_{t+i-1, t+i}$$

### Mathematical Definition of the Target
The supervised target is formulated as the **30-trading-day ahead cumulative forward log return**:
$$y_t = \ln\left(\frac{P_{t+30}}{P_t}\right) = \ln(P_{t+30}) - \ln(P_t)$$

At inference, given current price $P_t$ and predicted quantile return $\hat{y}_{t+h, q}$, future nominal prices are reconstructed:
$$P_{t+h, q} = P_t \cdot \exp\left(\hat{y}_{t+30, q} \cdot \frac{h}{30}\right) \quad \text{for } h \in [1, 30]$$

---

## 2. Technical Feature Engineering (Strictly OHLCV)

All feature inputs are derived exclusively from historical price action and trading volume:

### 2.1 Wilder's Relative Strength Index (RSI)
Measures the velocity and magnitude of directional price movements:
$$U_t = \max(P_t - P_{t-1}, 0), \quad D_t = \max(P_{t-1} - P_t, 0)$$
$$\text{RS}_t = \frac{\text{EMA}(U, 14)}{\text{EMA}(D, 14)}, \quad \text{RSI}_t = 100 - \frac{100}{1 + \text{RS}_t}$$

### 2.2 Moving Average Convergence Divergence (MACD)
Captures shifting exponential trend momentum:
$$\text{MACD}_t = \text{EMA}_{12}(P_t) - \text{EMA}_{26}(P_t)$$
$$\text{Signal}_t = \text{EMA}_9(\text{MACD}_t), \quad \text{Hist}_t = \text{MACD}_t - \text{Signal}_t$$

### 2.3 Parkinson High-Low Volatility Estimator
A high-efficiency extreme-value volatility estimator that leverages intraday High and Low extremes rather than close-to-close prices:
$$\sigma_P = \sqrt{\frac{252}{4 \ln(2) \cdot N} \sum_{i=1}^N \left(\ln\frac{\text{High}_i}{\text{Low}_i}\right)^2}$$
Parkinson volatility is approximately 5 times more efficient than traditional close-to-close volatility estimators.

### 2.4 Bollinger Bands (%B)
Measures price position relative to rolling standard deviation bands:
$$\text{Upper} = \text{SMA}_{20} + 2\sigma_{20}, \quad \text{Lower} = \text{SMA}_{20} - 2\sigma_{20}$$
$$\%B = \frac{\text{Close} - \text{Lower}}{\text{Upper} - \text{Lower}}$$

---

## 3. Purged & Embargoed Walk-Forward Cross-Validation

Standard $K$-Fold cross-validation is fundamentally invalid in time-series forecasting. Two leakage channels must be mitigated:

```text
Time Horizon: ────────────────────────────────────────────────────────►
Fold k:       [======== Train Window ========] [ Embargo Gap ] [== Test Window ==]
                                               <-- 30 Days -->
```

1. **Forward Label Overlap (Purging)**:
   Because target $y_t$ incorporates price data up to $t+30$, training observations at $t \in [T_{\text{test}} - 30, T_{\text{test}} - 1]$ utilize forward price data that spills into the test set. All training rows within 30 days prior to the test set are strictly purged.
2. **Serial Autocorrelation (Embargoing)**:
   Volatility and momentum clustering create memory spillover. An embargo buffer of $E = 30$ trading days is enforced between the end of the training window and the evaluation period.

---

## 4. Asymmetric Quantile Loss (Pinball Loss)

Rather than outputting a single point estimate, the platform models return uncertainty using **Multi-Quantile LightGBM** for quantiles $\alpha \in \{0.10, 0.50, 0.90\}$.

The model minimizes the asymmetric **Pinball Loss**:
$$\mathcal{L}_\alpha(y, \hat{y}) = \begin{cases} \alpha(y - \hat{y}) & \text{if } y \ge \hat{y} \\ (1 - \alpha)(\hat{y} - y) & \text{if } y < \hat{y} \end{cases} = \max\left(\alpha(y - \hat{y}), (\alpha - 1)(y - \hat{y})\right)$$

- **$P_{10}$ ($\alpha=0.10$)**: Downside risk boundary.
- **$P_{50}$ ($\alpha=0.50$)**: Conditional median return expectation.
- **$P_{90}$ ($\alpha=0.90$)**: Bullish expansion boundary.

---

## 5. Benchmark Tournament

LightGBM is benchmarked against standard quantitative baselines across every walk-forward fold:

| Model | Architecture | Role |
| :--- | :--- | :--- |
| **Naive Random Walk** | $\hat{y}_{t+h} = 0, \hat{P}_{t+h} = P_t$ | Martingale baseline testing market efficiency |
| **Historical Rolling Drift** | $\hat{y}_{t+h} = h \cdot \mu_{\text{daily}}$ | Captures secular market drift without features |
| **FB Prophet** | $y(t) = g(t) + s(t) + \epsilon_t$ | Trend & seasonality benchmark |
| **Multi-Quantile LightGBM** | Gradient-boosted decision trees | Primary model capturing non-linear OHLCV interactions |

---

## 6. Dual-Layer Explainability

1. **TreeSHAP Attributions (Lundberg et al., 2020)**:
   Exact Shapley value calculation decomposing each feature's contribution:
   $$f(x) = \phi_0 + \sum_{j=1}^M \phi_j(x)$$
2. **Retail Technical Heuristics**:
   Rule engine classifying indicators into intuitive badges:
   - **"Supporting"**: Indicator agrees with predicted forecast direction (e.g. Bullish forecast with RSI $<30$ oversold recovery).
   - **"Rejecting"**: Indicator signals caution against the forecast (e.g. Bullish forecast with RSI $>70$ or Parkinson volatility $>40\%$).
   - **"Neutral"**: Indicator is in equilibrium.
