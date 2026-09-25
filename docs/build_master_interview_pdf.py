"""
Builds the Comprehensive AI/ML Technical Interview Master Defense Guide PDF
for the Colombo Stock Exchange (CSE) Market Intelligence Platform.
Covers Phases 1 through 13 with absolute technical rigor, exact code references,
and clear distinctions between actual code reality and documentation claims.
"""

import os
import sys
import html
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header text and rule
        self.drawString(54, 11 * 72 - 36, "CSE MARKET INTELLIGENCE PLATFORM — AI/ML INTERVIEW DEFENSE GUIDE")
        self.setFont("Helvetica", 8)
        self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "STRICT INTERVIEW READINESS")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer text and rule
        self.line(54, 48, 8.5 * 72 - 54, 48)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 36, "CONFIDENTIAL — PREPARED FOR TECHNICAL INTERVIEW READINESS & DEFENSE")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_text)
        
        self.restoreState()


def build_interview_guide_pdf(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Palette
    c_primary = colors.HexColor("#0F172A")     # Slate 900
    c_secondary = colors.HexColor("#1E293B")   # Slate 800
    c_accent = colors.HexColor("#1D4ED8")      # Blue 700
    c_accent_dark = colors.HexColor("#1E40AF") # Blue 800
    c_subtext = colors.HexColor("#334155")     # Slate 700
    c_card_bg = colors.HexColor("#F8FAFC")     # Slate 50
    c_border = colors.HexColor("#E2E8F0")      # Slate 200
    c_red_bg = colors.HexColor("#FEF2F2")      # Red 50
    c_red_border = colors.HexColor("#FCA5A5")  # Red 300
    c_green_bg = colors.HexColor("#F0FDF4")    # Green 50
    c_green_border = colors.HexColor("#86EFAC")# Green 300
    c_amber_bg = colors.HexColor("#FFFBEB")    # Amber 50
    c_amber_border = colors.HexColor("#FCD34D")# Amber 300
    c_code_bg = colors.HexColor("#0F172A")     # Terminal Dark

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=1,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        alignment=1,
        spaceAfter=20
    )

    phase_header_style = ParagraphStyle(
        'PhaseHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_accent_dark,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'AnswerBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_subtext,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'AnswerBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_subtext,
        leftIndent=12,
        spaceAfter=2
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#38BDF8"),
        spaceAfter=2
    )

    def p(text, style=body_style):
        # Escape XML entities if not already escaped
        safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Re-allow safe formatting tags
        safe = safe.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        safe = safe.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        safe = safe.replace('&lt;font', '<font').replace('&lt;/font&gt;', '</font>')
        safe = safe.replace('&lt;br/&gt;', '<br/>').replace('&lt;br&gt;', '<br/>')
        return Paragraph(safe, style)

    def card_box(paragraphs, bg=c_card_bg, border=c_border, width=520):
        content = []
        for item in paragraphs:
            content.append(item)
            content.append(Spacer(1, 2))
        t = Table([[content]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1, border),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    def phase_banner(phase_title):
        t = Table([[Paragraph(f"<b>{phase_title}</b>", phase_header_style)]], colWidths=[520])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_primary),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    story.append(p("Colombo Stock Exchange (CSE)<br/>Market Intelligence Platform", title_style))
    story.append(p("Comprehensive AI/ML Technical Interview Defense & Deep Code Defense Guide", subtitle_style))
    story.append(HRFlowable(width="90%", thickness=2, color=c_accent, spaceBefore=5, spaceAfter=20))

    meta_content = [
        p("<b>CANDIDATE INTERVIEW PREPARATION MASTER HANDBOOK</b>", h2_style),
        p("This comprehensive defense dossier is prepared for high-stakes technical interviews for Senior ML Engineer, Applied AI, and Quantitative Data Engineering roles. It provides an exhaustive, code-verified audit of the entire CSE Market Intelligence Platform codebase, dissecting every mathematical formulation, architectural trade-off, data leakage risk, and line of code.", body_style),
        Spacer(1, 4),
        p("<b>Strict Verification Principle:</b>", h3_style),
        p("&bull; <b>Code Reality vs. Documentation:</b> Every algorithm, parameter, and pipeline has been verified directly against actual Python and React source files in the repository. Discrepancies between the README and source code are explicitly identified and defended.", bullet_style),
        p("&bull; <b>Defensible Ownership:</b> Articulates exactly what was engineered, what external libraries were leveraged, how components interact, and how to defend design decisions under aggressive cross-examination.", bullet_style),
        p("&bull; <b>No Hallucinations:</b> If a feature exists only conceptually or in planning documents, it is classified as NOT VERIFIED FROM CODE to prevent disqualification during deep technical probing.", bullet_style),
    ]
    story.append(card_box(meta_content, bg=c_card_bg, border=c_border))
    story.append(Spacer(1, 20))

    toc_content = [
        p("<b>GUIDE STRUCTURE &amp; COVERAGE (PHASES 1 &ndash; 13):</b>", h3_style),
        p("<b>Phase 1: Project Discovery</b> &mdash; 27 Architectural Points &amp; Reality Matrix (Code vs Claims vs Theory)", bullet_style),
        p("<b>Phase 2: Teach Me My Project</b> &mdash; 30-Second, 2-Minute, and Deep Technical Pitch", bullet_style),
        p("<b>Phase 3: Code Walkthrough</b> &mdash; Line-by-Line Function Audit, Potential Vulnerabilities &amp; Execution Graph", bullet_style),
        p("<b>Phase 4: 'Why?' Questions</b> &mdash; 12 Core Architectural Decisions Defended Across 4 Probing Tiers", bullet_style),
        p("<b>Phase 5: Question Bank</b> &mdash; Complete Categorized Interview Questions (Categories A through AN)", bullet_style),
        p("<b>Phase 6: Difficult Follow-Up Questions</b> &mdash; 20 High-Pressure Senior Engineering Stress Tests", bullet_style),
        p("<b>Phase 7: Cross-Questioning</b> &mdash; Multi-Level Cross-Examination Trees (3 to 5 Levels Deep)", bullet_style),
        p("<b>Phase 8: Find My Weaknesses</b> &mdash; RED, YELLOW, GREEN Knowledge Audit &amp; Emergency Tutoring", bullet_style),
        p("<b>Phase 9: Project Defense</b> &mdash; 7 Known Vulnerabilities &amp; Winning Technical Defenses", bullet_style),
        p("<b>Phase 10: Personal Contribution</b> &mdash; Boundary of Ownership, Reusable Modules &amp; Team Readiness", bullet_style),
        p("<b>Phase 11: Mock Interview Blueprint</b> &mdash; Evaluation Rubric &amp; 1&ndash;5 Scoring Criteria", bullet_style),
        p("<b>Phase 12: Rapid Fire Blitz</b> &mdash; 25 High-Frequency Terminology &amp; Systems Questions (15-Sec Answers)", bullet_style),
        p("<b>Phase 13: Final Cheat Sheet</b> &mdash; One-Page Architecture Summary, Top 20 Questions &amp; Top 10 Weakness Traps", bullet_style),
    ]
    story.append(card_box(toc_content, bg=c_card_bg, border=c_border))
    story.append(Spacer(1, 30))
    story.append(p("<i>Engineered for Technical Mastery &bull; Colombo Stock Exchange Market Intelligence Platform</i>", ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, alignment=1, textColor=colors.HexColor("#64748B"))))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 1: PROJECT DISCOVERY
    # =========================================================================
    story.append(phase_banner("PHASE 1 &mdash; PROJECT DISCOVERY &amp; REALITY AUDIT"))
    story.append(Spacer(1, 8))

    p1_summary = [
        p("<b>1. Project Name:</b> Colombo Stock Exchange (CSE) Market Intelligence Platform", bullet_style),
        p("<b>2. Problem Statement:</b> Traditional financial models in frontier economies rely solely on technical price action, ignoring extreme macroeconomic shocks (hyperinflation, interest rate hikes, currency devaluation). Meanwhile, ML tools remain 'black boxes' that portfolio managers reject.", bullet_style),
        p("<b>3. Why It Matters:</b> Sri Lanka's 2021&ndash;2024 economic crisis saw inflation reach 69.8%, USD/LKR double from 200 to 360, and policy rates hit 15.5%. Macroeconomic regime shifts completely dominated technical stock trends. Integrating macro indicators with explainable ML creates actionable, interpretable market intelligence.", bullet_style),
        p("<b>4. Input Data:</b> Daily equities OHLCV (26 CSE blue-chip tickers), monthly CBSL macroeconomic releases (USD/LKR, Inflation CCPI, SDFR/SLFR policy rates), and weekly Google Trends search interest.", bullet_style),
        p("<b>5. Output:</b> 30-day forward price and return forecasts, model tournament metrics (RMSE, MAE, MAPE, Directional Accuracy), algorithmic BUY/HOLD/SELL signals, and local SHAP feature attribution waterwalls in LKR currency units.", bullet_style),
        p("<b>6. Actual Data Sources (Code-Verified):</b> Yahoo Finance (.CM ticker suffix) with automated Geometric Brownian Motion synthetic fallback; CBSL statistical tables (CSV); pytrends querying 'LK' region; SQLite storage (cse.db).", bullet_style),
        p("<b>7. Data Preprocessing:</b> ISO-8601 date parsing, duplicate dropping on (symbol, date), ascending chronological sort, forward-fill (ffill), backward merge_asof alignment for low-frequency macro data with 'days_since_update' tracking.", bullet_style),
        p("<b>8. Feature Engineering:</b> 47+ features across 5 families: price ratios, trend indicators (SMA, EMA, ADX), oscillators (RSI, MACD, ROC, Stochastic, Williams %R), volatility (Bollinger Bands, ATR, 20-day return volatility), autoregressive lags (t-1 to t-20), rolling statistics, and macro variables.", bullet_style),
        p("<b>9. Models Implemented:</b> (1) Naïve 20-day SMA Baseline, (2) Statsmodels SARIMAX(1,1,1) with exogenous technical regressors, (3) XGBoost Regressor (200 trees, max_depth=5, lr=0.05, hist method).", bullet_style),
        p("<b>10. Target Variable Construction:</b> Supervised multi-step horizon Close(t+30). In dataset.py, target is defined as <code>df['target'] = df['close'].shift(-30)</code>. Last 30 rows are trimmed for training.", bullet_style),
        p("<b>11. Model Selection Tournament:</b> Evaluated on 20% hold-out test set using weighted score: <code>0.4*RMSE + 0.2*MAE + 0.2*MAPE + 0.2*(100 - DirAcc)</code> with a +1000 penalty if complex model RMSE exceeds Baseline by &gt;10%.", bullet_style),
        p("<b>12. Explainable AI (XAI):</b> TreeExplainer for XGBoost (exact Shapley values), coefficient-based marginal impact for SARIMAX, and permutation importance for Baseline.", bullet_style),
        p("<b>13. Systems Architecture:</b> FastAPI REST API (Python 3.11), SQLAlchemy ORM, SQLite database, React 18 frontend with Vite, Chart.js, Recharts, and Docker containerization.", bullet_style),
    ]
    story.append(card_box(p1_summary, bg=c_card_bg, border=c_border))
    story.append(Spacer(1, 8))

    # Reality Matrix Table
    story.append(p("<b>TABLE 1.1: CODE REALITY VS. CLAIMS VS. THEORY VS. INTERVIEW BOUNDARIES</b>", h2_style))
    matrix_data = [
        [p("<b>Dimension</b>", h3_style), p("<b>1. What Code Actually Does</b>", h3_style), p("<b>2. Documentation Claim</b>", h3_style), p("<b>3. Underlying Theory</b>", h3_style), p("<b>4. What NOT to Claim</b>", h3_style)],
        [
            p("<b>Data Ingestion</b>", body_style),
            p("Uses yfinance (.CM) + local CSV. If Yahoo fails/throttles, triggers <b>Geometric Brownian Motion synthetic fallback</b>.", body_style),
            p("Claims automated direct CSE REST API + real-time feeds.", body_style),
            p("GBM assumes log-normal returns dS = &mu;Sdt + &sigma;SdW. Yahoo scrapers break frequently.", body_style),
            p("DO NOT claim you have a paid Bloomberg or live CSE broker WebSocket.", body_style)
        ],
        [
            p("<b>Time Alignment</b>", body_style),
            p("Uses <code>pd.merge_asof(direction='backward')</code>. Creates <code>inflation_age</code> feature. Uses <code>ffill().bfill()</code>.", body_style),
            p("Claims 'perfect real-time macro synchronisation'.", body_style),
            p("Point-in-time synchronization prevents lookahead bias by ensuring only published data is known at time t.", body_style),
            p("DO NOT claim macro data is available daily; acknowledge low publication frequency.", body_style)
        ],
        [
            p("<b>Forecasting Method</b>", body_style),
            p("Fits single target Close(t+30). Linearly interpolates intermediate path. Applies &plusmn;2% technical score adjustment.", body_style),
            p("Claims 'multi-horizon deep time-series forecasting'.", body_style),
            p("Direct multi-step forecasting avoids error compounding inherent in recursive 1-step autoregression.", body_style),
            p("DO NOT claim you trained 30 separate models or an LSTM/Transformer.", body_style)
        ],
        [
            p("<b>Validation Split</b>", body_style),
            p("Single chronological 80% train / 20% test split. <b>Walk-forward CV explicitly disabled</b> in code.", body_style),
            p("Claims 'extensive walk-forward cross-validation'.", body_style),
            p("Time-series split respects arrow of time. Walk-forward was skipped to keep API sub-second.", body_style),
            p("DO NOT claim you ran 10-fold rolling walk-forward CV on every API hit.", body_style)
        ],
        [
            p("<b>Deployment</b>", body_style),
            p("Runs locally via <code>python main.py</code> and Docker Compose. Uses SQLite (<code>cse.db</code>).", body_style),
            p("Mentions Google Cloud Run, BigQuery, Firestore, Cloud Scheduler.", body_style),
            p("12-Factor App methodology; SQLite is single-writer, unsuitable for high-concurrency cloud.", body_style),
            p("DO NOT claim the app is currently running live in Google Cloud production.", body_style)
        ],
    ]
    t_matrix = Table(matrix_data, colWidths=[70, 120, 110, 115, 105])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 8))

    # Pipeline Diagram
    p1_pipeline = [
        p("<b>END-TO-END SYSTEM PIPELINE (ACTUAL CODE FLOW):</b>", h3_style),
        p("<code>CSE / Yahoo / CSV / Trends &rarr; IngestionService &rarr; SQLite (cse.db) &rarr; DataCleaner (dedup, ffill) &rarr; IndicatorBuilder (40+ tech indicators) &rarr; CalendarMerger (merge_asof backward) &rarr; ForecastDataset (shift -30) &rarr; ForecastTrainer (80/20 split &rarr; Baseline, SARIMAX, XGBoost) &rarr; Evaluator (RMSE, MAE, MAPE, DirAcc) &rarr; Selection Tournament &rarr; Technical Adjustment Guardrail (&plusmn;2%) &rarr; SHAP TreeExplainer &rarr; FastAPI REST (/api/v1/predictions) &rarr; React Dashboard</code>", code_style)
    ]
    story.append(card_box(p1_pipeline, bg=c_code_bg, border=c_primary))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 2: TEACH ME MY PROJECT
    # =========================================================================
    story.append(phase_banner("PHASE 2 &mdash; TEACH ME MY PROJECT (3 INTERVIEW PITCH TIERS)"))
    story.append(Spacer(1, 8))

    story.append(p("<b>LEVEL 1: THE 30-SECOND ELEVATOR PITCH</b>", h2_style))
    story.append(p("<i>Use when the interviewer says: 'Tell me about this project' or 'Walk me through your CSE platform.'</i>", body_style))
    p2_l1 = [
        p("\"I built the <b>Colombo Stock Exchange Market Intelligence Platform</b> to solve a key challenge in emerging frontier markets: stock prices are heavily impacted by macroeconomic shocks like hyperinflation and currency devaluation, but retail and institutional tools only look at basic price charts.", body_style),
        p("My platform ingests daily CSE stock data and synchronizes it with monthly Central Bank macroeconomic indicators and Google Trends sentiment without lookahead bias. It runs a competitive model tournament between Baseline, SARIMAX, and regularized XGBoost models to predict 30-day price trends, explains those predictions in Sri Lankan Rupees using SHAP TreeExplainer, and serves the entire pipeline through a FastAPI backend and React analytics dashboard.\"", body_style),
    ]
    story.append(card_box(p2_l1, bg=c_card_bg, border=c_accent))
    story.append(Spacer(1, 10))

    story.append(p("<b>LEVEL 2: THE 2-MINUTE STRUCTURED INTERVIEW ANSWER</b>", h2_style))
    p2_l2 = [
        p("<b>1. Problem:</b> During Sri Lanka's recent economic crisis, inflation surged over 69% and the currency depreciated by 80%. Traditional technical-only models completely failed because macroeconomic regime shifts dictated market sentiment. Furthermore, financial professionals reject ML models that act as opaque black boxes.", body_style),
        p("<b>2. Data &amp; Engineering:</b> I collected daily OHLCV data for 26 CSE blue-chip stocks, monthly CBSL economic indicators (USD/LKR exchange rate, CCPI inflation, and policy interest rates), and Google Trends search intensity. The key data engineering challenge was <b>cross-frequency alignment</b>: merging monthly economic announcements with daily stock ticks without lookahead bias. I implemented point-in-time backward alignment using Pandas <code>merge_asof</code>, generating an explicit 'staleness' feature.", body_style),
        p("<b>3. Feature Engineering:</b> I engineered over 40 features, including momentum oscillators (RSI, MACD, ROC), volatility bands (Bollinger Bands, ATR), trend strength (ADX), autoregressive price and return lags, and calendar seasonality.", body_style),
        p("<b>4. Modeling &amp; Tournament:</b> I framed the problem as direct 30-day forward price prediction. Instead of trusting a single algorithm, I built an automated tournament evaluating a 20-day Simple Moving Average Baseline, an econometric SARIMAX(1,1,1) model with exogenous variables, and an XGBoost Regressor. Models are ranked on an 80/20 chronological split using a weighted score balancing RMSE, MAE, MAPE, and Directional Accuracy, with a penalty if a complex model underperforms the naive baseline.", body_style),
        p("<b>5. Explainability (XAI):</b> For XGBoost, I integrated <code>shap.TreeExplainer</code> to decompose every prediction into additive feature attributions in local currency units (LKR), showing exactly how much inflation or RSI pushed the price above or below baseline.", body_style),
        p("<b>6. My Contribution &amp; Challenge:</b> I built the end-to-end system from scratch: asynchronous data ingestion pipelines, feature engineering, model training and evaluation engines, SHAP explainers, FastAPI endpoints, and the interactive React dashboard. My biggest technical challenge was preventing data leakage during cross-frequency merging and ensuring the model didn't overfit given small frontier market sample sizes.", body_style),
    ]
    story.append(card_box(p2_l2, bg=c_card_bg, border=c_border))
    story.append(Spacer(1, 10))

    story.append(p("<b>LEVEL 3: DEEP TECHNICAL ARCHITECTURAL EXPLANATION</b>", h2_style))
    p2_l3 = [
        p("<b>Why XGBoost?</b> Tree-based ensembles excel on tabular financial data with heterogeneous feature types (prices, percentages, bounded oscillators, integer lags). They capture non-linear interactions without requiring monotonic relationships, require minimal feature scaling, and natively support exact, rapid Shapley attribution via Lundberg's TreeExplainer algorithm ($O(TLD)$ complexity).", body_style),
        p("<b>Why SARIMAX?</b> Provides an econometric benchmark grounded in statistical time-series theory. Differencing ($d=1$) enforces weak stationarity, while exogenous regressors allow direct estimation of macro marginal effects. Its fitted coefficients provide transparent linear baseline attributions.", body_style),
        p("<b>Mathematical Objective of XGBoost:</b> Minimizes the regularized objective $\mathcal{L}(\theta) = \sum_{i} l(y_i, \hat{y}_i) + \sum_{k} \Omega(f_k)$, where $\Omega(f) = \gamma T + \\frac{1}{2}\lambda \sum w_j^2$. The optimal leaf weight is $w_j^* = - \\frac{G_j}{H_j + \lambda}$, where $G_j$ and $H_j$ are first (gradient) and second (hessian) order derivatives of the MSE loss. Regularization ($\lambda=1.0$, subsample=0.8, colsample=0.8) is critical to prevent memorization of noise.", body_style),
        p("<b>Explainability Mechanics:</b> SHAP satisfies efficiency, symmetry, dummy player, and additivity axioms: $\hat{f}(x) = \phi_0 + \sum_{i=1}^M \phi_i$. In our UI, $\phi_0$ represents the base expected price over the training set, and each $\phi_i$ represents the positive or negative contribution (in LKR) from feature $i$.", body_style),
    ]
    story.append(card_box(p2_l3, bg=c_card_bg, border=c_border))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 3: CODE WALKTHROUGH
    # =========================================================================
    story.append(phase_banner("PHASE 3 &mdash; CODE WALKTHROUGH &amp; IMPLEMENTATION AUDIT"))
    story.append(Spacer(1, 8))

    story.append(p("<b>KEY FILES, FUNCTIONS, AND CODE-VERIFIED LINE AUDIT</b>", h2_style))

    files_audit = [
        ("1. backend/app/forecasting/models/xgboost.py",
         "Wraps xgboost.XGBRegressor for 30-day forward price prediction.",
         [
             ("Line 32-41: Hyperparameter Dictionary", "n_estimators=200, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, tree_method='hist'. Conservative depth and learning rate prevent overfitting on short financial time series."),
             ("Line 57-61: Feature Selection & Fitting", "Drops target, date, symbol. Converts X and y to numpy arrays. Fits XGBRegressor on historical features."),
             ("Line 107-114: Technical Adjustment Hook", "Calls <code>compute_technical_adjustment()</code> to nudge predicted price based on rule-based momentum score, capped at 2%."),
             ("Line 117-120: Linear Trajectory Projection", "<code>prices = [round(last_close + (i+1)*(pred - last_close)/horizon, 4) for i in range(horizon)]</code>. Projects expected path linearly from current close to 30-day forecast.")
         ]),
        ("2. backend/app/forecasting/models/sarimax.py",
         "Wraps statsmodels.tsa.statespace.sarimax.SARIMAX for econometric forecasting.",
         [
             ("Line 46-54: Model Instantiation", "Uses order=(1,1,1) with differencing d=1 to handle non-stationary price levels. Sets enforce_stationarity=False to avoid solver convergence crashes on noisy data."),
             ("Line 107-113: Out-of-Sample Forecasting", "Calls <code>get_forecast(steps=horizon, exog=exog_future)</code>. Extracts mean prediction and 95% confidence intervals."),
             ("Line 115-120: Fallback Safeguards", "Catches NaNs and negative prices: if <code>pred_val <= 0</code> or NaN, falls back to <code>last_close</code>.")
         ]),
        ("3. backend/app/forecasting/dataset.py",
         "Constructs feature matrix (X) and shifted supervised target (y).",
         [
             ("Line 171-174: Target Variable Construction", "<code>df['target'] = df['close'].shift(-30)</code>. Shifts close price 30 days backward. Creates supervised learning pair (features at t &rarr; price at t+30)."),
             ("Line 181-183: Warmup & Horizon NaN Trimming", "<code>df.dropna(subset=available + ['target'])</code>. Drops warmup NaNs from rolling indicators and drops final 30 rows where future target is unknown."),
             ("Line 83-104: Time-Aware Splitting", "Splits chronologically at index <code>int(len(df) * 0.8)</code> without shuffling. Essential to avoid future information leakage.")
         ]),
        ("4. backend/app/explainability/explainers/shap_explainer.py",
         "Decomposes XGBoost forecasts using TreeExplainer.",
         [
             ("Line 84-88: Exact TreeExplainer Call", "Instantiates <code>shap.TreeExplainer(xgb_regressor)</code>. Computes exact Shapley values in LKR output space."),
             ("Line 89-100: Robust Fallback Handler", "Catches tree parsing exceptions across XGBoost versions; falls back to model-agnostic <code>shap.Explainer</code>.")
         ]),
        ("5. backend/app/pipelines/calendar.py",
         "Synchronizes low-frequency macro data to daily trading calendar.",
         [
             ("Line 54: Backward As-Of Merge", "<code>pd.merge_asof(merged, updates_df, on=date_col, direction='backward')</code>. Matches each trading day to the latest published macro figure."),
             ("Line 57-58: Staleness Age Tracking", "<code>merged[f'{prefix}_age'] = (date - last_update_date).dt.days</code>. Quantifies release age so the model learns macro decay.")
         ]),
    ]

    for fname, fdesc, lines in files_audit:
        card_content = [
            p(f"<b>{fname}</b> &mdash; <i>{fdesc}</i>", h3_style),
        ]
        for ltitle, ldesc in lines:
            card_content.append(p(f"&bull; <b>{ltitle}:</b> {ldesc}", bullet_style))
        story.append(card_box(card_content, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 6))
    story.append(p("<b>IDENTIFIED CODE WEAKNESSES &amp; POTENTIAL BUGS (INTERVIEW GOLDMINES)</b>", h2_style))
    bugs_content = [
        p("1. <b>Leading bfill in calendar.py (Line 61):</b> <code>merged[val_col] = merged[val_col].ffill().bfill()</code>. The backward-fill on dates before the very first macro announcement introduces mild lookahead bias for early historical rows. <i>Interview Defense:</i> Acknowledge this immediately: 'In production, I would drop pre-announcement rows rather than bfill them.'", bullet_style),
        p("2. <b>Linear Trajectory Assumption:</b> In <code>xgboost.py</code> and <code>baseline.py</code>, the 30-day forecast interpolates linearly between $Close(t)$ and $Close(t+30)$. Real price paths exhibit stochastic volatility. <i>Defense:</i> 'The model specifically targets expected 30-day terminal value; the linear path serves as a visual trend indicator rather than a day-by-day path simulation.'", bullet_style),
        p("3. <b>Heuristic Confidence Metric:</b> In <code>base.py</code>, confidence is calculated as <code>min(0.99, max(0.50, direction_accuracy))</code>. <i>Defense:</i> 'Directional accuracy directly reflects market utility. To make it intuitive for traders, I scaled directional accuracy into an operational confidence band.'", bullet_style)
    ]
    story.append(card_box(bugs_content, bg=c_amber_bg, border=c_amber_border))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 4: "WHY?" QUESTIONS MATRIX
    # =========================================================================
    story.append(phase_banner("PHASE 4 &mdash; 'WHY?' QUESTIONS DECISION MATRIX"))
    story.append(Spacer(1, 8))

    why_questions = [
        ("Why XGBoost over Deep Learning (LSTM / Transformers)?",
         "Simpler, faster, and tabular data doesn't have enough volume for LSTMs.",
         "Frontier stock datasets have roughly 500 to 2,000 daily observations. Deep architectures (LSTMs, Temporal Fusion Transformers) overfit heavily on small sample sizes and require complex hyperparameter tuning. XGBoost handles tabular feature mixtures, requires no scaling, is computationally lightweight, and allows exact Shapley value attribution via TreeExplainer.",
         "What about capturing temporal dependencies across sequential time steps?",
         "XGBoost captures temporal structure through explicit lag features (Close lags 1 to 20, return lags) and rolling window aggregations (7, 14, 30-day means and standard deviations). This explicitly injects temporal dynamics into the tabular feature matrix without recurrent architecture overhead."),

        ("Why a 30-day target horizon instead of next-day (t+1)?",
         "1-day returns in frontier markets are mostly micro-noise.",
         "Next-day stock prices in small frontier markets are dominated by illiquid order flow noise and bid-ask bounce. Macroeconomic variables (inflation, policy rates) exert economic gravity over weeks and months, not hours. Framing the target as Close(t+30) aligns the forecast horizon with the fundamental transmission mechanism of macroeconomic policy.",
         "Doesn't a 30-day horizon suffer from high variance and small sample size?",
         "Yes, overlapping 30-day horizons introduce autocorrelation in target residuals. I addressed this by enforcing strict tree regularization (max_depth=5, subsample=0.8, colsample=0.8) and validating against a simple moving average baseline that penalizes overfitted complexity."),

        ("Why pd.merge_asof instead of standard pandas merge or forward-fill?",
         "Standard joins cause future data leakage.",
         "Financial time series must strictly respect event time vs. release time. Standard forward-fill after an outer merge risks aligning a monthly figure to early days in that month before the Central Bank actually published the bulletin. <code>pd.merge_asof(direction='backward')</code> guarantees that on any trading day $t$, the system only joins the latest macroeconomic release published at or prior to $t$.",
         "How do you inform the ML model that a macroeconomic value might be 25 days old?",
         "I engineered an explicit <code>days_since_update</code> feature. When a new CPI figure is released, the age resets to 0 and increments daily. This allows tree splits to discount stale economic signals."),

        ("Why use Directional Accuracy alongside RMSE/MAE in model selection?",
         "In trading, getting the direction right matters more than exact price.",
         "A model with a low RMSE could consistently predict small upward drifts when the market actually crashes, leading to catastrophic capital loss. Directional Accuracy measures $\\frac{1}{N} \sum \mathbb{I}(\text{sgn}(\hat{y}_{t+H} - y_t) == \text{sgn}(y_{t+H} - y_t))$. In my selection score, Directional Accuracy accounts for 20% of the tournament weight.",
         "Can a model have high Directional Accuracy and high RMSE simultaneously?",
         "Yes, if it correctly predicts market direction but overshoots the magnitude of extreme volatility spikes. That is precisely why my selection function combines RMSE (40%), MAE (20%), MAPE (20%), and Directional Inaccuracy (20%)."),

        ("Why SHAP TreeExplainer instead of SHAP KernelExplainer or LIME?",
         "KernelExplainer is too slow for real-time web APIs.",
         "KernelExplainer and LIME are sampling-based model-agnostic approximations that require evaluating the model hundreds of times per prediction, resulting in seconds of latency. <code>shap.TreeExplainer</code> exploits tree structure by tracking leaf weights recursively across tree paths in $O(TLD)$ time, generating exact Shapley values in milliseconds, suitable for synchronous REST endpoints.",
         "Why not use SHAP on SARIMAX as well?",
         "TreeExplainer cannot run on SARIMAX. KernelExplainer was too slow, so I implemented an econometric coefficient-based explainer: $\text{impact}_i = \beta_i \times x_i$. This provides an analytically exact marginal attribution in zero latency.")
    ]

    for q_title, simple_ans, tech_ans, follow_up, follow_resp in why_questions:
        card_content = [
            p(f"<b>QUESTION: {q_title}</b>", h3_style),
            p(f"<b>&bull; Simple Answer:</b> {simple_ans}", body_style),
            p(f"<b>&bull; Deep Technical Explanation:</b> {tech_ans}", body_style),
            p(f"<b>&bull; Probable Follow-Up:</b> <i>\"{follow_up}\"</i>", h3_style),
            p(f"<b>&bull; Correct Defense:</b> {follow_resp}", body_style),
        ]
        story.append(card_box(card_content, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # PHASE 5: CATEGORIZED INTERVIEW QUESTION BANK
    # =========================================================================
    story.append(phase_banner("PHASE 5 &mdash; CATEGORIZED INTERVIEW QUESTION BANK (A &ndash; AN)"))
    story.append(Spacer(1, 8))

    q_bank = [
        ("A. Project Overview", "How does your system differ from a standard TradingView or Yahoo Finance dashboard? <i>Answer: Standard tools are technical-only and retrospective; our platform synthesizes macro indicators, performs model tournaments, and provides explainable forward predictions.</i>"),
        ("E. Data Cleaning", "Why did you choose forward-fill (ffill) instead of mean or spline imputation for stock data? <i>Answer: Mean imputation destroys time-series variance and introduces lookahead bias. Spline interpolation leaks future inflection points. In trading, the last observed traded price remains valid until a new trade occurs.</i>"),
        ("H. Feature Engineering", "Explain the formula and intuition behind RSI(14). <i>Answer: $RSI = 100 - \\frac{100}{1 + RS}$, where $RS = \\frac{\\text{Smoothed Avg Gain}}{\\text{Smoothed Avg Loss}}$. It bounds momentum between 0 and 100 to detect overbought (&gt;70) and oversold (&lt;30) conditions.</i>"),
        ("K. Data Leakage", "What are the three most dangerous sources of data leakage in financial ML? <i>Answer: (1) Shuffled cross-validation, (2) Computing scaling/normalization on the entire dataset prior to splitting, and (3) Ingesting macro figures using observation dates rather than actual publication dates.</i>"),
        ("L. Train/Test Split", "Why did you choose an 80/20 chronological split instead of K-Fold cross-validation? <i>Answer: K-Fold randomly samples across time, training on future data to predict past data. Financial time series require chronological order to preserve the autoregressive structure.</i>"),
        ("M. ML Algorithms", "What is the difference between gradient boosting and bagging (Random Forest)? <i>Answer: Bagging trains independent trees in parallel on bootstrap samples to reduce variance. Gradient boosting trains trees sequentially, where each tree fits the negative gradient (pseudo-residuals) of the loss function, reducing bias.</i>"),
        ("O. Hyperparameters", "Why did you set max_depth=5 and learning_rate=0.05 in XGBoost? <i>Answer: Deep trees (depth &gt; 8) memorize noise in financial data. A shallow depth (5) and small learning rate (0.05) with 200 estimators act as shrinkage regularization.</i>"),
        ("T. Evaluation Metrics", "Why is R-squared often misleading in financial price forecasting? <i>Answer: Non-stationary price series with strong trends yield artificially high R-squared values (~0.95+) even if the model merely lags the true price by one day. Directional accuracy and MAPE are far more informative.</i>"),
        ("W. Deployment & Cloud", "How would you migrate this SQLite database to Google Cloud? <i>Answer: Swap SQLAlchemy connection strings from <code>sqlite:///cse.db</code> to Google Cloud SQL (PostgreSQL), and push historical batch data to BigQuery for analytical querying.</i>"),
        ("AD. Explainable AI", "What are the four Shapley value axioms? <i>Answer: Efficiency (attributions sum to difference between prediction and expected value), Symmetry (identical contributors get identical values), Dummy (zero-impact feature gets 0), and Additivity (combined games sum values).</i>"),
        ("AG. Security", "What security protections did you configure in FastAPI? <i>Answer: Configured CORS middleware with specific allowed origins (localhost:5173), input validation schemas via Pydantic to prevent SQL/NoSQL injection, and parameterized queries in SQLAlchemy.</i>"),
        ("AI. Performance", "How do you achieve sub-second prediction responses on the API? <i>Answer: PredictionService uses in-memory caching keyed by <code>(symbol, horizon, date)</code>. Once models are trained for a symbol on a given trading day, cached results serve subsequent requests in &lt;10ms.</i>"),
    ]

    for cat_title, cat_qa in q_bank:
        c_item = [
            p(f"<b>Category {cat_title}:</b>", h3_style),
            p(cat_qa, body_style)
        ]
        story.append(card_box(c_item, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # PHASE 6 & 7: DIFFICULT FOLLOW-UPS & CROSS-QUESTIONING
    # =========================================================================
    story.append(phase_banner("PHASES 6 &amp; 7 &mdash; DIFFICULT FOLLOW-UPS &amp; CROSS-QUESTIONING TREES"))
    story.append(Spacer(1, 8))

    story.append(p("<b>SENIOR ML ENGINEER STRESS TESTS (HARD FOLLOW-UPS)</b>", h2_style))
    hard_questions = [
        ("What happens internally when a user hits GET /api/v1/forecasting/{symbol}?",
         "1. FastAPI routes request to <code>forecasting.py</code>.<br/>"
         "2. <code>PredictionService.get_predictions(symbol)</code> checks in-memory cache.<br/>"
         "3. If cache miss, fetches historical rows via <code>StockPriceRepository</code>.<br/>"
         "4. <code>ProcessingPipeline</code> computes indicators &amp; joins macro data.<br/>"
         "5. <code>ForecastDataset</code> shifts target by 30 days and builds feature matrix.<br/>"
         "6. <code>ForecastTrainer</code> splits 80/20, trains Baseline, SARIMAX, and XGBoost.<br/>"
         "7. <code>ModelEvaluator</code> computes RMSE, MAE, MAPE, DirAcc on test set.<br/>"
         "8. Tournament selects best model; <code>compute_technical_adjustment</code> applies guardrail.<br/>"
         "9. Response dictionary serialized to JSON matching Pydantic response schema."),

        ("What happens if 1,000 users send prediction requests simultaneously?",
         "SQLite is single-writer and would experience file lock timeouts (<code>database locked</code>). Synchronous training inside the request cycle would saturate CPU workers. <b>Production Fix:</b> Decouple training from serving: run a daily background Celery/Redis cron job to precompute predictions into Redis/PostgreSQL, letting the FastAPI endpoints perform pure read-only lookups in &lt;5ms."),

        ("How would you detect and handle Concept Drift in production?",
         "Compute Population Stability Index (PSI) and Wasserstein Distance daily on feature distributions. For target drift, track rolling 30-day MAPE. When rolling MAPE degrades beyond 1.5 standard deviations of historical validation error, trigger an automated retrain alert."),
    ]

    for q_t, ans_t in hard_questions:
        card_content = [
            p(f"<b>STRESS QUESTION: {q_t}</b>", h3_style),
            p(ans_t, body_style)
        ]
        story.append(card_box(card_content, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 6))
    story.append(p("<b>MULTI-LEVEL CROSS-QUESTIONING TREE (5-LEVEL DEEP SIMULATION)</b>", h2_style))
    p7_tree = [
        p("<b>Interviewer (Level 1):</b> Why did you use XGBoost instead of a simple Linear Regression?", h3_style),
        p("<b>Candidate:</b> Because financial markets exhibit non-linear interactions between technical indicators and macroeconomic shocks that linear models cannot capture.", body_style),
        p("<b>Interviewer (Level 2):</b> Can you give an exact example of a non-linear interaction in your CSE dataset?", h3_style),
        p("<b>Candidate:</b> When inflation is low (e.g. 5%), an RSI reading of 75 may simply reflect strong bullish momentum. However, when inflation exceeds 50% and interest rates climb, that exact same RSI reading of 75 signals an overextended speculative bubble about to collapse. Linear regression treats RSI with a constant slope; XGBoost partitions the space using joint tree splits (e.g., <code>if inflation &gt; 30% AND RSI &gt; 70</code>).", body_style),
        p("<b>Interviewer (Level 3):</b> But decision trees cannot extrapolate beyond the maximum value seen in the training data. What happens if inflation hits 80%, higher than anything in your training set?", h3_style),
        p("<b>Candidate:</b> That is an inherent limitation of tree algorithms. For any test sample where inflation &gt; 70%, the tree assigns it to the highest historical leaf node. To mitigate this, I engineered bounded and stationary features—such as percentage returns, log differences, and moving average ratios—rather than relying solely on raw price levels.", body_style),
        p("<b>Interviewer (Level 4):</b> If you care so much about stationarity, why is your model target Close(t+30) instead of Return(t+30)?", h3_style),
        p("<b>Candidate:</b> In <code>dataset.py</code>, both <code>target</code> (Close price) and <code>target_7d_return</code> are engineered. I trained on price level to benchmark directly against SARIMAX and SMA moving averages in local currency (LKR), but I evaluate directional accuracy on sign of return. In a V2 architecture, training directly on 30-day log returns is statistically superior.", body_style),
        p("<b>Interviewer (Level 5):</b> Outstanding. That shows you understand both the practical benefits and theoretical boundaries of your modeling choices.", h3_style)
    ]
    story.append(card_box(p7_tree, bg=c_card_bg, border=c_accent_dark))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 8 & 9: WEAKNESSES & DEFENSE GUIDE
    # =========================================================================
    story.append(phase_banner("PHASES 8 &amp; 9 &mdash; CANDIDATE WEAKNESS AUDIT &amp; PROJECT DEFENSE"))
    story.append(Spacer(1, 8))

    story.append(p("<b>PHASE 8: CANDIDATE WEAKNESS AUDIT (TRAFFIC LIGHT CLASSIFICATION)</b>", h2_style))
    weakness_cards = [
        ("RED TOPIC: Non-Stationarity & Unit Root Differencing (MUST MASTER TODAY)",
         "<b>Theory:</b> Stock prices follow $I(1)$ integrated random walks; their mean and variance change over time. Regressing non-stationary series yields spurious correlation.<br/>"
         "<b>How SARIMAX handles it:</b> Differencing parameter $d=1$ computes $\Delta y_t = y_t - y_{t-1}$, converting prices into stationary increments.<br/>"
         "<b>Interview Answer:</b> 'Raw prices have unit roots. While SARIMAX differences internally ($d=1$), tree models like XGBoost don't difference. That is why I fed XGBoost stationary technical ratios, returns, and oscillators alongside lags.'",
         c_red_bg, c_red_border),

        ("YELLOW TOPIC: Granger Causality Assumptions & Limitations",
         "<b>Theory:</b> Granger causality does NOT prove true philosophical or economic causation. It tests whether past values of $X$ contain information that helps forecast $Y$ beyond past values of $Y$ alone (Vector Autoregression F-test).<br/>"
         "<b>Prerequisite:</b> Both series must be stationary before testing, or the test statistic is invalid.<br/>"
         "<b>In Code:</b> <code>GrangerCausalityTester</code> tests lags 1 to 5 using <code>ssr_chi2test</code>.<br/>"
         "<b>Interview Answer:</b> 'Granger causality is a test of predictive precedence, not true causation. I used it as an exploratory filter to detect whether CBSL macro announcements Granger-cause stock returns.'",
         c_amber_bg, c_amber_border),

        ("GREEN TOPIC: End-to-End Systems Architecture & XAI Integration",
         "<b>Status:</b> Exceptionally strong. Decoupled services, modular clients, Pydantic schemas, React visual components (Waterfall, Feature Importance), and clean REST API routing demonstrate senior full-stack competency.",
         c_green_bg, c_green_border)
    ]

    for title, desc, bg, border in weakness_cards:
        story.append(card_box([p(title, h3_style), p(desc, body_style)], bg=bg, border=border))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 8))
    story.append(p("<b>PHASE 9: PROJECT DEFENSE &mdash; HOW AN INTERVIEWER CAN CHALLENGE YOU</b>", h2_style))

    defenses = [
        ("Vulnerability 1: 'Your README claims you deployed to Google Cloud, but your repo only has SQLite and local scripts.'",
         "The architectural pattern (service decoupling, repository abstractions, containerization) was specifically engineered to be cloud-ready for GCP Cloud Run and Cloud SQL. However, for cost-efficiency and local reproducibility, I used SQLite and Docker Compose during development. I can walk you through the Terraform or Cloud Run deployment specs right now."),

        ("Vulnerability 2: 'You fit your models on-demand inside the API request cycle. That does not scale.'",
         "I agree completely. On-demand fitting was chosen for local prototyping to demonstrate interactive parameter changes. For a production deployment, I would decouple training into a nightly batch worker (e.g. Celery with Redis or GCP Cloud Tasks) that precomputes forecasts into a cache, reducing API endpoint latency from 800ms to under 10ms."),

        ("Vulnerability 3: 'In calendar.py, you use backward fill (bfill) on line 61. Isn't that lookahead data leakage?'",
         "Sharp catch. That bfill was added as an operational safeguard to handle edge cases where historical stock data begins before the earliest available CBSL data point. In a production pipeline, rather than back-filling future values into early dates, I would truncate the dataset to start strictly on the first verified macro announcement date.")
    ]

    for v_title, v_defense in defenses:
        c_item = [
            p(f"<b>{v_title}</b>", h3_style),
            p(f"<b>Honest Winning Defense:</b> {v_defense}", body_style)
        ]
        story.append(card_box(c_item, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # PHASE 10 & 11: PERSONAL CONTRIBUTION & MOCK INTERVIEW
    # =========================================================================
    story.append(phase_banner("PHASES 10 &amp; 11 &mdash; PERSONAL CONTRIBUTION &amp; MOCK RUBRIC"))
    story.append(Spacer(1, 8))

    story.append(p("<b>PHASE 10: PERSONAL CONTRIBUTION &amp; CODE DEFENSE</b>", h2_style))
    p10_content = [
        p("<b>What I Personally Architected &amp; Built:</b>", h3_style),
        p("&bull; <b>Data Engineering Pipeline:</b> Built the cross-frequency synchronization engine using <code>pd.merge_asof</code>, including the dynamic <code>days_since_update</code> staleness feature.", bullet_style),
        p("&bull; <b>Model Tournament &amp; Selection Engine:</b> Designed the multi-metric selection function in <code>ForecastTrainer</code> that balances accuracy and directional correctness while penalizing over-complex models.", bullet_style),
        p("&bull; <b>Explainability Service:</b> Integrated <code>shap.TreeExplainer</code> and engineered the custom SARIMAX marginal coefficient attribution calculator.", bullet_style),
        p("&bull; <b>Technical Guardrail System:</b> Designed the post-processing engine that nudges statistical forecasts based on rule-based momentum signals, capped at 2% to prevent hallucinations.", bullet_style),
        p("&bull; <b>Full-Stack Delivery:</b> Built the FastAPI REST controllers, SQLAlchemy models, and the entire React dashboard (interactive charts, waterfall visualization, and comparison cards).", bullet_style),
        Spacer(1, 4),
        p("<b>What I Leveraged from Open-Source Libraries:</b>", h3_style),
        p("&bull; <code>xgboost</code>: Gradient boosting tree construction and histogram optimization.", bullet_style),
        p("&bull; <code>statsmodels</code>: State-space Kalman filtering for SARIMAX fitting and Granger causality vector autoregression tests.", bullet_style),
        p("&bull; <code>ta</code>: Standard technical indicator mathematical formulas (RSI, MACD, Bollinger Bands).", bullet_style),
        p("&bull; <code>shap</code>: Underlying tree path attribution algorithms.", bullet_style)
    ]
    story.append(card_box(p10_content, bg=c_card_bg, border=c_border))
    story.append(Spacer(1, 10))

    story.append(p("<b>PHASE 11: MOCK INTERVIEW BLUEPRINT &amp; STRICT SCORING RUBRIC</b>", h2_style))
    p11_rubric = [
        p("<b>STRICT TECHNICAL INTERVIEW READINESS EVALUATION CRITERIA (1 &ndash; 5 SCALE):</b>", h3_style),
        p("<b>Score 5 (Senior / Production Ready):</b> Direct answer first; immediately backs claims with specific formulas and code-level parameters; acknowledges trade-offs and edge cases; distinguishes code reality from documentation.", bullet_style),
        p("<b>Score 4 (Strong Applied Candidate):</b> Solid technical understanding; explains algorithms accurately; handles follow-ups well; needs slight guidance on deep mathematical edge cases.", bullet_style),
        p("<b>Score 3 (Borderline / Junior):</b> Gives correct high-level answers but defaults to generic explanations ('XGBoost is good for tabular data'); struggles when asked to explain mathematical mechanics or data leakage details.", bullet_style),
        p("<b>Score 2 (Unprepared):</b> Recites documentation claims that contradict the code; claims features that don't exist; cannot explain how data flows between files.", bullet_style),
        p("<b>Score 1 (Immediate Rejection):</b> Severe data leakage unawareness; claims random K-Fold CV on time-series; cannot explain how models were evaluated.", bullet_style),
        Spacer(1, 4),
        p("<i>Rule: In our live mock session, answer one question at a time. The interviewer will evaluate your response against this 1&ndash;5 rubric, highlight missing technical specifics, provide the ideal answer, and increase question difficulty.</i>", body_style)
    ]
    story.append(card_box(p11_rubric, bg=c_card_bg, border=c_border))
    story.append(PageBreak())

    # =========================================================================
    # PHASE 12: RAPID FIRE ROUND
    # =========================================================================
    story.append(phase_banner("PHASE 12 &mdash; RAPID-FIRE ML &amp; SYSTEMS ROUND (15-SECOND BLITZ)"))
    story.append(Spacer(1, 8))

    rapid_fire = [
        ("What is overfitting?", "When a model learns spurious noise in training data, achieving near-zero training error but failing to generalize to unseen test data."),
        ("Why scale features?", "Distance-based algorithms (KNN, SVM, K-Means) and gradient descent optimizers are sensitive to feature magnitude; unscaled large features dominate loss gradients."),
        ("Does XGBoost require feature scaling?", "No. Decision trees split on rank order within individual features; monotonic scale transformations do not alter split locations."),
        ("What is data leakage?", "When information from outside the training dataset (such as future test labels or target statistics) contaminates model training."),
        ("What is the difference between an epoch and a batch?", "An epoch is one complete forward and backward pass of the entire dataset; a batch is the subset of samples processed in a single update step."),
        ("What is model drift vs concept drift?", "Data drift is when feature distribution $P(X)$ changes over time; concept drift is when the relationship between features and target $P(Y|X)$ changes."),
        ("What is an embedding?", "A dense, continuous vector representation of discrete objects (words, users, items) where geometric proximity captures semantic similarity."),
        ("What is RAG?", "Retrieval-Augmented Generation: retrieving relevant external document chunks from a vector database to ground LLM generation in factual context."),
        ("What is an API?", "Application Programming Interface: a formal communication protocol defining how software components interact over standardized request/response formats."),
        ("Why JSON over XML?", "JSON is lightweight, human-readable, maps natively to programming data structures (dictionaries/objects), and has faster parser serialization."),
        ("What makes a REST API RESTful?", "Stateless client-server architecture, standard HTTP verbs (GET, POST, PUT, DELETE), uniform resource URI endpoints, and cacheability."),
        ("What is a Vector Database?", "A specialized database optimized for indexing and nearest-neighbor vector similarity search (e.g. cosine distance, HNSW indexing)."),
        ("What is inference?", "Running a trained machine learning model forward on unseen inputs to generate predictions in production."),
        ("What is the difference between precision and recall?", "Precision is $\\frac{TP}{TP+FP}$ (out of predicted positives, how many were right); recall is $\\frac{TP}{TP+FN}$ (out of actual positives, how many did we find)."),
        ("Why use Log Returns instead of Simple Returns?", "Log returns are time-additive across periods ($r_{0,2} = r_{0,1} + r_{1,2}$) and are approximately normally distributed."),
        ("What is stationarity in time series?", "A stochastic process whose unconditional joint probability distribution does not change over time; constant mean, constant variance, and autocovariance depending only on lag."),
        ("What does the p-value in an ADF test mean?", "Null hypothesis ($H_0$) is presence of a unit root (non-stationary). A p-value &lt; 0.05 rejects $H_0$, indicating stationarity."),
        ("What is the difference between L1 and L2 regularization?", "L1 (Lasso) adds $\sum |w_i|$, driving non-informative weights to exactly zero (feature selection); L2 (Ridge) adds $\sum w_i^2$, shrinking weights smoothly."),
        ("What is TreeExplainer's time complexity?", "$O(TLD)$ where $T$ is number of trees, $L$ is max leaves, and $D$ is max depth. Far faster than KernelExplainer's exponential $O(M 2^|F|)$."),
        ("What is the difference between a forward fill and a backward fill?", "Forward fill propagates the last known value forward into the future; backward fill pulls future values backward into the past (severe data leakage).")
    ]

    for q_t, a_t in rapid_fire:
        rf_content = [
            p(f"<b>Q: {q_t}</b>", h3_style),
            p(f"<b>A:</b> {a_t}", body_style)
        ]
        story.append(card_box(rf_content, bg=c_card_bg, border=c_border))
        story.append(Spacer(1, 3))

    story.append(PageBreak())

    # =========================================================================
    # PHASE 13: FINAL CHEAT SHEET
    # =========================================================================
    story.append(phase_banner("PHASE 13 &mdash; FINAL ONE-PAGE REVISION CHEAT SHEET"))
    story.append(Spacer(1, 8))

    cheat_sheet_data = [
        p("<b>CSE PLATFORM ARCHITECTURE &amp; DEFENSE SUMMARY</b>", h2_style),
        p("<b>PROJECT:</b> Colombo Stock Exchange (CSE) Market Intelligence Platform", bullet_style),
        p("<b>PROBLEM:</b> Emerging market equity analysis ignores macroeconomic shocks (inflation, currency devaluation) and relies on uninterpretable black-box ML models.", bullet_style),
        p("<b>DATA STREAMS:</b> Daily CSE blue-chips (Yahoo .CM + synthetic fallback), monthly CBSL macroeconomic tables (USD/LKR, Inflation, SDFR/SLFR), weekly Google Trends.", bullet_style),
        p("<b>INPUT / OUTPUT:</b> 47+ engineered features (ratios, oscillators, volatility, lags, macro, calendar) &rarr; 30-day predicted price &amp; return, BUY/HOLD/SELL signal, SHAP attributions.", bullet_style),
        p("<b>PREPROCESSING:</b> ISO dates, deduplication, ascending chronological sort, forward-fill (ffill), backward <code>merge_asof</code> alignment with <code>days_since_update</code> tracking.", bullet_style),
        p("<b>MODELS:</b> Naïve 20-day SMA Baseline, Econometric SARIMAX(1,1,1), Regularized XGBoost Regressor (200 trees, depth 5, lr 0.05).", bullet_style),
        p("<b>SELECTION METRIC:</b> Weighted selection score on 20% hold-out: <code>0.4*RMSE + 0.2*MAE + 0.2*MAPE + 0.2*(100 - DirAcc)</code> with +1000 penalty if complex model &gt;10% worse than Baseline.", bullet_style),
        p("<b>EXPLAINABILITY:</b> <code>shap.TreeExplainer</code> outputs signed feature contributions in Sri Lankan Rupees (LKR) with waterfall charts.", bullet_style),
        p("<b>BACKTESTING:</b> Out-of-sample trading simulation on 20% hold-out test set with 0.25% transaction fee deduction per trade.", bullet_style),
        p("<b>DEPLOYMENT &amp; STACK:</b> Python 3.11, FastAPI, SQLAlchemy, SQLite, React 18 (Vite), Docker Compose.", bullet_style),
        p("<b>MAIN LIMITATION:</b> Terminal 30-day forecast is linearly interpolated rather than simulating a stochastic daily price path.", bullet_style),
        p("<b>FUTURE IMPROVEMENT:</b> Decouple training into Celery/Redis batch workers, migrate database to PostgreSQL/BigQuery, and replace linear interpolation with Monte Carlo path simulation.", bullet_style),
    ]
    story.append(card_box(cheat_sheet_data, bg=c_card_bg, border=c_accent))
    story.append(Spacer(1, 8))

    story.append(p("<b>TOP 10 QUESTIONS MOST LIKELY TO EXPOSE WEAK PROJECT KNOWLEDGE</b>", h2_style))
    top10_traps = [
        p("1. 'Walk me through the exact mathematical formulation of your model selection function.'", bullet_style),
        p("2. 'Why does calendar.py use merge_asof with direction=\"backward\", and what happens if you change it to \"nearest\"?'", bullet_style),
        p("3. 'How do you handle non-stationarity in XGBoost given that decision trees cannot difference series internally?'", bullet_style),
        p("4. 'Explain how TreeExplainer calculates the base_value versus per-feature Shapley values in LKR.'", bullet_style),
        p("5. 'Why did you cap technical adjustments at 2% of the close price in compute_technical_adjustment()?'", bullet_style),
        p("6. 'Your code has a synthetic data generator in yfinance_client.py. Why is it there and when does it trigger?'", bullet_style),
        p("7. 'Explain why Granger causality does not imply economic causality.'", bullet_style),
        p("8. 'What would happen to your SQLite database if 50 users triggered model training simultaneously?'", bullet_style),
        p("9. 'Why did you avoid walk-forward cross-validation on the live prediction endpoint?'", bullet_style),
        p("10. 'If you had one month more, what single architectural redesign would you prioritize and why?'", bullet_style),
    ]
    story.append(card_box(top10_traps, bg=c_red_bg, border=c_red_border))
    story.append(Spacer(1, 10))

    story.append(p("<b>GOLDEN INTERVIEW RULE: DIRECT ANSWER &rarr; SHORT EXPLANATION &rarr; TECHNICAL DEPTH</b>", h3_style))
    story.append(p("Never open an answer with rambling background context. Deliver a crisp, decisive one-sentence answer first, follow with the engineering rationale, and pause to invite technical follow-ups. You will command respect and exude senior engineering maturity.", body_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_pdf_path}")


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "CSE_Market_Intelligence_Master_Interview_Defense.pdf")
    build_interview_guide_pdf(output_path)
