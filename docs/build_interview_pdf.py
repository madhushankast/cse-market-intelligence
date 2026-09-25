"""
Builds the comprehensive PDF and Markdown interview guide for CSE Market Intelligence Platform.
"""
import os
import sys
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.drawString(54, 11 * 72 - 36, "CSE Market Intelligence Platform — Deep Technical Interview Master Guide")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL — INTERVIEW PREPARATION MATERIAL")
        self.line(54, 48, 8.5 * 72 - 54, 48)
        
        self.restoreState()


def create_pdf(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary = colors.HexColor("#0F172A")    # Slate 900
    accent = colors.HexColor("#1D4ED8")     # Blue 700
    subtext = colors.HexColor("#334155")    # Slate 700
    bg_card = colors.HexColor("#F8FAFC")    # Slate 50
    border_card = colors.HexColor("#E2E8F0")# Slate 200

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary,
        alignment=1, # Center
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=accent,
        alignment=1,
        spaceAfter=30
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    q_title_style = ParagraphStyle(
        'QuestionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=accent,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'AnswerBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=subtext,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'AnswerBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=subtext,
        leftIndent=15,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        alignment=1
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("Colombo Stock Exchange (CSE)<br/>Market Intelligence Platform", title_style))
    story.append(Paragraph("Deep Technical Interview Master Guide & Comprehensive Q&amp;A", subtitle_style))
    story.append(HRFlowable(width="80%", thickness=2, color=accent, spaceBefore=10, spaceAfter=25))
    
    overview_p = Paragraph(
        "<b>Candidate Profile &amp; Project Summary:</b><br/>"
        "A full-stack, cloud-ready financial market analytics and machine learning system integrating "
        "Colombo Stock Exchange (CSE) daily equities data, Central Bank of Sri Lanka (CBSL) macroeconomic indicators, "
        "and Google Trends public sentiment interest into a cross-frequency, leak-free predictive platform.<br/><br/>"
        "<b>Core Architecture:</b> Python &bull; FastAPI &bull; XGBoost &bull; SARIMAX &bull; SHAP XAI &bull; "
        "Pandas (merge_asof) &bull; SQLAlchemy &bull; React 18 (Vite) &bull; Docker &bull; GitHub Actions CI/CD",
        body_style
    )
    
    box_table = Table([[overview_p]], colWidths=[500])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_card),
        ('BOX', (0,0), (-1,-1), 1, border_card),
        ('TOPPADDING', (0,0), (-1,-1), 14),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
    ]))
    story.append(box_table)

    story.append(Spacer(1, 35))

    modules_text = Paragraph(
        "<b>Topics Covered in this Guide:</b><br/>"
        "1. <b>Project Understanding &amp; Data Pipeline</b> (14 Core Questions)<br/>"
        "2. <b>Time Series Theory &amp; Econometrics</b> (17 Core Questions)<br/>"
        "3. <b>XGBoost Machine Learning Mechanics</b> (12 Core Questions)<br/>"
        "4. <b>Granger Causality &amp; Statistical Inference</b> (7 Core Questions)<br/>"
        "5. <b>Explainable AI (SHAP) Interpretation</b> (8 Core Questions)<br/>"
        "6. <b>FastAPI, React &amp; Docker Systems Architecture</b> (12 Core Questions)",
        body_style
    )
    story.append(modules_text)

    story.append(Spacer(1, 70))
    story.append(Paragraph("Authored for Senior Full-Stack &amp; ML Engineering Interview Excellence &bull; 2026", meta_style))
    story.append(PageBreak())

    # ================= CONTENT SECTIONS =================
    
    sections = [
        ("1. Project Understanding & Data Pipeline", [
            ("Explain your CSE Market Intelligence Platform.",
             "The CSE Market Intelligence Platform is an end-to-end financial data engineering, machine learning forecasting, and visualization system. "
             "Unlike traditional market tools that rely solely on historical stock charts, this platform solves the unique challenge of emerging frontier markets "
             "by combining daily equities prices from the Colombo Stock Exchange with monthly macroeconomic indicators from the Central Bank of Sri Lanka (CBSL) "
             "and Google Trends public sentiment interest. It features automated ingestion pipelines, leak-free cross-frequency data alignment, "
             "a tournament of predictive models (Baseline, SARIMAX, XGBoost), SHAP explainable AI attribution, a FastAPI REST service, and a React UI dashboard."),

            ("What problem were you trying to solve?",
             "In frontier economies like Sri Lanka, stock prices are dominated by macroeconomic shocks—such as hyperinflation, sovereign debt restructuring, "
             "interest rate shifts, and severe currency depreciations against the USD. Retail and institutional investors had no unified platform that: "
             "(1) Integrated macroeconomic factors with equity pricing, (2) Solved the severe lag between daily prices and monthly economic reporting without lookahead bias, "
             "and (3) Demystified the 'black-box' nature of machine learning predictions using interpretable feature attributions (SHAP)."),

            ("Why did you choose the Colombo Stock Exchange dataset?",
             "Sri Lanka underwent a historic economic crisis between 2021 and 2024 (inflation exceeded 69%, USD/LKR doubled, policy interest rates reached 15.5%). "
             "This provided an extraordinary real-world testbed to study how intense macroeconomic volatility impacts equity valuation. "
             "Western markets have stable macroeconomic baselines where micro-technical patterns dominate; the CSE, conversely, provided the ideal environment "
             "to demonstrate the power of cross-frequency macroeconomic feature engineering."),

            ("What data did you use?",
             "The platform utilizes three distinct data streams:\n"
             "• Colombo Stock Exchange Equities: Daily OHLCV data for blue-chip tickers (e.g., COMB, JKH, SAMP).\n"
             "• Macroeconomic Data (CBSL): Monthly Colombo Consumer Price Index (Inflation_CCPI), daily/monthly USD/LKR exchange rates, Standing Deposit Facility Rate (SDFR), and Standing Lending Facility Rate (SLFR).\n"
             "• Alternative Sentiment Data: Weekly Google Trends search volume indices for Sri Lankan corporate symbols and economic keywords."),

            ("What were your input features?",
             "Over 40 engineered features across 5 functional categories:\n"
             "• Price Action & Returns: Daily return, log return, high-low range ratio, open-close difference ratio.\n"
             "• Technical Oscillators & Trends: SMA (10, 20, 50), EMA (10, 20, 50), ADX(14), RSI(14), MACD & Signal line, ROC(12), Stochastic (%K, %D), Williams %R.\n"
             "• Volatility & Volume: Bollinger Bands (upper, middle, lower), ATR(14), On-Balance Volume (OBV), Volume 20-day MA, 20-day return volatility.\n"
             "• Autoregressive Lags & Rolling Aggregations: Close lags at t-1, t-3, t-5, t-10, t-20; return lags at t-1, t-5; rolling 7, 14, 30-day price means and volatilities.\n"
             "• Macro & Sentiment: ExchangeRate_USD_LKR, Inflation_CCPI, InterestRate_SDFR, InterestRate_SLFR, trend_score, plus calendar day_of_week and month."),

            ("What was your target variable?",
             "The primary target variable was the future Close price shifted across a defined forward horizon: y[t] = Close[t + H], where H = 30 trading days for monthly outlooks, "
             "and H = 1 or 7 days for short-term forecasts. I also derived target_7d_return = (Close[t+H] - Close[t]) / Close[t] to evaluate percentage returns."),

            ("How did you collect the data?",
             "Through modular, decoupled ingestion clients:\n"
             "• Equities: Ingested via direct CSE REST APIs and Yahoo Finance historical tickers (.LK suffix) via yfinance_client.py.\n"
             "• Macroeconomic: Parsed from official Central Bank of Sri Lanka (CBSL) statistical releases and standardized CSV tables.\n"
             "• Google Trends: Queried via pytrends using Sri Lanka's country code ('LK').\n"
             "All ingestion tasks are coordinated by IngestionService and logged to the job_logs database table."),

            ("How did you clean the financial data?",
             "In DataCleaner, I: (1) Removed duplicate rows on (symbol, date), (2) Standardized date formats to ISO-8601 YYYY-MM-DD, (3) Strictly sorted the time series in ascending order, "
             "and (4) Trimmed initial window warmup rows after computing 50-day moving averages and 30-day rolling statistics so no initial NaNs entered the training matrices."),

            ("How did you handle missing values?",
             "I strictly avoided backward imputation (which leaks future data). Missing macroeconomic values were handled via forward-fill (ffill), "
             "implemented through Pandas merge_asof with backward direction. This guarantees that on trading day t, the model only sees the most recently released CBSL figure. "
             "For XGBoost, its native histogram tree algorithm automatically handles any remaining sparsity by routing NaNs to optimal branch splits."),

            ("How did you handle outliers?",
             "Rather than deleting real market shocks (which represent genuine macroeconomic regime shifts during the 2022 default), I handled outliers by: "
             "(1) Transforming prices into percentage returns and log returns to stabilize variance, (2) Relying on decision-tree-based algorithms (XGBoost), "
             "which split on feature rank order rather than absolute magnitude, making them inherently robust to scale outliers compared to linear regression."),

            ("What features did you engineer?",
             "Key engineered features include: (1) Cross-frequency merge_asof macro alignment, (2) Multi-horizon price lags (t-1 to t-20) capturing momentum persistence, "
             "(3) Rolling volatility windows (7, 20, 30 days) capturing volatility clustering, (4) Intraday volatility ratios: (High - Low) / Low and (Close - Open) / Open, "
             "and (5) Calendar cyclical signals: day_of_week and month to capture Friday profit-taking and quarterly rebalancing."),

            ("What technical indicators did you use?",
             "Implemented via the ta library in IndicatorBuilder:\n"
             "• Trend: SMA(10, 20, 50), EMA(10, 20, 50), ADX(14)\n"
             "• Momentum: RSI(14), MACD & Signal(12, 26, 9), ROC(12), Stochastic Oscillator, Williams %R\n"
             "• Volatility: Bollinger Bands (20, 2), Average True Range (ATR 14), Rolling Return Volatility\n"
             "• Volume: On-Balance Volume (OBV) and Volume 20-day Moving Average."),

            ("Why are technical indicators useful?",
             "Technical indicators extract non-linear dynamics from raw prices: RSI quantifies overbought/oversold extremes; MACD captures moving-average convergence momentum; "
             "Bollinger Bands define statistical dynamic volatility envelopes; ATR measures risk range without directional bias; and OBV validates whether price moves are supported by institutional liquidity."),

            ("How did you avoid data leakage?",
             "Data leakage was prevented through three strict architectural controls:\n"
             "1. Strict Chronological Split: 80% train / 20% test without random shuffling. The test set always exists in the chronological future.\n"
             "2. Point-in-Time Alignment: Used merge_asof backward matching so daily stock prices only join with macroeconomic indicators published on or before that exact trading day.\n"
             "3. No Future Rolling Windows: All rolling metrics (SMA, volatility) use trailing historical windows exclusively; no centered or future-looking windows were allowed.")
        ]),

        ("2. Time Series Theory & Econometrics", [
            ("What is time-series forecasting?",
             "Time-series forecasting is the task of predicting future values of a variable based on its historically observed sequence ordered chronologically over time: "
             "y[t+h] = f(y[t], y[t-1], ..., X[t]). Unlike cross-sectional prediction where observations are assumed independent and identically distributed (i.i.d.), "
             "time series observations exhibit strong temporal dependencies and serial autocorrelation."),

            ("How is time-series data different from normal tabular data?",
             "Tabular data assumes row independence (permuting row order does not change model semantics). "
             "Time-series data has strict chronological ordering: observations at time t depend heavily on t-1 (autocorrelation), distributions change over time (non-stationarity), "
             "and shuffling rows completely destroys the temporal structure and introduces catastrophic lookahead bias."),

            ("Why can't you randomly split time-series data?",
             "Random k-fold splitting shuffles past and future observations together. If day t is in the test set while day t-1 and day t+1 are in the training set, "
             "the model easily 'memorizes' the surrounding context. This leads to artificially perfect training metrics that collapse in production because in the real world, "
             "you can never know tomorrow's price when predicting today."),

            ("What is SARIMAX?",
             "SARIMAX stands for Seasonal AutoRegressive Integrated Moving Average with eXogenous variables. It models: "
             "(p) Autoregression: linear combination of past lagged values; (d) Integration: degree of differencing to achieve stationarity; "
             "(q) Moving Average: linear combination of past forecast error terms; (P, D, Q, s) Seasonal components over period s; and "
             "(X) Exogenous variables: external explanatory series (such as RSI or inflation)."),

            ("What does ARIMA stand for?",
             "ARIMA stands for AutoRegressive (AR), Integrated (I), Moving Average (MA). AR models dependence on past values; I differences the series to eliminate trends; "
             "MA models dependence on lagged residual errors."),

            ("What is seasonality?",
             "Seasonality is a predictable, recurring pattern or fluctuation in a time series occurring at fixed, regular intervals (such as day of week, month of year, "
             "or quarterly reporting cycles). In our dataset, we captured day_of_week and month calendar seasonality."),

            ("What is stationarity?",
             "A time series is strictly stationary if its statistical properties (mean, variance, and autocovariance) are constant over time. "
             "Weak (covariance) stationarity requires: (1) E[y_t] = μ (constant mean), (2) Var(y_t) = σ² (constant variance), (3) Cov(y_t, y_{t-k}) depends only on lag k, not on time t."),

            ("Why is stationarity important?",
             "Most classical statistical time-series models (ARIMA, SARIMAX, linear regressions) assume stationarity. "
             "If a series has a changing mean (trend) or explosive variance, regression coefficients become spurious, t-statistics become invalid, "
             "and predictions quickly diverge into nonsense. Stationarity ensures that relationships learned from the past remain valid in the future."),

            ("What is differencing?",
             "Differencing is the mathematical transformation of subtracting the previous observation from the current observation: Δy_t = y_t - y_{t-1}. "
             "First-order differencing removes linear trends; second-order differencing removes quadratic curves. In finance, percentage returns or log differences "
             "r_t = ln(P_t / P_{t-1}) are standard differencing transformations used to achieve stationarity."),

            ("What is autocorrelation?",
             "Autocorrelation (serial correlation) is the Pearson correlation between a time series and a lagged version of itself: Corr(y_t, y_{t-k}). "
             "It measures the persistence of historical values into future periods. In stock prices, returns typically have low autocorrelation (efficient market hypothesis), "
             "whereas absolute returns or volatilities exhibit high autocorrelation (volatility clustering)."),

            ("What is partial autocorrelation?",
             "Partial Autocorrelation Function (PACF) measures the direct correlation between y_t and y_{t-k} after mathematically filtering out the mutual linear influence "
             "of all intermediate lags (y_{t-1}, y_{t-2}, ..., y_{t-k+1}). In ARIMA modeling, PACF cutoff plots determine the AR order (p), while ACF plots determine the MA order (q)."),

            ("What is an exogenous variable?",
             "An exogenous variable (the 'X' in SARIMAX) is an external explanatory input determined outside the immediate target system whose future or contemporaneous values "
             "aid in predicting the target series (e.g. using USD/LKR exchange rate or RSI to predict stock price), in contrast to endogenous variables which are explained by the model itself."),

            ("Why did you use SARIMAX?",
             "SARIMAX served as a rigorous, interpretable econometric benchmark. Unlike black-box ML, SARIMAX provides formal statistical inference, parameter coefficients, "
             "p-values for exogenous variables, and analytical confidence intervals (forecast ± 1.96 × SE), ensuring our platform evaluates classical econometric theory alongside machine learning."),

            ("What is multi-step forecasting?",
             "Multi-step forecasting is the prediction of values multiple steps into the future (e.g. projecting prices for days t+1, t+2, ..., t+30) rather than just one single step ahead."),

            ("How did you perform multi-step forecasting?",
             "In our platform, we implemented direct multi-horizon target projection: the supervised models fit target Close(t+H) (H=30 days), and the system constructs a trajectory "
             "from the latest actual close to the predicted terminal price, modulated by our Technical Signal Engine. In SARIMAX, multi-step out-of-sample forecasting uses dynamic state-space projection."),

            ("What problems occur with multi-step forecasting?",
             "Two major problems: (1) Error Compounding: in recursive auto-regressive multi-step models, errors made at t+1 feed back into the input for t+2, causing predictions to quickly drift; "
             "(2) Degrading Exogenous Information: predicting 30 steps ahead requires knowing the exogenous features 30 steps ahead. In our architecture, we mitigate this by using direct multi-horizon targets "
             "and forward-filled latest economic indicators."),

            ("How did you evaluate your forecasting models?",
             "In ModelEvaluator, we evaluated all models on a strict 20% chronological holdout set using: RMSE (Root Mean Squared Error), MAE (Mean Absolute Error), "
             "MAPE (Mean Absolute Percentage Error), Directional Accuracy (% of days movement direction matched), and R². We selected the winning model using a composite selection score: "
             "Score = 0.4*RMSE + 0.2*MAE + 0.2*MAPE + 0.2*(100 - Directional Accuracy)."),

            ("Why did you include a Naive Baseline?",
             "In financial time series, complex models often overfit and fail to beat simple persistence rules (e.g. predicting tomorrow's price equals today's price). "
             "A Naive Baseline is an essential scientific control. In our ForecastTrainer, if XGBoost or SARIMAX has an RMSE 10% worse than the baseline, the system penalizes it by +1000 points "
             "to ensure we never deploy an over-parameterized model that underperforms a simple average."),

            ("What is a naive forecasting model?",
             "A naive forecasting model sets the forecast equal to the last observed value: ŷ_{t+h} = y_t (Random Walk assumption), or sets the forecast equal to a rolling historical mean. "
             "It represents zero-complexity persistence."),

            ("When can a simple baseline outperform ML?",
             "A baseline outperforms ML when: (1) The signal-to-noise ratio is extremely low, (2) The market is efficient and prices follow a pure random walk, "
             "(3) Severe regime shifts occur (e.g. sudden geopolitical outbreak) that make historical training patterns obsolete, or (4) When the ML model suffers from overfitting.")
        ]),

        ("3. XGBoost Machine Learning Mechanics", [
            ("Why did you use XGBoost?",
             "XGBoost (Extreme Gradient Boosting) is the gold standard for tabular financial datasets: (1) It captures complex non-linear interactions between macroeconomic rates and technical indicators, "
             "(2) It is invariant to feature monotonic scaling and robust to outliers, (3) It natively handles sparse data and missing values, (4) It trains in milliseconds, "
             "and (5) It integrates seamlessly with TreeSHAP for explainable AI."),

            ("How does XGBoost work?",
             "XGBoost is an ensemble of decision trees trained sequentially. Each new tree fits the negative gradient (pseudo-residuals) of the loss function calculated from all prior trees. "
             "It optimizes a regularized objective function combining a loss term (e.g., Mean Squared Error) and a tree complexity penalty Ω(f_t) = γ*T + 0.5*λ*Σw_j², using exact greedy or histogram split finding."),

            ("XGBoost vs Random Forest?",
             "Random Forest uses Bagging (Bootstrap Aggregation): it trains deep, independent trees in parallel on bootstrap samples and averages them to reduce variance. "
             "XGBoost uses Boosting: it trains shallow trees sequentially where each tree corrects the residual errors of the previous ensemble to reduce bias, with explicit L1/L2 regularization to control variance."),

            ("What is boosting?",
             "Boosting is an ensemble technique where weak base learners (shallow trees) are trained iteratively. Each successive learner focuses on the mistakes, errors, or gradients "
             "produced by the previous learners, combining them into a strong, accurate predictor."),

            ("What is bagging?",
             "Bagging (Bootstrap Aggregating) trains multiple identical base estimators independently on random bootstrap subsets of the training data (sampled with replacement) "
             "and aggregates their outputs (via voting or averaging) to reduce model variance without increasing bias."),

            ("What is a decision tree?",
             "A decision tree is a non-parametric model that recursively partitions the feature space into orthogonal rectangular regions using binary if-then decision rules. "
             "At each node, it selects the feature and threshold that maximizes impurity reduction (e.g., variance reduction for regression)."),

            ("What is overfitting in XGBoost?",
             "Overfitting in XGBoost occurs when trees grow too deep or too numerous, learning the high-frequency idiosyncratic noise and market anomalies of the training window. "
             "The model shows near-zero training error but fails completely on the unseen holdout test set."),

            ("How did you tune XGBoost?",
             "In our codebase (models/xgboost.py), we tuned XGBoost conservatively for tabular financial series: n_estimators=200, max_depth=5, learning_rate=0.05, "
             "subsample=0.8, colsample_bytree=0.8, and tree_method='hist'. We validated performance strictly on the 20% holdout test set."),

            ("Which hyperparameters did you tune?",
             "• n_estimators: Total number of boosting rounds.\n"
             "• max_depth: Maximum depth of each decision tree.\n"
             "• learning_rate (eta): Step-size shrinkage applied to new tree leaf weights.\n"
             "• subsample: Fraction of training rows randomly sampled per boosting iteration.\n"
             "• colsample_bytree: Subsample ratio of columns when constructing each tree."),

            ("What is learning rate?",
             "Learning rate (eta) is a shrinkage factor (e.g. 0.05) multiplied by the leaf weights of each newly added tree. It slows down learning, requiring more trees, "
             "but prevents any single tree from dominating the ensemble and drastically reduces overfitting."),

            ("What is number of estimators?",
             "Number of estimators (n_estimators = 200) is the total count of sequential decision trees built during boosting. "
             "Too few trees leads to underfitting; too many trees can lead to overfitting unless countered by early stopping and small learning rates."),

            ("What is max depth?",
             "Max depth (max_depth = 5) limits the maximum number of levels allowed in each decision tree. Setting max_depth=5 allows up to 2^5 = 32 leaf nodes, "
             "enabling the model to capture up to 5-way feature interactions (e.g. Inflation + USD/LKR + RSI + SMA + Volume) while strictly preventing runaway tree memorization.")
        ]),

        ("4. Granger Causality & Statistical Inference", [
            ("What is Granger causality?",
             "Granger causality is an econometric hypothesis test developed by Clive Granger to determine whether one time series X contains statistically significant information "
             "that is useful in forecasting another time series Y, beyond the information already contained in the historical past of Y itself."),

            ("How does Granger causality work?",
             "It compares two Vector AutoRegressive (VAR) linear regressions:\n"
             "1. Restricted Model: Y_t = α + Σ β_i * Y_{t-i} + ε_t\n"
             "2. Unrestricted Model: Y_t = α + Σ β_i * Y_{t-i} + Σ γ_j * X_{t-j} + u_t\n"
             "Using an F-test or Chi-square test (ssr_chi2test), it tests the null hypothesis that all coefficients γ_j = 0. If the p-value < 0.05, we reject the null hypothesis and state that X Granger-causes Y."),

            ("What does it mean if X Granger-causes Y?",
             "It means that past values of X statistically improve the prediction of future values of Y compared to relying on past values of Y alone. "
             "It establishes temporal precedence and incremental forecasting power."),

            ("Does Granger causality prove actual causation?",
             "No! Correlation does not imply causation, and Granger causality only proves temporal precedence in linear forecasting. "
             "It cannot prove physical or economic cause and effect. A classic counterexample: roosters crowing Granger-causes sunrise because the crowing precedes the sunrise, "
             "even though the rooster does not cause the sun to rise."),

            ("Why did you use Granger causality in your project?",
             "In causality.py, we used Granger causality to scientifically test whether macroeconomic indicators (such as USD/LKR exchange rate shifts or CBSL inflation updates) "
             "and Google Trends search interest statistically lead Colombo Stock Exchange returns, validating our feature selection rather than blindly assuming economic features help."),

            ("What is a lead-lag relationship?",
             "A lead-lag relationship occurs when changes in one series (the leading indicator, e.g. currency devaluation or central bank rate hike) consistently precede "
             "and predict corresponding changes in another series (the lagging indicator, e.g. banking stock prices) across an observed time lag (e.g., lag = 2 days)."),

            ("How is correlation different from Granger causality?",
             "• Correlation measures contemporaneous linear association at time t: Corr(X_t, Y_t). It is completely symmetric: Corr(X, Y) = Corr(Y, X), and does not account for time or direction.\n"
             "• Granger Causality is directional and time-lagged: it tests if X_{t-k} predicts Y_t after controlling for Y_{t-k}. It is asymmetric: X can Granger-cause Y while Y does not Granger-cause X.")
        ]),

        ("5. Explainable AI (SHAP) Interpretation", [
            ("What is SHAP?",
             "SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explain the output of any machine learning model. "
             "Derived from Lloyd Shapley's cooperative game theory (Nobel Prize in Economics), it computes the fair marginal contribution of each input feature to the final prediction."),

            ("Why did you use SHAP?",
             "Financial portfolio managers and traders do not accept black-box predictions. In explainability/explanation_service.py, SHAP breaks the black box "
             "by providing mathematically grounded feature attributions that show exactly which macroeconomic or technical signals drove a stock forecast up or down."),

            ("How does SHAP explain a prediction?",
             "SHAP explains a prediction via an additive feature attribution model: f(x) = φ_0 + Σ φ_i, where φ_0 is the base expected value of the dataset, "
             "and φ_i is the Shapley value (impact) of feature i. If base is 100 LKR and prediction is 112 LKR, SHAP proves that RSI contributed +5 LKR, USD/LKR contributed +9 LKR, and Inflation contributed -2 LKR."),

            ("What is a SHAP value?",
             "A SHAP value φ_i represents the weighted average marginal change in model prediction when feature i is added to all possible subsets of features that do not include i. "
             "It satisfies 4 fundamental axiomatic properties: Efficiency, Symmetry, Dummy (Null player), and Additivity."),

            ("What is the difference between global and local explanations?",
             "• Local Explanation: Explains one single prediction for a specific date or ticker (e.g., 'For COMB on Friday, why did the model forecast a 4% decline?').\n"
             "• Global Explanation: Summarizes overall model behavior across the entire dataset, showing which features are globally most important across all stocks and seasons."),

            ("How would you interpret a SHAP summary plot?",
             "In a SHAP summary (beeswarm) plot: (1) Features are ranked on the y-axis by overall importance; (2) The x-axis shows the SHAP value (impact on model output); "
             "(3) Each dot is a data point; (4) Color indicates feature value (red = high, blue = low). For example, if red dots for USD/LKR lie to the right of zero, "
             "it proves high currency depreciation drove stock price forecasts upward."),

            ("Why is explainability important in financial ML?",
             "Three reasons: (1) Risk & Sanity Checking: ensure the model isn't learning spurious noise or artifacts; (2) Regulatory Compliance: financial regulators require justifiable risk decisions; "
             "(3) Trader Adoption: traders will only execute trades when the model's logic aligns with coherent economic reasoning."),

            ("Can SHAP prove that a feature causes the prediction?",
             "SHAP explains the internal mathematical mechanics of the trained model, NOT causal reality in the world. "
             "It proves that the model relied on feature X to compute prediction Y. If the model learned a spurious historical correlation, SHAP will faithfully explain that spurious reliance.")
        ]),

        ("6. FastAPI, React & Docker Systems Architecture", [
            ("Why did you use FastAPI?",
             "FastAPI is modern, blazing fast, and production-ready: (1) High performance on par with NodeJS and Go via Starlette and Uvicorn; "
             "(2) Automatic request validation and data serialization using Pydantic; (3) Native Python asynchronous (async/await) concurrency; "
             "and (4) Automatic interactive OpenAPI/Swagger documentation generated at /docs."),

            ("What is FastAPI?",
             "FastAPI is an asynchronous, high-performance web framework for building REST APIs with Python 3.8+ based on standard Python type hints and Starlette ASGI."),

            ("Why FastAPI instead of Flask?",
             "• Performance & Async: Flask is traditionally synchronous WSGI; FastAPI is asynchronous ASGI, handling concurrent I/O operations (fetching CSE APIs, database reads) efficiently.\n"
             "• Type Safety & Validation: FastAPI automatically validates incoming request parameters using Pydantic models with clear 422 error messages; Flask requires manual validation.\n"
             "• Auto-Docs: FastAPI generates interactive OpenAPI Swagger docs out of the box."),

            ("How does your React frontend communicate with FastAPI?",
             "Via standard asynchronous HTTP REST requests (using Axios or Fetch API) configured in frontend/src/services/api.js. "
             "The frontend sends GET/POST requests to http://localhost:8000/api/v1/..., and FastAPI validates requests and returns JSON responses. "
             "CORS middleware is enabled in FastAPI to permit browser cross-origin calls."),

            ("What is an API?",
             "An Application Programming Interface (API) is a formal software contract that allows two distinct systems to communicate over defined protocols, data formats, and endpoints without exposing internal implementation."),

            ("What is REST?",
             "REST (Representational State Transfer) is an architectural style for distributed hypermedia systems. "
             "It adheres to 6 constraints: (1) Client-Server separation, (2) Statelessness, (3) Cacheability, (4) Uniform Interface (standard HTTP verbs: GET, POST, PUT, DELETE), "
             "(5) Layered System, and (6) Code on demand."),

            ("What is JSON?",
             "JSON (JavaScript Object Notation) is a lightweight, language-agnostic text-based data interchange format based on key-value pairs and arrays. "
             "It is the universal standard for modern REST APIs."),

            ("Explain the request-response cycle in your application.",
             "1. Client Action: User selects 'COMB' on the React dashboard.\n"
             "2. HTTP Call: React issues a GET /api/v1/forecasting/COMB?horizon=30 request.\n"
             "3. FastAPI Routing & Validation: FastAPI routes to forecasting.py, validating query parameters via Pydantic.\n"
             "4. Service Execution: PredictionService retrieves historical data, verifies cache or executes ForecastTrainer, running XGBoost/SARIMAX inference.\n"
             "5. Explainability: ExplanationService computes SHAP feature attributions.\n"
             "6. JSON Serialization: FastAPI serializes dataclass/dict objects into standard JSON.\n"
             "7. Frontend Render: React parses JSON, updates state, and Chart.js dynamically renders the forecast envelope and SHAP attribution bars."),

            ("Why did you use Docker?",
             "Docker containerizes both the Python backend and React frontend into portable, self-contained images with all runtime dependencies, operating system libraries, "
             "and configurations locked. It guarantees that the application runs identically on my development machine, my teammate's laptop, and production cloud servers."),

            ("What problem does Docker solve?",
             "It completely eliminates the 'it works on my machine' problem caused by operating system differences, missing C-compiler extensions (required for xgboost and statsmodels), "
             "and conflicting Node or Python version dependencies."),

            ("How would you deploy this application?",
             "Following our docs/deployment.md blueprint:\n"
             "• Backend: Containerized using Dockerfile and deployed to Google Cloud Run or Render as an autoscaling serverless container.\n"
             "• Frontend: Built into static HTML/JS/CSS via npm run build and deployed to Cloudflare Pages or Vercel with global edge CDN distribution.\n"
             "• Database: SQLite file storage or seamless migration to managed Cloud SQL (PostgreSQL).\n"
             "• Ingestion CI/CD: Automated daily pipeline executed by GitHub Actions (.github/workflows/daily_ingest.yml) at 18:30 IST on market close weekdays.")
        ])
    ]

    for sec_title, qa_list in sections:
        story.append(Paragraph(sec_title, section_header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=border_card, spaceBefore=4, spaceAfter=10))
        
        for q, a in qa_list:
            q_elem = Paragraph(f"Q: {q}", q_title_style)
            
            # Format bullets if any
            if "\n•" in a or a.startswith("•"):
                parts = a.split("\n")
                ans_elems = [Paragraph(parts[0], body_style)]
                for p in parts[1:]:
                    if p.strip().startswith("•"):
                        ans_elems.append(Paragraph(f"&bull; {p.strip()[1:].strip()}", bullet_style))
                    else:
                        ans_elems.append(Paragraph(p, body_style))
                story.append(KeepTogether([q_elem] + ans_elems + [Spacer(1, 6)]))
            else:
                a_elem = Paragraph(a, body_style)
                story.append(KeepTogether([q_elem, a_elem, Spacer(1, 6)]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_pdf_path}")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf = os.path.join(out_dir, "CSE_Market_Intelligence_Interview_Guide.pdf")
    create_pdf(target_pdf)
