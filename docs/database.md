# Database Schema

The platform utilizes SQLite (`cse.db`) for lightweight local persistence and fast local query speeds. Object Relational Mapping (ORM) is managed via **SQLAlchemy**.

Database engine instantiation and connection pooling logic reside in [`backend/app/database/connection.py`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/connection.py), while the model class declarations are located in [`backend/app/database/models.py`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/models.py) and separate model files.

---

## 1. Table: `stock_prices`
Stores historical and ingested daily OHLCV stock data.
- **Model Class**: `StockPrice` ([models.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/models.py))

| Column Name  | Data Type | Constraints               | Description                                  |
|--------------|-----------|---------------------------|----------------------------------------------|
| `id`         | Integer   | Primary Key, Indexed      | Unique record identifier                     |
| `symbol`     | String    | Indexed, Not Null         | Stock Ticker (e.g., `COMB`, `JKH`, `SAMP`)   |
| `date`       | String    | Indexed, Not Null         | Trading Date (`YYYY-MM-DD`)                  |
| `open`       | Float     | Not Null                  | Daily open price                             |
| `high`       | Float     | Not Null                  | Daily high price                             |
| `low`        | Float     | Not Null                  | Daily low price                              |
| `close`      | Float     | Not Null                  | Daily close price                            |
| `volume`     | Integer   | Not Null                  | Traded volume                                |
| `created_at` | DateTime  | Default: UTC Now          | Database record insertion timestamp          |

---

## 2. Table: `alternative_data`
Stores macroeconomic indicators and web search interest indicators.
- **Model Class**: `AlternativeData` ([models.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/models.py))

| Column Name  | Data Type | Constraints          | Description                                                    |
|--------------|-----------|----------------------|----------------------------------------------------------------|
| `id`         | Integer   | Primary Key, Indexed | Unique record identifier                                       |
| `source`     | String    | Indexed, Not Null    | Source of data (e.g., `CBSL`, `Google`)                        |
| `indicator`  | String    | Indexed, Not Null    | Name of indicator (e.g., `Inflation_CCPI`, `ExchangeRate_USD`) |
| `date`       | String    | Indexed, Not Null    | Reference date (`YYYY-MM-DD` or `YYYY-MM`)                     |
| `value`      | Float     | Not Null             | Value of the indicator                                         |
| `frequency`  | String    | Not Null             | Periodicity (e.g., `Daily`, `Weekly`, `Monthly`)               |
| `created_at` | DateTime  | Default: UTC Now     | Database record insertion timestamp                            |

---

## 3. Table: `forecast_results`
Stores the outputs from forecasting runs.
- **Model Class**: `ForecastResult` ([models.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/models.py))

| Column Name        | Data Type | Constraints          | Description                                              |
|--------------------|-----------|----------------------|----------------------------------------------------------|
| `id`               | Integer   | Primary Key, Indexed | Unique record identifier                                 |
| `symbol`           | String    | Indexed, Not Null    | Stock symbol forecasted                                  |
| `date`             | String    | Indexed, Not Null    | Forecast generation date                                 |
| `model`            | String    | Not Null             | Model type (e.g. `xgboost`, `sarimax`, `baseline`)       |
| `horizon`          | Integer   | Not Null             | Forecast step horizon in trading days                    |
| `expected_return`  | Float     | Not Null             | Estimated returns over horizon                           |
| `forecast_values`  | Text      | Not Null             | JSON serialized array of forecasted close prices         |
| `explanation_json` | Text      | Nullable             | JSON serialized SHAP or parameter coefficient details    |
| `created_at`       | DateTime  | Default: UTC Now     | Model execution run timestamp                            |

---

## 4. Table: `job_logs`
Tracks pipeline job executions, monitoring runtime health and processing volumes.
- **Model Class**: `JobLog` ([job_log.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/models/job_log.py))

| Column Name      | Data Type | Constraints          | Description                                       |
|------------------|-----------|----------------------|---------------------------------------------------|
| `id`             | Integer   | Primary Key, Indexed | Unique log record identifier                      |
| `pipeline`       | String    | Indexed, Not Null    | Name of pipeline executed (e.g. `Daily Pipeline`) |
| `started_at`     | DateTime  | Not Null, Default    | Initialization timestamp                          |
| `finished_at`    | DateTime  | Nullable             | Completion timestamp                              |
| `status`         | String    | Not Null             | State of job (`Running`, `Success`, `Failed`)     |
| `rows_processed` | Integer   | Default: 0           | Number of rows modified or ingested               |
| `error_message`  | Text      | Nullable             | Stack trace details if job status is `Failed`     |

---

## 5. Table: `prediction_explanations`
Logs detailed feature impact scores for auditability and forecasting explanation stability analysis.
- **Model Class**: `PredictionExplanationLog` ([prediction_explanation.py](file:///c:/Ongoing%20Projects/New%20folder/backend/app/models/prediction_explanation.py))

| Column Name          | Data Type | Constraints               | Description                                            |
|----------------------|-----------|---------------------------|--------------------------------------------------------|
| `id`                 | Integer   | Primary Key, Indexed      | Unique record identifier                               |
| `symbol`             | String    | Indexed, Not Null         | Stock symbol being explained                           |
| `model`              | String    | Not Null                  | Prediction engine utilized                             |
| `prediction`         | Float     | Nullable                  | Forecasted target price                                |
| `confidence`         | Float     | Nullable                  | Model confidence estimation                            |
| `baseline_value`     | Float     | Nullable                  | Baseline expected value of target                      |
| `explanation_method` | String    | Not Null                  | explainer format (e.g., `SHAP`, `Coefficients`)        |
| `feature_name`       | String    | Not Null                  | Name of feature input (e.g., `rsi`, `ExchangeRate_USD`)|
| `impact`             | Float     | Not Null                  | Directional SHAP value / coefficient value             |
| `abs_impact`         | Float     | Not Null                  | Absolute impact value for ranking                      |
| `direction`          | String    | Not Null                  | Impact category: `positive` or `negative`              |
| `feature_rank`       | Integer   | Nullable                  | Relative rank of feature importance (1 = highest)       |
| `warning`            | Text      | Nullable                  | Explainer evaluation warnings                          |
| `created_at`         | DateTime  | Indexed, Default: UTC Now | Log entry creation timestamp                           |
