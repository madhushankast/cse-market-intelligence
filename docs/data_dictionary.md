# Data Dictionary & Feature Engineering Specification

## 1. Primary Data Sources

The platform ingests price and volume series directly from official CSE digital endpoints:

| Series | Endpoint / Source | Frequency | Attributes |
| :--- | :--- | :--- | :--- |
| **Equities OHLCV** | CSE API (`https://www.cse.lk/api/companyChartDataByStock`) | Daily EOD | `date`, `open`, `high`, `low`, `close`, `volume` |
| **ASPI Index** | CSE API (`https://www.cse.lk/api/aspiData`) | Daily EOD | `date`, `close`, `change`, `pct_change`, `volume` |

---

## 2. Feature Store Schema (`FEATURE_COLUMNS`)

All 22 features used in model training and inference are mathematically computed in `src/features/technical_features.py` strictly from past information to ensure **zero lookahead bias**:

### 2.1 Multi-Horizon Return Momentum Features

| Feature Name | Type | Description | Mathematical Formulation |
| :--- | :--- | :--- | :--- |
| `return_1d` | float | 1-Day Log Return | $r_{1d} = \ln(P_t / P_{t-1})$ |
| `return_5d` | float | 5-Day Cumulative Log Return (1 week) | $r_{5d} = \ln(P_t / P_{t-5})$ |
| `return_10d` | float | 10-Day Cumulative Log Return (2 weeks) | $r_{10d} = \ln(P_t / P_{t-10})$ |
| `return_20d` | float | 20-Day Cumulative Log Return (1 month) | $r_{20d} = \ln(P_t / P_{t-20})$ |
| `return_30d` | float | 30-Day Cumulative Log Return | $r_{30d} = \ln(P_t / P_{t-30})$ |

---

### 2.2 Classical Technical Indicators

| Feature Name | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `rsi_14` | float | $[0, 100]$ | 14-period Wilder Relative Strength Index measuring speed and change of price movements. |
| `macd` | float | $\mathbb{R}$ | Moving Average Convergence Divergence: $\text{EMA}_{12}(P) - \text{EMA}_{26}(P)$. |
| `macd_signal` | float | $\mathbb{R}$ | 9-period Exponential Moving Average of the MACD line. |
| `macd_hist` | float | $\mathbb{R}$ | MACD Histogram: $\text{MACD} - \text{MACD}_{\text{signal}}$, capturing momentum inflection. |
| `ema_ratio_12_26` | float | $> 0$ | Ratio of 12-day to 26-day EMA: $\text{EMA}_{12} / \text{EMA}_{26} - 1.0$. |
| `sma_ratio_20_50` | float | $> 0$ | Trend strength ratio: $\text{SMA}_{20} / \text{SMA}_{50} - 1.0$. Captures golden/death crosses. |

---

### 2.3 Microstructure & Volatility Estimators

| Feature Name | Type | Description | Mathematical Formulation |
| :--- | :--- | :--- | :--- |
| `parkinson_vol` | float | Daily Parkinson High-Low Volatility | $\sigma_P = \sqrt{\frac{(\ln(H_t / L_t))^2}{4 \ln 2}}$ (5x more efficient than close-to-close) |
| `parkinson_vol_10d` | float | 10-day rolling mean of $\sigma_P$ | $\frac{1}{10}\sum_{i=0}^{9} \sigma_{P, t-i}$ |
| `parkinson_vol_20d` | float | 20-day rolling mean of $\sigma_P$ | $\frac{1}{20}\sum_{i=0}^{19} \sigma_{P, t-i}$ |
| `high_low_spread` | float | Normalized daily trading range | $(H_t - L_t) / C_t$ |
| `log_volume` | float | Log-transformed trading volume | $\ln(V_t + 1)$ |
| `volume_surge_ratio` | float | Volume expansion vs 20d baseline | $V_t / (\frac{1}{20}\sum_{i=1}^{20} V_{t-i} + \epsilon)$ |

---

### 2.4 ASPI Market-Relative Benchmark Dynamics

| Feature Name | Type | Description | Purpose |
| :--- | :--- | :--- | :--- |
| `aspi_return_5d` | float | 5-day cumulative log return of ASPI | General market short-term momentum. |
| `aspi_return_10d` | float | 10-day cumulative log return of ASPI | General market intermediate trend. |
| `aspi_return_30d` | float | 30-day cumulative log return of ASPI | Broad market cyclical state. |
| `relative_strength_30d` | float | Asset 30d return minus ASPI 30d return | Outperformance / underperformance spread ($\alpha$). |
| `rolling_corr_aspi_30d` | float | 30-day rolling Pearson correlation with ASPI | Systematic market beta alignment. |

---

## 3. Data Hygiene & Outlier Cleaning

In `src/features/technical_features.py`:
1. **Zero / Negative Price Handling**: Forward-fills previous valid close prices.
2. **Infinite Values**: `np.inf` values resulting from zero volume divisions are replaced with `0.0`.
3. **Missing Value Imputation**: Median backward/forward imputation for leading rolling windows.
4. **Target Alignment**: Forward 30-day targets are shifted strictly backwards ($t + 30$), and trailing 30 days without realized targets are reserved for live inference.
