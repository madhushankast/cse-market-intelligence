"""
CSE Market Intelligence Platform - Interactive Executive Dashboard
-------------------------------------------------------------------
Visualizes 30-day multi-quantile forecast cones (P10, P50, P90),
TreeSHAP mathematical attributions, domain indicator heuristics,
and model benchmark validation tables across all 26 CSE equities.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path when running via Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from src.modeling.predict import ModelRegistryService
from src.ingestion.cse_scraper import CSEScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard")

# Streamlit Page Setup
st.set_page_config(
    page_title="CSE 30-Day Market Intelligence Cockpit",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Institutional CSS Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        height: 100%;
    }
    .metric-header {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 4px;
    }
    .badge-supporting {
        background-color: rgba(35, 134, 54, 0.2);
        color: #3fb950;
        border: 1px solid #238636;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-rejecting {
        background-color: rgba(218, 54, 51, 0.2);
        color: #f85149;
        border: 1px solid #da3633;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-neutral {
        background-color: rgba(139, 148, 158, 0.2);
        color: #8b949e;
        border: 1px solid #30363d;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_model_service():
    """Initializes and caches ModelRegistryService."""
    return ModelRegistryService(
        raw_dir="data/raw",
        processed_dir="data/processed",
        models_dir="models",
    )


@st.cache_data
def load_all_equities() -> List[Dict[str, Any]]:
    """Loads all 26 available equities from data/processed/*.parquet."""
    processed_dir = Path("data/processed")
    files = sorted(processed_dir.glob("*.parquet"))

    # Load tickers.yaml mapping
    tickers_file = Path("configs/tickers.yaml")
    meta_map = {}
    if tickers_file.exists():
        with open(tickers_file, "r", encoding="utf-8") as f:
            t_data = yaml.safe_load(f)
            for item in t_data.get("tickers", []):
                sym = item.get("symbol", "").replace(".", "_")
                meta_map[sym] = item

    equities = []
    for f in files:
        if f.stem == "ASPI":
            continue
        stem = f.stem
        meta = meta_map.get(stem, {})
        code = meta.get("code", stem.split("_")[0])
        name = meta.get("name", stem.split("_")[0] + " PLC")
        sector = meta.get("sector", "Colombo Equities")
        equities.append({
            "symbol": stem,
            "code": code,
            "name": name,
            "sector": sector,
            "display": f"{code} - {name}",
        })
    return equities


@st.cache_data
def load_benchmark_report() -> Optional[pd.DataFrame]:
    """Loads cross-validation benchmark summary report."""
    rep_path = Path("reports/cv_benchmark_summary.csv")
    if rep_path.exists():
        return pd.read_csv(rep_path)
    return None


def main():
    service = get_model_service()
    equities = load_all_equities()

    if not equities:
        st.error("No processed stock parquet files found in data/processed/.")
        return

    # -------------------------------------------------------------
    # Sidebar Navigation & Controls
    # -------------------------------------------------------------
    st.sidebar.markdown("## 🏛️ CSE Intelligence")
    st.sidebar.caption("30-Day Multi-Quantile Forecasting Engine")

    equities_display = [e["display"] for e in equities]
    selected_display = st.sidebar.selectbox("Select Security", equities_display, index=0)
    selected_stock = next(e for e in equities if e["display"] == selected_display)
    selected_symbol = selected_stock["symbol"]

    horizon_days = st.sidebar.slider(
        "Forecast Horizon (Trading Days)",
        min_value=10,
        max_value=60,
        value=30,
        step=5,
        help="Target forward prediction window in trading days.",
    )

    if st.sidebar.button("🔄 Refresh Live Quotes", use_container_width=True):
        with st.sidebar.status("Connecting to official CSE API..."):
            try:
                scraper = CSEScraper()
                norm_sym = selected_stock["code"] + ".N0000"
                quote = scraper.pull_latest_ohlcv(norm_sym)
                if not quote.empty:
                    st.sidebar.success(f"Latest CSE bar fetched ({len(quote)} records).")
                else:
                    st.sidebar.info("Market closed. Using preserved historical data.")
            except Exception as e:
                st.sidebar.warning(f"Live CSE quote notice: {e}")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Security Code:** `{selected_stock['code']}`")
    st.sidebar.markdown(f"**Sector:** {selected_stock['sector']}")
    st.sidebar.markdown("**Engine:** Multi-Quantile LightGBM ($P_{10}, P_{50}, P_{90}$)")
    st.sidebar.markdown("**Validation:** Purged Walk-Forward (30d Embargo)")
    st.sidebar.markdown("**Input Scope:** Strictly Historical Stock OHLCV + ASPI")

    # -------------------------------------------------------------
    # Compute Inference & Explainability Payload
    # -------------------------------------------------------------
    with st.spinner(f"Computing 30-day forecast & TreeSHAP attributions for {selected_stock['name']}..."):
        try:
            df = service.get_processed_data(selected_symbol)
            forecast = service.predict(selected_symbol, horizon_days=horizon_days, explain=True)
        except Exception as exc:
            st.error(f"Failed to generate prediction for {selected_symbol}: {exc}")
            return

    # -------------------------------------------------------------
    # Main Dashboard Header & Top Metrics
    # -------------------------------------------------------------
    st.title(f"{selected_stock['name']} ({selected_stock['code']})")
    st.caption(f"As of: **{forecast['as_of_date']}** | Horizon: **{horizon_days} Trading Days** | Monotonic Prediction Interval: **P10 to P90**")

    curr_price = forecast["current_price"]
    tp = forecast["target_prices"]
    tr = forecast["target_returns"]
    exp_pct = tr["expected_pct_change"]
    p10_price = tp["price_p10"]
    p50_price = tp["price_p50"]
    p90_price = tp["price_p90"]

    p10_pct = ((p10_price - curr_price) / curr_price) * 100.0
    p90_pct = ((p90_price - curr_price) / curr_price) * 100.0

    # Macro Market Alignment
    heuristics = forecast.get("indicator_heuristics", [])
    supporting_count = sum(1 for h in heuristics if h["status"] == "Supporting")
    total_heuristics = len(heuristics)
    market_status = "Tailwind Alignment" if supporting_count >= 4 else ("Headwinds / Caution" if supporting_count <= 2 else "Selective Alignment")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">Current Price</div>
            <div class="metric-value">LKR {curr_price:,.2f}</div>
            <div style="color: #8b949e; font-size: 0.85rem;">Last CSE trade close</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        ret_color = "#3fb950" if exp_pct >= 0 else "#f85149"
        sign = "+" if exp_pct >= 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">Expected Target (P50)</div>
            <div class="metric-value" style="color: {ret_color};">LKR {p50_price:,.2f}</div>
            <div style="color: {ret_color}; font-size: 0.9rem; font-weight: 600;">{sign}{exp_pct:.2f}% (Expected 30d Return)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">P10 Downside Floor</div>
            <div class="metric-value" style="color: #f85149;">LKR {p10_price:,.2f}</div>
            <div style="color: #f85149; font-size: 0.9rem; font-weight: 600;">{p10_pct:+.2f}% 90% VaR Floor</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">P90 Bullish Ceiling</div>
            <div class="metric-value" style="color: #3fb950;">LKR {p90_price:,.2f}</div>
            <div style="color: #3fb950; font-size: 0.9rem; font-weight: 600;">{p90_pct:+.2f}% Upside Target</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Interactive Plotly Multi-Quantile Forecast Cone
    # -------------------------------------------------------------
    st.subheader("🎯 30-Day Multi-Quantile Forecast Cone")

    hist_bars = df.tail(90)
    traj_df = pd.DataFrame(forecast["cone_trajectory"])
    traj_df["date"] = pd.to_datetime(traj_df["date"])

    fig = go.Figure()

    # Historical price curve
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(hist_bars["date"]),
        y=hist_bars["close"],
        mode="lines",
        name="Historical Close (LKR)",
        line=dict(color="#58a6ff", width=2.5),
    ))

    # P90 Ceiling Line
    fig.add_trace(go.Scatter(
        x=traj_df["date"],
        y=traj_df["price_p90"],
        mode="lines",
        name="P90 Upside Ceiling",
        line=dict(color="rgba(63, 185, 80, 0.6)", width=1.5, dash="dash"),
    ))

    # P10 Floor Line with Shaded Band
    fig.add_trace(go.Scatter(
        x=traj_df["date"],
        y=traj_df["price_p10"],
        mode="lines",
        name="P10 Downside Floor",
        fill="tonexty",
        fillcolor="rgba(35, 134, 54, 0.15)",
        line=dict(color="rgba(248, 81, 73, 0.6)", width=1.5, dash="dash"),
    ))

    # P50 Expected Path
    fig.add_trace(go.Scatter(
        x=traj_df["date"],
        y=traj_df["price_p50"],
        mode="lines+markers",
        name="P50 Expected Median Trajectory",
        line=dict(color="#3fb950" if exp_pct >= 0 else "#f85149", width=3),
        marker=dict(size=4),
    ))

    fig.update_layout(
        template="plotly_dark",
        height=480,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Trading Session",
        yaxis_title="Price (LKR)",
        hovermode="x unified",
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
    )
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------
    # Dual-Layer Explainability & Benchmark Validation Tabs
    # -------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs([
        "🛡️ Technical Indicator Signals (Layer 2)",
        "📊 TreeSHAP Feature Drivers (Layer 1)",
        "🏆 Model Benchmark Ladder",
    ])

    # TAB 1: DOMAIN INDICATOR HEURISTICS
    with tab1:
        st.markdown("#### Institutional Heuristic Alignment Cards")
        st.caption("Validates mathematical model projections against technical price/volume and ASPI benchmark indicators.")

        if heuristics:
            # Render grid of cards (3 columns x 2 rows)
            rows = [heuristics[i:i + 3] for i in range(0, len(heuristics), 3)]
            for row_cards in rows:
                cols = st.columns(len(row_cards))
                for idx, card in enumerate(row_cards):
                    status = card["status"]
                    badge_class = (
                        "badge-supporting" if status == "Supporting"
                        else ("badge-rejecting" if "Rejecting" in status or "Risk" in status else "badge-neutral")
                    )

                    with cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="color: #f0f6fc; font-size: 1.05rem;">{card['indicator']}</strong>
                                <span class="{badge_class}">{card['status']}</span>
                            </div>
                            <div style="color: #8b949e; font-size: 0.85rem; margin-bottom: 6px;">
                                <strong>Reading:</strong> <span style="color: #58a6ff;">{card['value']}</span> | <strong>Stance:</strong> {card.get('signal', 'Neutral')}
                            </div>
                            <p style="font-size: 0.88rem; color: #c9d1d9; margin-top: 8px; line-height: 1.4;">
                                {card['explanation']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No indicator heuristic cards generated for this security.")

    # TAB 2: TREESHAP FEATURE ATTRIBUTION
    with tab2:
        st.markdown("#### Exact TreeSHAP Mathematical Decomposition")
        st.caption("Calculates local Shapley contributions (phi_i) explaining the deviation from historical average return.")

        shap_data = forecast.get("shap_explanation", {})
        pos_drivers = shap_data.get("top_positive_drivers", [])
        neg_drivers = shap_data.get("top_negative_drivers", [])
        base_val = shap_data.get("base_value", 0.0)
        pred_val = shap_data.get("predicted_return", 0.0)

        c1, c2 = st.columns([3, 2])

        with c1:
            combined_drivers = pos_drivers + neg_drivers
            if combined_drivers:
                shap_df = pd.DataFrame(combined_drivers)
                shap_df = shap_df.sort_values("shap_impact", ascending=True)

                colors = ["#3fb950" if imp > 0 else "#f85149" for imp in shap_df["shap_impact"]]

                bar_fig = go.Figure(go.Bar(
                    x=shap_df["shap_impact_pct"],
                    y=shap_df["description"],
                    orientation="h",
                    marker_color=colors,
                    text=[f"{v:+.2f}%" for v in shap_df["shap_impact_pct"]],
                    textposition="auto",
                ))
                bar_fig.update_layout(
                    template="plotly_dark",
                    height=360,
                    margin=dict(l=10, r=20, t=20, b=20),
                    xaxis_title="Percentage-Point Contribution to 30-Day Return (%)",
                    plot_bgcolor="#0d1117",
                    paper_bgcolor="#0d1117",
                )
                st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.info("No TreeSHAP attributions available.")

        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">Shapley Additivity Identity</div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #c9d1d9;">
                    <strong>Historical Base Value (phi_0):</strong> {base_val:+.4f}<br>
                    <strong>Net Feature Contributions (sum phi_i):</strong> {(pred_val - base_val):+.4f}<br>
                    <strong>Final Expected 30d Return:</strong> <span style="color: {'#3fb950' if pred_val >= 0 else '#f85149'}; font-weight:700;">{pred_val:+.4f}</span>
                </div>
                <hr style="border-color: #30363d;">
                <p style="font-size: 0.85rem; color: #8b949e;">
                    TreeSHAP calculates exact additive Shapley values based on tree path conditionality, guaranteeing zero attribution leakage.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if combined_drivers:
                st.dataframe(
                    pd.DataFrame(combined_drivers)[["feature", "value", "shap_impact_pct", "direction"]].rename(
                        columns={
                            "feature": "Feature",
                            "value": "Value",
                            "shap_impact_pct": "Impact (%)",
                            "direction": "Direction",
                        }
                    ),
                    use_container_width=True,
                    height=180,
                )

    # TAB 3: BENCHMARK MODEL COMPARISON
    with tab3:
        st.markdown("#### Cross-Validation Benchmark Ladder (26 CSE Equities)")
        st.caption("Walk-forward cross-validation with 30-day embargo gap comparing Multi-Quantile LightGBM vs. Naive and Prophet baselines.")

        bench_df = load_benchmark_report()
        if bench_df is not None:
            # Summary stats
            avg_lgb = bench_df["lgb_dir_acc"].mean()
            avg_edge = bench_df["dir_acc_edge_vs_naive"].mean()
            avg_rmse = bench_df["lgb_rmse"].mean()
            avg_cov = bench_df["lgb_coverage_80"].mean()

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LGB Mean Directional Acc", f"{avg_lgb:.2f}%", delta=f"{avg_edge:+.2f}% vs Naive")
            m2.metric("Market Naive Baseline", "50.00%", delta="Random Walk")
            m3.metric("LGB Mean RMSE", f"{avg_rmse:.4f}")
            m4.metric("Empirical 80% CI Coverage", f"{avg_cov:.1f}%", delta="Target: 80.0%")

            st.dataframe(
                bench_df[[
                    "symbol", "lgb_dir_acc", "naive_dir_acc", "prophet_dir_acc",
                    "dir_acc_edge_vs_naive", "lgb_rmse", "naive_rmse", "lgb_mean_pinball", "lgb_coverage_80"
                ]].rename(columns={
                    "symbol": "Security",
                    "lgb_dir_acc": "LGB Hit %",
                    "naive_dir_acc": "Naive Hit %",
                    "prophet_dir_acc": "Prophet Hit %",
                    "dir_acc_edge_vs_naive": "LGB Edge (%)",
                    "lgb_rmse": "LGB RMSE",
                    "naive_rmse": "Naive RMSE",
                    "lgb_mean_pinball": "Pinball Loss",
                    "lgb_coverage_80": "Coverage (80%)",
                }),
                use_container_width=True,
                height=350,
            )
        else:
            st.info("Run `python scripts/train_all_models.py` to generate reports/cv_benchmark_summary.csv.")


if __name__ == "__main__":
    main()
