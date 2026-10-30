"""
Generate Minimal, Clean 5-Slide LinkedIn Carousel Presentation Deck (.pptx)
Matches the 4:5 Mobile Portrait Carousel Aspect Ratio (8.5 x 10.625 inches)
Palette: Plain Deep Dark Canvas (#090D16) with High-Impact Minimal Typography
Focused on: AI / ML / Software Engineering Skills & Concrete Technical Implementation
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
# 4:5 Portrait Mobile Carousel standard in inches (8.5 x 10.625 in)
prs.slide_width = Inches(8.5)
prs.slide_height = Inches(10.625)
blank_layout = prs.slide_layouts[6]

# Plain Dark Design System Palette
COLOR_BG = RGBColor(9, 13, 22)         # #090d16 plain deep dark
COLOR_CARD = RGBColor(17, 23, 34)      # #111722 minimal surface card
COLOR_BORDER = RGBColor(30, 41, 59)    # #1e293b subtle card border
COLOR_WHITE = RGBColor(248, 250, 252)  # #f8fafc title
COLOR_MUTED = RGBColor(148, 163, 184)  # #94a3b8 body
COLOR_DIM = RGBColor(100, 116, 139)    # #64748b sub / footer
COLOR_CYAN = RGBColor(56, 189, 248)    # #38bdf8 brand accent
COLOR_EMERALD = RGBColor(52, 211, 153) # #34d399 bullish / stationarity
COLOR_ROSE = RGBColor(248, 113, 113)   # #f87171 bearish / risk / anti-pattern
COLOR_PURPLE = RGBColor(192, 132, 252) # #c084fc shap / stack

FONT_TITLE = "Trebuchet MS"
FONT_BODY = "Calibri"
FONT_MONO = "Consolas"


def set_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    bg.line.fill.background()
    return bg


def add_header(slide, tag, title, desc):
    # Tag
    tb_tag = slide.shapes.add_textbox(Inches(0.7), Inches(0.65), Inches(7.1), Inches(0.3))
    tf_tag = tb_tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN

    # Title
    tb_t = slide.shapes.add_textbox(Inches(0.7), Inches(0.98), Inches(7.1), Inches(1.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(27)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Desc
    tb_d = slide.shapes.add_textbox(Inches(0.7), Inches(2.25), Inches(7.1), Inches(0.85))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]
    p_d.text = desc
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(13.5)
    p_d.font.color.rgb = COLOR_MUTED


def add_footer(slide, index_str):
    tb = slide.shapes.add_textbox(Inches(0.7), Inches(9.85), Inches(7.1), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "AI / ML SYSTEM ENGINEERING"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_DIM

    run = p.add_run()
    run.text = f"   |   {index_str}"
    run.font.color.rgb = COLOR_CYAN
    run.font.bold = True


def make_card(slide, left, top, width, height, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card


def add_skill_pills(slide, left, top, skills):
    """Draw clean monospaced tech stack pills."""
    tb = slide.shapes.add_textbox(left, top, Inches(7.1), Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TECH STACK:  "
    p.font.name = FONT_MONO
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_DIM

    for s in skills:
        run = p.add_run()
        run.text = f" [{s}] "
        run.font.name = FONT_MONO
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_CYAN


# ==============================================================================
# SLIDE 1: FINANCIAL ML MATHEMATICS
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_bg(s1)
add_header(
    s1,
    "[ 01 / FINANCIAL ML MATHEMATICS ]",
    "Solving Time-Series Non-Stationarity",
    "How I engineered a stationary quantitative learning target, eliminating the identity lag trap that plagues naive financial ML.",
)

# Card 1: Anti-Pattern
make_card(s1, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.7), COLOR_ROSE)
tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.4))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "THE PERSISTENCE ANTI-PATTERN (I(1) UNIT ROOT)"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf1.add_paragraph()
p.text = "Predicting Raw Nominals: P_hat(t+30) ~= P_t"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf1.add_paragraph()
p.text = "MSE optimization on raw price levels creates identity models: the booster simply outputs yesterday's price with synthetic 98% R^2 and zero predictive alpha."
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: Mathematical Formulation
make_card(s1, Inches(0.7), Inches(6.2), Inches(7.1), Inches(2.7), COLOR_EMERALD)
tb2 = s1.shapes.add_textbox(Inches(0.9), Inches(6.35), Inches(6.7), Inches(2.4))
tf2 = tb2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "MY MATHEMATICAL FORMULATION"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf2.add_paragraph()
p.text = "y_t = ln( P_{t+30} / P_t )   [Forward Log Return]"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2.add_paragraph()
p.text = "Induces strict covariance stationarity and scale invariance across 26 CSE blue-chip equities, forcing gradient-boosted trees to isolate genuine momentum and mean-reversion."
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_skill_pills(s1, Inches(0.7), Inches(9.2), ["NumPy", "Pandas", "Statistical Stationarity", "Unit Root I(1)"])
add_footer(s1, "Swipe >")


# ==============================================================================
# SLIDE 2: DATA ENGINEERING & LAKEHOUSE
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_header(
    s2,
    "[ 02 / DATA ENGINEERING & LAKEHOUSE ]",
    "High-Throughput Vectorized Feature Store",
    "Engineered a zero-copy Apache Parquet lakehouse coupled with 22 leak-free microstructure estimators.",
)

# Card 1: Columnar Lakehouse
make_card(s2, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.6), COLOR_CYAN)
tb2_1 = s2.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.3))
tf2_1 = tb2_1.text_frame
tf2_1.word_wrap = True

p = tf2_1.paragraphs[0]
p.text = "COLUMNAR ZERO-COPY SERVING LAYER"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf2_1.add_paragraph()
p.text = "Apache Parquet + PyArrow + DuckDB"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2_1.add_paragraph()
p.text = "Sub-millisecond columnar partition scans for all 26 equities (data/processed/*.parquet), bypassing slow SQL connection latency during real-time inference."
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: Market Dynamics Pipeline
make_card(s2, Inches(0.7), Inches(6.1), Inches(7.1), Inches(2.8), COLOR_CYAN)
tb2_2 = s2.shapes.add_textbox(Inches(0.9), Inches(6.25), Inches(6.7), Inches(2.5))
tf2_2 = tb2_2.text_frame
tf2_2.word_wrap = True

p = tf2_2.paragraphs[0]
p.text = "VECTORIZED MARKET DYNAMICS PIPELINE"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

features = [
    ("Parkinson Volatility", "High-Low dispersion (5x more efficient than close-to-close)"),
    ("Momentum & Trend", "Wilder RSI(14), MACD Histogram, 20/50 SMA Golden Cross"),
    ("Systematic Beta", "ASPI 30-Day relative alpha spread & rolling Pearson correlation"),
]
for f_name, f_desc in features:
    p = tf2_2.add_paragraph()
    p.text = f"• {f_name}: {f_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_skill_pills(s2, Inches(0.7), Inches(9.2), ["Apache Parquet", "PyArrow", "DuckDB", "Vectorized Math", "ETL Pipelines"])
add_footer(s2, "Swipe >")


# ==============================================================================
# SLIDE 3: MLOPS & ALGORITHMIC RIGOR
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_bg(s3)
add_header(
    s3,
    "[ 03 / MLOPS & ALGORITHMIC RIGOR ]",
    "Purged Cross-Validation & Quantile Loss",
    "Preventing overlapping target contamination with purged embargo gaps while optimizing asymmetric Pinball Loss.",
)

# Card 1: Purged & Embargoed CV
make_card(s3, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.5), COLOR_CYAN)
tb3_1 = s3.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.2))
tf3_1 = tb3_1.text_frame
tf3_1.word_wrap = True

p = tf3_1.paragraphs[0]
p.text = "CUSTOM PURGED & EMBARGOED WALK-FORWARD CV"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf3_1.add_paragraph()
p.text = "Standard K-Fold leaks future 30-day returns. I built an expanding 5-fold CV engine with a 30-day purge gap (drops overlapping train labels) and a 30-day embargo buffer (kills serial correlation)."
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(8)

# Card 2: Multi-Quantile LightGBM
make_card(s3, Inches(0.7), Inches(6.0), Inches(7.1), Inches(2.9), COLOR_EMERALD)
tb3_2 = s3.shapes.add_textbox(Inches(0.9), Inches(6.15), Inches(6.7), Inches(2.6))
tf3_2 = tb3_2.text_frame
tf3_2.word_wrap = True

p = tf3_2.paragraphs[0]
p.text = "MULTI-QUANTILE LIGHTGBM (PINBALL LOSS)"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

quantiles = [
    ("P10 Floor (q=0.10)", "Downside Value-at-Risk floor (9x penalty on drawdown misses)"),
    ("P50 Median (q=0.50)", "Robust median expected trajectory (MAE optimization)"),
    ("P90 Ceiling (q=0.90)", "Bullish expansion envelope (90th percentile resistance)"),
]
for q_name, q_desc in quantiles:
    p = tf3_2.add_paragraph()
    p.text = f"• {q_name}: {q_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_skill_pills(s3, Inches(0.7), Inches(9.2), ["LightGBM", "Quantile Regression", "Pinball Loss", "Purged & Embargoed CV", "Scikit-Learn"])
add_footer(s3, "Swipe >")


# ==============================================================================
# SLIDE 4: EXPLAINABLE AI & INTERPRETABILITY
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_bg(s4)
add_header(
    s4,
    "[ 04 / EXPLAINABLE AI & INTERPRETABILITY ]",
    "Dual-Layer Transparent XAI Architecture",
    "Bridging mathematically verified Shapley attribution with domain-driven heuristic validation rules.",
)

# Card 1: TreeSHAP
make_card(s4, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.6), COLOR_PURPLE)
tb4_1 = s4.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.3))
tf4_1 = tb4_1.text_frame
tf4_1.word_wrap = True

p = tf4_1.paragraphs[0]
p.text = "LAYER 1: EXACT TREESHAP ATTRIBUTION"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_PURPLE

p = tf4_1.add_paragraph()
p.text = "y_hat = phi_0 + sum( phi_i )   [Exact Additive Decomp]"
p.font.name = FONT_TITLE
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf4_1.add_paragraph()
p.text = "Calculates exact game-theoretic Shapley values directly across tree ensemble paths, decomposing predicted returns into basis-point impacts with 100% additivity verification in pytest."
p.font.name = FONT_BODY
p.font.size = Pt(12.5)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: Heuristic Validation Engine
make_card(s4, Inches(0.7), Inches(6.1), Inches(7.1), Inches(2.8), COLOR_CYAN)
tb4_2 = s4.shapes.add_textbox(Inches(0.9), Inches(6.25), Inches(6.7), Inches(2.5))
tf4_2 = tb4_2.text_frame
tf4_2.word_wrap = True

p = tf4_2.paragraphs[0]
p.text = "LAYER 2: DOMAIN HEURISTIC VALIDATION ENGINE"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

heuristics = [
    ("SUPPORTING", "Setup confirms forecast (e.g. RSI momentum <70 without exhaustion)"),
    ("REJECTING / RISK", "Warns of counter-trend risk (e.g. elevated Parkinson volatility)"),
    ("NEUTRAL", "Stable baseline alignment (e.g. volume consolidation)"),
]
for h_name, h_desc in heuristics:
    p = tf4_2.add_paragraph()
    p.text = f"• {h_name}: {h_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_skill_pills(s4, Inches(0.7), Inches(9.2), ["TreeSHAP", "Local Feature Attribution", "Rule Engines", "XAI Pytest Additivity"])
add_footer(s4, "Swipe >")


# ==============================================================================
# SLIDE 5: FULL-STACK CLOUD ARCHITECTURE & RESULTS
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_bg(s5)
add_header(
    s5,
    "[ 05 / FULL-STACK CLOUD ARCHITECTURE ]",
    "Production Serving & Empirical Results",
    "Production-grade full-stack financial terminal deployed on a zero-cost automated cloud topology.",
)

# 3 Stat Cards
stats = [
    ("58.3%", "DIRECTION ACCURACY", "+8.3% over Random Walk", COLOR_CYAN),
    ("79.4%", "EMPIRICAL COVERAGE", "Inside P10-P90 Envelope", COLOR_EMERALD),
    ("26+1", "EQUITIES + ASPI", "Automated Daily Sync", COLOR_PURPLE),
]
for i, (val, label, sub, col) in enumerate(stats):
    left = Inches(0.7 + i * 2.45)
    make_card(s5, left, Inches(3.3), Inches(2.2), Inches(2.0), col)
    tb = s5.shapes.add_textbox(left + Inches(0.1), Inches(3.45), Inches(2.0), Inches(1.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = val
    p.font.name = FONT_TITLE
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = col

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = label
    p2.font.name = FONT_MONO
    p2.font.size = Pt(9)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(4)

    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = sub
    p3.font.name = FONT_BODY
    p3.font.size = Pt(9)
    p3.font.color.rgb = COLOR_DIM
    p3.space_before = Pt(4)

# Cloud Stack Card
make_card(s5, Inches(0.7), Inches(5.5), Inches(7.1), Inches(3.4), COLOR_CYAN)
tb5 = s5.shapes.add_textbox(Inches(0.9), Inches(5.65), Inches(6.7), Inches(3.1))
tf5 = tb5.text_frame
tf5.word_wrap = True

p = tf5.paragraphs[0]
p.text = "PRODUCTION CLOUD SERVING STACK"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

stack_items = [
    ("Frontend Terminal", "React 19 + TypeScript + TradingView Lightweight Charts on Vercel CDN"),
    ("Serving REST API", "FastAPI in Docker container with OpenMP multiprocessing on Render"),
    ("Cloud Database", "PostgreSQL 15 on Supabase (Composite PK idempotent daily upserts)"),
    ("MLOps Automation", "GitHub Actions daily cron (15:00 SLST) + 29-test Pytest CI suite"),
]
for item_name, item_desc in stack_items:
    p = tf5.add_paragraph()
    p.text = f"• {item_name}: {item_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_skill_pills(s5, Inches(0.7), Inches(9.2), ["FastAPI", "Docker", "PostgreSQL / Supabase", "React 19 + TypeScript", "GitHub Actions"])
add_footer(s5, "[05 / 05]")

# Save PPTX
output_path = Path("docs/linkedin_presentation_deck.pptx")
prs.save(str(output_path))
print(f"Minimal LinkedIn Carousel PPTX saved successfully: {output_path.resolve()}")
