# Colombo Stock Exchange (CSE) Market Intelligence Platform
## LinkedIn Post & CV / Resume Master Assets for ML / AI / Software Engineer

---

## 1. LinkedIn Post (Ready to Copy & Paste)

> **Instructions for LinkedIn:**
> 1. Export your 5 slides from `docs/linkedin_presentation_deck.pptx` or print `docs/linkedin_presentation_deck.html` to PDF.
> 2. On LinkedIn, click **Start a post** $\to$ Click the **Document icon** (Add document) $\to$ Upload your PDF.
> 3. Document Title: `Why Most Stock AI Models Fail (And How to Build Real Financial ML)`
> 4. Paste the text below into the post caption:

```markdown
Most machine learning projects on stock markets fail for one simple reason:

They try to predict tomorrow’s exact price. 📉

If a stock closed at Rs. 100 today, a naive model will predict Rs. 100 tomorrow. It displays a deceptive 98% R² score, but in reality, it just built an expensive copy-paste machine with ZERO trading alpha.

Over the past few weeks, I engineered and deployed an end-to-end Quantitative Market Intelligence Platform for the Colombo Stock Exchange (CSE) to tackle this problem with actual engineering rigor.

Here is how I designed it from data pipeline to cloud deployment:

🔹 1. Formulated a Stationary Target
Instead of predicting nominal price levels, I modeled 30-day cumulative forward returns [y = ln(P_t+30 / P_t)]. This eliminates the unit-root persistence trap and forces the model to learn real momentum and mean-reversion cycles across 26 CSE blue-chip equities.

🔹 2. Built a Zero-Copy Data Lakehouse
Engineered a high-throughput columnar pipeline using Apache Parquet and DuckDB. Automated GitHub Actions cron jobs sync post-market data at 15:00 SLST daily, computing 22 vectorized market indicators (Parkinson volatility, Wilder RSI, MACD, and systematic ASPI beta) in milliseconds.

🔹 3. Quantified Uncertainty with Pinball Loss
Point forecasts are dangerous in volatile emerging markets. I trained Multi-Quantile LightGBM models minimizing Pinball Loss across 3 separate risk cones:
- P10 Floor: Downside Value-at-Risk boundary (penalizes extreme drawdowns 9x)
- P50 Median: Robust expected return path
- P90 Ceiling: Bullish momentum expansion resistance

🔹 4. Dual-Layer Explainable AI (XAI)
No "black boxes". Every inference breaks down into exact additive TreeSHAP contributions verified with unit tests, coupled with institutional trader health badges (Supporting, Risk Warning, Neutral).

🔹 5. 100% Live Cloud Deployment
- Backend: Containerized Python FastAPI with Docker on Render
- Frontend: React 19 + TypeScript + TradingView Lightweight Charts on Vercel
- Database: PostgreSQL 15 on Supabase with composite-key idempotent upserts
- Validation: 58.3% directional accuracy (+8.3% over random walk) with 79.4% empirical envelope coverage.

Swipe through the carousel below to see the architecture breakdown! 👇

Full open-source code & documentation:
🔗 GitHub: https://github.com/madhushankast/cse-market-intelligence

I’d love to hear feedback from quant researchers, ML engineers, and full-stack architects!

#MachineLearning #SoftwareEngineering #MLOps #Python #React #FastAPI #CloudArchitecture #QuantitativeFinance #DataEngineering #AI
```

---

## 2. Resume / CV Master Entries (Select the Version that Fits Your Resume Layout)

### Option A: Comprehensive Bullet Points (For 1-Page / 2-Page Tech Resume)

**Colombo Stock Exchange (CSE) Quantitative Market Intelligence Platform** | *Lead AI / Full-Stack Engineer*  
*Tech Stack: Python, LightGBM, Scikit-Learn, SHAP, Apache Parquet, DuckDB, FastAPI, Docker, PostgreSQL (Supabase), React 19, TypeScript, GitHub Actions*  
*GitHub: github.com/madhushankast/cse-market-intelligence*

- **End-to-End Financial ML Architecture**: Engineered and deployed an automated cloud platform analyzing 26 listed CSE equities and the All Share Price Index (ASPI), achieving **58.3% out-of-sample directional accuracy** (+8.3% edge over random walk baseline).
- **Time-Series Stationarity & Target Engineering**: Formulated a stationary 30-day forward log return target ($y_t = \ln(P_{t+30}/P_t)$), eliminating the $I(1)$ unit root persistence trap where naive models yield trivial identity predictions.
- **Leakage-Free Validation & Quantile Regression**: Built a custom expanding 5-fold walk-forward cross-validation engine enforcing a **30-day purge buffer** and **30-day embargo gap**; trained Multi-Quantile LightGBM optimizing asymmetric Pinball Loss ($P_{10}, P_{50}, P_{90}$), capturing **79.4% of real price moves** within predictive risk envelopes.
- **Vectorized Data Lakehouse**: Designed a zero-copy columnar feature store using Apache Parquet and DuckDB to compute 22 market microstructure features (Parkinson volatility, Wilder RSI, MACD, ASPI relative beta) in sub-millisecond execution times.
- **Explainable AI (XAI) Engine**: Implemented exact additive TreeSHAP local attributions ($y = \phi_0 + \sum \phi_i$) backed by automated unit tests enforcing mathematical additivity, mapped to domain heuristic validation badges (Supporting, Risk, Neutral).
- **Full-Stack Cloud Deployment & CI/CD**: Shipped a containerized Python FastAPI REST API (Docker) on Render, an interactive React 19 + TypeScript terminal with TradingView charts on Vercel, Supabase PostgreSQL, and automated daily post-market ETL/retraining workflows via GitHub Actions.

---

### Option B: Concise Version (3 Bullet Points for High-Density Resumes)

**CSE Market Intelligence Platform** | *Python, LightGBM, FastAPI, React 19, Docker, Supabase, CI/CD*  
*Link: github.com/madhushankast/cse-market-intelligence*

- Architected a cloud-native quantitative intelligence system for 26 Colombo Stock Exchange equities, achieving **58.3% directional accuracy** via stationary target formulation and multi-quantile LightGBM ($P_{10}, P_{50}, P_{90}$ Pinball Loss).
- Prevented time-series lookahead leakage by engineering a custom expanding 5-fold Purged & Embargoed walk-forward cross-validation pipeline, processing 22 vectorized technical indicators via an Apache Parquet/DuckDB lakehouse.
- Deployed a production-ready zero-cost cloud topology: Dockerized FastAPI backend on Render, React 19/TypeScript dashboard on Vercel, Supabase PostgreSQL, automated daily GitHub Actions post-market ETL, and unit-tested TreeSHAP explainability.

---

## 3. Skills Matrix for LinkedIn / Resume Profile

Copy and paste these exact keywords into your LinkedIn **Skills** section or resume header:

* **Machine Learning & AI**: Time-Series Forecasting, Quantile Regression, Gradient Boosted Trees (LightGBM), Scikit-Learn, Explainable AI (SHAP / TreeSHAP), Feature Engineering, Statistical Stationarity, Validation Design.
* **Data Engineering & MLOps**: Apache Parquet, DuckDB, PyArrow, ETL Pipeline Automation, Purged & Embargoed Cross-Validation, Continuous Integration / Continuous Deployment (CI/CD), Model Auditing.
* **Backend & Systems**: Python 3.11, FastAPI, REST APIs, Docker Containerization, PostgreSQL, Supabase, Automated Cron Workflows (GitHub Actions).
* **Frontend & Visualization**: React 19, TypeScript, TradingView Lightweight Charts, Responsive UI, Vercel Edge.
