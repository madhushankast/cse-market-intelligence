# Database Schema

The platform utilizes SQLite (`cse.db`) for lightweight local persistence and fast local query speeds, managed using **SQLAlchemy ORM**.

## Table: `stock_prices`

| Column Name  | Data Type | Constraints               | Description                                  |
|--------------|-----------|---------------------------|----------------------------------------------|
| `id`         | Integer   | Primary Key, Indexed      | Unique record identifier                     |
| `symbol`     | String    | Indexed, Not Null         | Stock Ticker (e.g., `COMB.N0000`)            |
| `date`       | String    | Indexed, Not Null         | Trading Date (`YYYY-MM-DD`)                  |
| `open`       | Float     | Not Null                  | Daily open price                             |
| `high`       | Float     | Not Null                  | Daily high price                             |
| `low`        | Float     | Not Null                  | Daily low price                              |
| `close`      | Float     | Not Null                  | Daily close price                            |
| `volume`     | Integer   | Not Null                  | Traded volume                                |
| `created_at` | DateTime  | Default: UTC Now          | Database record insertion timestamp           |

## Connection & Pool Management
Database engine instantiation and connection pooling logic reside in [`backend/app/database/connection.py`](file:///c:/Ongoing%20Projects/New%20folder/backend/app/database/connection.py).
