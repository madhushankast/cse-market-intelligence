# Cloud Deployment Guide

The platform architecture is designed to support serverless containerized cloud deployment on **Google Cloud Platform (GCP)** or similar cloud environments.

## Deployment Target Topology

1. **Backend Service**:
   - **GCP Cloud Run**: Containerize backend using Docker (`uvicorn main:app --host 0.0.0.0 --port 8080`).
2. **Database**:
   - **Cloud Storage / BigQuery / Cloud SQL**: Migrate SQLite database layer to PostgreSQL (Cloud SQL) or BigQuery for large enterprise scale.
3. **Scheduled Ingestion**:
   - **GCP Cloud Scheduler & Cloud Functions**: Trigger periodic ingestion endpoints (`/api/v1/stocks/{symbol}/ingest`) on market close.
4. **Frontend Hosting**:
   - **Firebase Hosting / Vercel / Netlify**: Build static production assets (`npm run build`) and host over CDN.
