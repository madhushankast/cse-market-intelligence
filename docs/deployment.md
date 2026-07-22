# Deployment Guide

The **CSE Market Intelligence Platform** is architected to support cost-effective deployment. Since this is an academic research platform rather than an enterprise-scale commercial trading desk, it is designed to run entirely on **free-tier cloud services** with negligible maintenance costs.

---

## Recommended Deployment Topology

```text
                             Internet
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
           React + Vite UI               FastAPI Backend
          Cloudflare Pages            Render / Railway / Fly.io
                  │                             │
                  └──────────────┬──────────────┘
                                 │ REST API
                                 ▼
                         SQLite Database
                          (cse.db Storage)
                                 │
                                 ▼
                     Scheduled Ingestion / Training
                            (GitHub Actions)
```

---

## 1. Hosting Services Matrix

| Component | Target Service | Tier | Description |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | **Cloudflare Pages** | Free | Serves React static build files over high-speed CDNs. |
| **Backend REST API** | **Render / Railway** | Free | Hosts containerized FastAPI service. |
| **Database Engine** | **SQLite (`cse.db`)** | Free | Local serverless relational DB (can migrate to Cloud SQL / PostgreSQL). |
| **Data Update Pipeline**| **GitHub Actions** | Free | Triggers daily updates and runs retraining tasks off-site. |
| **Source Repository** | **GitHub** | Free | Code version control and automated CI/CD triggers. |

---

## 2. Frontend Deployment (Cloudflare Pages)

The React web application is compiled into static HTML/JS/CSS assets. Cloudflare Pages integrates directly with the GitHub repository:

*   **Build Command**: `npm run build`
*   **Publish Directory**: `dist`
*   **Configuration**:
    *   Set up a redirect rule in the `_redirects` file to route fallback calls to `index.html` to support React Router single-page navigation:
        ```text
        /* /index.html 200
        ```
    *   Set the frontend environment variable `VITE_API_BASE_URL` to point to the Render backend domain (e.g. `https://cse-api.onrender.com`).

---

## 3. Backend Deployment (Render Web Service)

FastAPI is deployed as a Docker service on Render. The root directory contains the `Dockerfile` specifying execution details.

*   **Dockerfile Configuration**:
    ```dockerfile
    FROM python:3.11-slim
    ENV PYTHONUNBUFFERED=1
    WORKDIR /workspace
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8080
    CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
    ```
*   **Free-Tier Inactivity Caveat**: On Render's free tier, the backend web service spins down after 15 minutes of inactivity. When a new request arrives, it may take 30–60 seconds to boot up.
*   **Environment Variables**:
    *   `ENV=production`
    *   `DATABASE_URL=sqlite:///cse.db`
    *   `CORS_ORIGINS=["https://your-frontend.pages.dev"]`

---

## 4. Database & File Persistence

For read-heavy research datasets, SQLite (`cse.db`) works perfectly. To handle SQLite's transient disk behavior on free container instances, we leverage an **offline/online decoupling strategy**:

```text
  ┌──────────────────────────────────────────────────────────────┐
  │ 1. OFFLINE PIPELINE (Scheduled Daily via GitHub Actions)     │
  │    - Fetches live stock data from CSE API.                   │
  │    - Preprocesses indicators & retrains XGBoost/SARIMAX.     │
  │    - Commits/uploads the updated cse.db and model artifacts.  │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ 2. ONLINE API SERVICE (FastAPI hosted on Render Web Service)  │
  │    - Downloads the committed cse.db on service startup.      │
  │    - Reads pre-computed forecasts and attributions directly. │
  │    - Exposes instantaneous API responses to the UI dashboard.│
  └──────────────────────────────────────────────────────────────┘
```

This decoupled approach ensures:
*   **Fast API Response**: Eliminates long-running ML training blocks on API requests.
*   **Zero Compute Overhead**: Model fitting is offloaded to GitHub Actions runner agents.

---

## 5. Scheduled Data Collection & CI/CD Pipeline

A GitHub Actions workflow script (`.github/workflows/daily_ingest.yml`) runs on a cron schedule to perform incremental updates:

```yaml
name: Daily CSE Ingestion and Model Training

on:
  schedule:
    - cron: '0 13 * * 1-5' # Runs at 18:30 IST (13:00 UTC) every weekday on market close
  workflow_dispatch:      # Allows manual trigger

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: pip install -r backend/requirements.txt

      - name: Execute Daily Pipeline Update
        run: |
          cd backend
          python -m app.pipelines.daily_pipeline

      - name: Commit Updated Database
        run: |
          git config --global user.name "Github Action Bott"
          git config --global user.email "action@github.com"
          git add backend/cse.db backend/data/
          git commit -m "auto: daily stock ingestion & model updates" || exit 0
          git push
```
