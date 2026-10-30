# Colombo Stock Exchange (CSE) Market Intelligence Platform
## 5-Pillar Portfolio Master Assets for ML / AI / Software Engineer

---

## 1. LinkedIn Post (Strictly 5 Pillars: Problem, Solution, Architecture, Tech, Accuracies)

> **Instructions for LinkedIn:**
> 1. Export the 5 slides from `docs/linkedin_presentation_deck.pptx` or print `docs/linkedin_presentation_deck.html` to PDF.
> 2. On LinkedIn, click **Start a post** $\to$ Click the **Document icon** $\to$ Upload your PDF.
> 3. Document Title: `Colombo Stock Exchange (CSE) ML Platform: 5 Core Pillars`
> 4. Paste the text below:

```markdown
Most stock market AI models fail in live trading. Here is how I engineered an end-to-end Quantitative Market Intelligence Platform for the Colombo Stock Exchange (CSE) across 5 core engineering pillars:

🚨 1. THE PROBLEM
Predicting raw stock prices is an anti-pattern. Because prices move slowly day-to-day, naive AI models just output yesterday's price as tomorrow's prediction. They boast a fake "98% R² accuracy" on paper, but have ZERO trading value. Furthermore, standard train/test splits cause lookahead data leakage, causing models to collapse in production.

💡 2. HOW I SOLVED IT
- Stationary Return Modeling: Instead of nominal prices, I modeled 30-day cumulative forward log returns [y = ln(P_t+30 / P_t)], forcing the models to learn real momentum and market cycles across 26 equities.
- Uncertainty Risk Envelopes: Replaced single price guesses with Multi-Quantile LightGBM (Pinball Loss) predicting a P10 downside floor, P50 median path, and P90 upside expansion.
- Leakage-Free Validation: Implemented an expanding 5-fold cross-validation engine with a 30-day purge buffer and 30-day embargo gap.

🏗️ 3. SYSTEM ARCHITECTURE
- Data Ingestion: Automated daily cron jobs syncing 26 CSE companies + ASPI index at 15:00 SLST market close.
- Vectorized Lakehouse: High-speed Apache Parquet store computing 22 indicators (Parkinson volatility, RSI, MACD, beta) in milliseconds.
- Backend API: Dockerized Python FastAPI on Render running real-time inferences and TreeSHAP explainability.
- Database & Web App: Supabase PostgreSQL (composite-key idempotent upserts) paired with a React 19 + TypeScript + TradingView terminal on Vercel.

⚙️ 4. TECHNOLOGIES USED
- AI & ML: LightGBM (Quantile Pinball Loss), Scikit-Learn, TreeSHAP Explainability, NumPy, Pandas.
- Data Engineering: Apache Parquet, DuckDB, PyArrow, Automated ETL Pipelines.
- Backend & Cloud: Python FastAPI, Docker Containers, PostgreSQL (Supabase), GitHub Actions CI/CD.
- Frontend & UI: React 19, TypeScript, TradingView Lightweight Charts, Vercel Edge.

📊 5. ACCURACIES & RESULTS
- 58.3% Directional Accuracy (+8.3% statistical edge over random walk baseline).
- 79.4% Empirical Coverage (actual prices remain inside the predicted P10-P90 risk envelope).
- 26 + 1 Tracked Assets updated daily in production.
- Audited via 29 automated Pytest unit tests in CI/CD verifying mathematical SHAP additivity and zero lookahead leakage.

Swipe through the carousel below to see the visual breakdown! 👇

🔗 GitHub: https://github.com/madhushankast/cse-market-intelligence

#MachineLearning #SoftwareEngineering #DataEngineering #Python #React #FastAPI #Docker #QuantitativeFinance #MLOps #AI
```

---

## 2. CV / Resume Description (Strictly 5 Pillars Format)

### For ML / AI / Software Engineer Resumes:

**CSE Quantitative Market Intelligence Platform** | *ML / Full-Stack Engineer*  
*Tech Stack: Python, LightGBM, Scikit-Learn, TreeSHAP, Apache Parquet, DuckDB, FastAPI, Docker, PostgreSQL, React 19, TypeScript*  
*GitHub: github.com/madhushankast/cse-market-intelligence*

- **The Problem Addressed**: Overcame the time-series persistence trap where naive models predict raw nominal prices with trivial identity bias ($P_{t+30} \approx P_t$), and eliminated lookahead leakage inherent in standard train/test splits.
- **How I Solved It**: Formulated a stationary quantitative target ($y_t = \ln(P_{t+30}/P_t)$) across 26 CSE equities; trained Multi-Quantile LightGBM models minimizing asymmetric Pinball Loss ($P_{10}, P_{50}, P_{90}$ risk envelopes); built a custom 5-fold Purged & Embargoed walk-forward cross-validation pipeline.
- **System Architecture**: Designed and deployed an automated cloud lakehouse: post-market ingestion (15:00 SLST cron), zero-copy Parquet feature store, containerized FastAPI REST API (Docker) on Render, Supabase PostgreSQL, and React 19 / TradingView dashboard on Vercel.
- **Technologies Used**: Python 3.11, LightGBM, Scikit-Learn, TreeSHAP, Apache Parquet, DuckDB, PyArrow, FastAPI, Docker, PostgreSQL, React 19, TypeScript, GitHub Actions CI/CD.
- **Accuracies & Quantifiable Results**: Achieved **58.3% out-of-sample directional accuracy** (+8.3% edge over random walk) and **79.4% empirical coverage** within the predicted uncertainty cone across 26 equities; audited via 29 automated Pytest unit tests in CI/CD.
