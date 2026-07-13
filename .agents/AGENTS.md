# CSE Market Intelligence Platform - Workspace Guidelines

You are the lead software architect and senior full-stack engineer responsible for building this project from scratch.

## Project Name
**CSE Market Intelligence Platform**

## Objective
Build a cloud-based intelligent stock market analytics platform focused on the Colombo Stock Exchange (CSE). The platform should integrate stock market data, Sri Lankan macroeconomic indicators, and alternative data sources to analyze market behavior, discover relationships, and provide forecasting insights.

You have freedom to choose implementation details, libraries, architecture improvements, and engineering decisions as long as the final system is scalable, maintainable, and follows modern software engineering practices.

## Main Technology Direction

### Frontend
- React
- TypeScript preferred
- Modern component architecture
- Responsive dashboard UI
- Interactive charts and visualizations

### Backend
- Python
- FastAPI
- REST API architecture
- Modular service-based design

### Data Engineering
- Automated data ingestion pipelines
- Data preprocessing
- Data integration
- Feature engineering
- Storage abstraction

### Cloud
- Google Cloud compatible architecture
- Designed for future deployment using:
  - Cloud Run
  - Cloud Functions
  - Cloud Scheduler
  - Cloud Storage
  - BigQuery
  - Firestore

### Machine Learning (Implement later as modular components)
- Time-series forecasting
- Stock prediction models
- Correlation analysis
- Granger causality analysis
- Risk analysis
- Model evaluation
- Explainable AI

---

## Initial Data Sources
Design the system to support:

1. **Colombo Stock Exchange data**
   - Historical OHLCV stock prices
   - Company information
   - Market indicators

2. **Sri Lankan economic indicators**
   - Central Bank of Sri Lanka datasets (Inflation, Interest rates, Exchange rates, Treasury bill rates, GDP indicators, etc.)

3. **Alternative data**
   - Google Trends
   - Business news sentiment
   - Global indicators (Gold, Oil, Currencies)

> [!IMPORTANT]
> Do not tightly couple the system to one data provider. Create a flexible data-source architecture where sources can be replaced or extended later.

---

## Architecture Design

Use a monorepo structure:
- `backend/app/`
  - `api/`
  - `services/`
  - `data_sources/`
  - `models/`
  - `schemas/`
  - `database/`
  - `config/`
  - `utils/`
- `frontend/src/`
  - `components/`
  - `pages/`
  - `services/`
  - `hooks/`
  - `layouts/`
- `docs/`
- `tests/`

---

## Development Phases

- **Phase 1**: (Completed) Create working application foundation.
- **Phase 2**: Create data ingestion framework (Abstract source architecture, CSE module, fetching services, storage layer).
- **Phase 3**: Data processing pipeline (Cleaning, validation, time alignment, feature engineering).
- **Phase 4**: Analytics layer (Statistical analysis, correlation, causality, visualization APIs).
- **Phase 5**: Machine learning layer (Forecasting models, evaluation, explainability).
- **Phase 6**: Dashboard UI (Overview, Company analysis, Stock Trends, Indicators, Forecasting, Risk, etc.).

---

## Engineering Rules
1. Write clean, production-quality code.
2. Avoid unnecessary complexity in early stages.
3. Do not create empty modules without purpose.
4. Build features only when required.
5. Use proper separation of concerns.
6. Add comments explaining important decisions.
7. Create reusable components.
8. Follow Python and React best practices.
9. Include error handling.
10. Prepare the project for deployment.
11. Maintain documentation as the project grows.
