# Colombo Stock Exchange (CSE) Market Intelligence Platform 📈🏛️

An intelligent, cloud-ready stock market analytics and forecasting platform designed to integrate equities data from the Colombo Stock Exchange (CSE), macroeconomic indicators from the Central Bank of Sri Lanka (CBSL), and public sentiment interest from Google Trends.

---

## 🌟 Key Features

- **Automated Data Ingestion**: Robust, resilient ingestion pipelines connecting to CSE APIs, CBSL macroeconomic datasets, and alternative web search metrics.
- **Cross-Frequency Alignment**: Custom time-series integration engine leveraging `pd.merge_asof` to synchronize high-frequency daily equities data with low-frequency monthly economic indicators.
- **Technical Indicators Engine**: Calculates standard financial metrics including RSI (14), SMA (20/50), MACD, and rolling daily return volatility.
- **Time-Series Forecasting**: Machine learning models designed for stock trend predictions over customizable validation horizons.
- **Explainable AI (XAI)**: SHAP feature importance visualizations highlighting macroeconomic impact on price movements.
- **Interactive UI Dashboard**: React-powered dashboard providing visual analytics, stock comparisons, and system status metrics.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────┐
│                     DATA SOURCES                       │
│  ┌─────────────────┐ ┌───────────────┐ ┌────────────┐  │
│  │  CSE REST API   │ │   CBSL CSV    │ │Google Trends│ │
│  └────────┬────────┘ └───────┬───────┘ └──────┬──────┘  │
└───────────┼──────────────────┼────────────────┼────────┘
            │                  │                │
            ▼                  ▼                ▼
┌────────────────────────────────────────────────────────┐
│               INGESTION & STORAGE LAYER                │
│                 SQLite Database (cse.db)               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               DATA ENGINEERING & PIPELINE              │
│  - Preprocessing & Technical Indicators (RSI, MACD)    │
│  - Asynchronous Cross-Frequency Data Merger            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FASTAPI REST API LAYER                 │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  REACT FRONTEND UI                     │
└────────────────────────────────────────────────────────┘
```

Detailed architectural specifications are available in [`docs/architecture.md`](file:///c:/Ongoing%20Projects/New%20folder/docs/architecture.md).

---

## 📂 Project Directory Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/             # REST API routers (/api/v1/)
│   │   ├── analytics/       # Technical indicators & statistical correlation engines
│   │   ├── forecasting/     # Time-series forecasting models
│   │   ├── explainability/  # SHAP feature importance explainers
│   │   ├── preprocessing/   # Data cleaning & time-alignment merger
│   │   ├── data_sources/    # Modular CSE, CBSL, Trends interfaces
│   │   ├── database/        # SQLAlchemy engine & models
│   │   ├── services/        # Orchestration & ingestion services
│   │   ├── core/            # App configurations & CORS settings
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Automated Pytest suite
│   ├── main.py              # Server execution script
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable React UI components
│   │   ├── pages/           # Dashboard views & analytics pages
│   │   ├── services/        # API HTTP client wrappers
│   │   └── App.jsx          # Main application router
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── docs/                    # System & API documentation
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── forecasting.md
│   └── deployment.md
├── run.txt                  # Quick start command reference
└── README.md                # Project README
```

---

## ⚡ Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI backend server
python main.py
```
The REST API will be accessible at `http://127.0.0.1:8000`. API documentation is automatically hosted at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Run development server
npm run dev
```
The React UI will run at `http://localhost:5173`.

---

## 📡 REST API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/v1/health` | Health check endpoint |
| `GET`  | `/api/v1/stocks/{symbol}` | Fetch equities price data |
| `POST` | `/api/v1/stocks/{symbol}/ingest` | Trigger symbol data ingestion |
| `GET`  | `/api/v1/analytics/stocks/{symbol}` | Compute technical indicator series |
| `GET`  | `/api/v1/analytics/stocks/{symbol}/integrated` | Integrated stock + macro dataset |
| `GET`  | `/api/v1/forecasting/{symbol}` | Time-series prediction horizons |
| `GET`  | `/api/v1/explanations/{symbol}` | SHAP feature attribution metrics |

Full REST API documentation is available in [`docs/api.md`](file:///c:/Ongoing%20Projects/New%20folder/docs/api.md).

---

## 🧪 Testing & Verification

Run backend unit and integration tests:

```bash
cd backend
pytest tests/
```

---

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, Pandas, NumPy
- **Machine Learning & Stats**: Statsmodels, XGBoost, Scikit-Learn, SHAP, Ta
- **Frontend**: React, TypeScript/JavaScript, Vite, Chart.js / Recharts
- **Database**: SQLite (Cloud-ready for PostgreSQL / GCP BigQuery)
