# Data Dictionary & Schema Specifications (Historical OHLCV Only)

Comprehensive data dictionary for the **Colombo Stock Exchange (CSE) Market Intelligence Platform**, documenting raw equities schemas and engineered technical feature matrices.

---

## 1. Raw Equities Data (OHLCV)

### 1.1 Individual Stock CSVs (`data/raw/cse/{SYMBOL}.csv`)
Historical daily trading bars for individual CSE listed equities.

| Field Name | Type | Unit / Format | Description | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `symbol` | String | String (`AAA.N0000`) | Standard CSE security identifier | Unique per trading date |
| `date` | Date | `YYYY-MM-DD` | Equities market trading session date | Mon–Fri excluding CSE holidays |
| `open` | Float | LKR | Opening auction execution price | $\text{open} > 0$ |
| `high` | Float | LKR | Highest recorded traded price of the session | $\text{high} \ge \max(\text{open}, \text{low}, \text{close})$ |
| `low` | Float | LKR | Lowest recorded traded price of the session | $\text{low} \le \min(\text{open}, \text{high}, \text{close})$ |
| `close` | Float | LKR | Official closing price (last traded price) | $\text{close} > 0$ |
| `volume` | Integer | Share units | Total number of shares executed | $\text{volume} \ge 0$ |

---

### 1.2 Multi-Year Archives (`data/raw/yearly/{YEAR}.csv`)
Official yearly bulk transaction dumps from the Colombo Stock Exchange (2021–2025).

| Header in Raw CSV | Normalized Column | Description |
| :--- | :--- | :--- |
| `COMPANY ID` | `symbol` | Ticker base code (e.g., `JKH`, `COMB`, `SAMP`) |
| `TRADING DATE` | `date` | Raw date format (`DD-MMM-YY`, e.g. `04-JAN-24`) |
| `OPEN PRICE (Rs.)` | `open` | Opening price in Sri Lankan Rupees |
| `PRICE HIGH (Rs.)` | `high` | Intraday high |
| `PRICE LOW (Rs.)` | `low` | Intraday low |
| `CLOSE PRICE (Rs.)` | `close` | Final closing price |
| `SHARE VOLUME (No.)` | `volume` | Executed volume in shares |
| `TURNOVER (Rs.)` | `turnover` | Total monetary turnover in LKR |

---

## 2. Engineered Technical Feature Store (`data/processed/cse_features.parquet`)

Tabular feature matrix derived strictly from historical OHLCV price action.

### 2.1 Returns & Intraday Ranges
| Feature Name | Type | Formula | Interpretation |
| :--- | :--- | :--- | :--- |
| `daily_return` | Float | $\frac{P_t - P_{t-1}}{P_{t-1}}$ | 1-day percentage price return |
| `log_return` | Float | $\ln\left(\frac{P_t}{P_{t-1}}\right)$ | Continuous 1-day logarithmic return |
| `high_low_pct` | Float | $\frac{\text{High}_t - \text{Low}_t}{\text{Low}_t}$ | Normalized daily high-low trading range |
| `open_close_pct` | Float | $\frac{\text{Close}_t - \text{Open}_t}{\text{Open}_t}$ | Intraday price displacement |

### 2.2 Trend & Moving Average Features
| Feature Name | Type | Parameter | Interpretation |
| :--- | :--- | :--- | :--- |
| `sma_{span}` | Float | $N \in \{10, 20, 50, 200\}$ | Simple Moving Average of closing prices |
| `ema_{span}` | Float | $\text{span} \in \{10, 20, 50, 200\}$ | Exponential Moving Average ($\alpha = \frac{2}{\text{span}+1}$) |
| `dist_ema_{span}` | Float | $\frac{\text{Close}_t - \text{EMA}_t}{\text{EMA}_t}$ | Normalized price distance from moving average |
| `price_to_sma_60`| Float | $\frac{\text{Close}_t}{\text{SMA}_{60}}$ | Medium-term trend ratio |

### 2.3 Momentum & Oscillator Features
| Feature Name | Type | Parameter | Interpretation |
| :--- | :--- | :--- | :--- |
| `rsi` | Float | Period = 14 | Wilder's Relative Strength Index ($\text{RSI} \in [0, 100]$) |
| `macd` | Float | Fast=12, Slow=26 | Difference between 12-EMA and 26-EMA |
| `macd_signal` | Float | Signal=9 | 9-day EMA of the MACD line |
| `macd_hist` | Float | — | MACD momentum histogram ($\text{MACD} - \text{Signal}$) |

### 2.4 Volatility Estimators
| Feature Name | Type | Formulation | Description |
| :--- | :--- | :--- | :--- |
| `parkinson_vol` | Float | $\sigma_P = \sqrt{\frac{252}{4 \ln 2 \cdot N} \sum_{i=1}^N \left(\ln\frac{H_i}{L_i}\right)^2}$ | Annualized Parkinson High-Low volatility ($N=20$) |
| `rolling_std_20` | Float | $\text{std}(\text{log\_return})_{20} \times \sqrt{252}$ | Classical annualized close-to-close volatility |
| `atr` | Float | Period = 14 | Average True Range |
| `atr_pct` | Float | $\frac{\text{ATR}_t}{\text{Close}_t}$ | Normalized volatility percentage |
| `bb_width` | Float | $\frac{\text{Upper BB} - \text{Lower BB}}{\text{SMA}_{20}}$ | Bollinger Band width |
| `bb_pct_b` | Float | $\frac{\text{Close} - \text{Lower BB}}{\text{Upper BB} - \text{Lower BB}}$ | Position of price relative to Bollinger Bands |

### 2.5 Volume Dynamics
| Feature Name | Type | Formula | Description |
| :--- | :--- | :--- | :--- |
| `volume_sma_20` | Float | $\text{rolling\_mean}(\text{volume}, 20)$ | 20-day baseline average share volume |
| `volume_ratio` | Float | $\frac{\text{volume}_t}{\text{volume\_sma\_20}}$ | Relative volume surge factor |

### 2.6 Autoregressive Lags
| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `return_lag_{k}` | Float | Historical log return lagged by $k \in \{1, 2, 3, 5, 10, 20\}$ trading days |
| `close_lag_{k}` | Float | Historical close price lagged by $k \in \{1, 2, 3, 5, 10, 20\}$ trading days |

### 2.7 Target Variable
| Field Name | Type | Formula | Description |
| :--- | :--- | :--- | :--- |
| `target_log_return_30d` | Float | $\ln\left(\frac{P_{t+30}}{P_t}\right)$ | 30-trading-day ahead forward cumulative log return |
