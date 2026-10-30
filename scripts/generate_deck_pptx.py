"""
Generate 5-Slide Presentation Deck (.pptx)
Strictly focused on the 5 Core Metrics:
1. The Problem
2. How I Solved It
3. System Architecture
4. Technologies Used
5. Accuracies & Results
Format: 4:5 Mobile Portrait Aspect Ratio (8.5 x 10.625 inches)
Palette: Plain Deep Dark Canvas (#090D16) with Clean High-Contrast Cards
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
COLOR_EMERALD = RGBColor(52, 211, 153) # #34d399 positive / solved
COLOR_ROSE = RGBColor(248, 113, 113)   # #f87171 problem / warning
COLOR_PURPLE = RGBColor(192, 132, 252) # #c084fc metrics / architecture

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
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Desc
    tb_d = slide.shapes.add_textbox(Inches(0.7), Inches(2.25), Inches(7.1), Inches(0.85))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]
    p_d.text = desc
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = COLOR_MUTED


def add_footer(slide, index_str):
    tb = slide.shapes.add_textbox(Inches(0.7), Inches(9.85), Inches(7.1), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "COLOMBO STOCK EXCHANGE (CSE) ML"
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


# ==============================================================================
# SLIDE 1: THE PROBLEM
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_bg(s1)
add_header(
    s1,
    "[ 01 / THE PROBLEM ]",
    "Why Stock AI Models Fail",
    "Most financial machine learning models collapse in real trading due to two critical engineering traps.",
)

# Trap 1 Card
make_card(s1, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.9), COLOR_ROSE)
tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.6))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "TRAP 1: THE COPY-PASTE IDENTITY BUG"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf1.add_paragraph()
p.text = "Predicting Raw Stock Prices (P_t+30)"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf1.add_paragraph()
p.text = "Because raw stock prices change slowly day-to-day, naive AI models simply output yesterday's price as tomorrow's forecast. It shows a fake 98% R² score on paper, but has zero real predictive alpha."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Trap 2 Card
make_card(s1, Inches(0.7), Inches(6.4), Inches(7.1), Inches(2.9), COLOR_ROSE)
tb2 = s1.shapes.add_textbox(Inches(0.9), Inches(6.55), Inches(6.7), Inches(2.6))
tf2 = tb2.text_frame
tf2.word_wrap = True

p = tf2.paragraphs[0]
p.text = "TRAP 2: LOOKAHEAD DATA LEAKAGE"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf2.add_paragraph()
p.text = "Overlapping Future Data in Training Splits"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2.add_paragraph()
p.text = "Standard random train/test splits accidentally let future 30-day stock returns leak into past training sets. The model memorizes future knowledge and fails completely in production."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_footer(s1, "Swipe >")


# ==============================================================================
# SLIDE 2: HOW I SOLVED IT
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_header(
    s2,
    "[ 02 / HOW I SOLVED IT ]",
    "Stationary Targets & Risk Cones",
    "I rebuilt the learning formulation and validation structure to ensure true out-of-sample edge.",
)

solutions = [
    ("1. PREDICTING 30-DAY FORWARD LOG RETURN", "y_t = ln( P_{t+30} / P_t )", "Forces models to predict momentum and trend instead of static price levels, enforcing stationarity across 26 equities.", COLOR_EMERALD),
    ("2. MULTI-QUANTILE RISK ENVELOPES (PINBALL LOSS)", "P10 Downside Floor + P50 Median + P90 Ceiling", "Replaced dangerous single price guesses with probabilistic uncertainty envelopes, giving investors downside protection.", COLOR_CYAN),
    ("3. PURGED & EMBARGOED CROSS-VALIDATION", "30-Day Purge Gap + 30-Day Embargo Buffer", "Guarantees 100% leak-free evaluation by removing overlapping return labels and killing serial correlation.", COLOR_PURPLE),
]

for i, (tag_str, title_str, body_str, col) in enumerate(solutions):
    top = Inches(3.3 + i * 2.05)
    make_card(s2, Inches(0.7), top, Inches(7.1), Inches(1.85), col)
    tb = s2.shapes.add_textbox(Inches(0.9), top + Inches(0.12), Inches(6.7), Inches(1.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = tag_str
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = col

    p2 = tf.add_paragraph()
    p2.text = title_str
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(15.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(4)

    p3 = tf.add_paragraph()
    p3.text = body_str
    p3.font.name = FONT_BODY
    p3.font.size = Pt(12.5)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(5)

add_footer(s2, "Swipe >")


# ==============================================================================
# SLIDE 3: SYSTEM ARCHITECTURE
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_bg(s3)
add_header(
    s3,
    "[ 03 / SYSTEM ARCHITECTURE ]",
    "End-to-End Cloud Architecture",
    "A resilient, production-grade cloud topology designed for automated daily operation.",
)

arch_steps = [
    ("1. DATA INGESTION ENGINE", "Daily Automated CSE Scraper", "Automated cron jobs execute at 15:00 SLST market close, syncing 26 blue chips + ASPI index.", COLOR_CYAN),
    ("2. VECTORIZED LAKEHOUSE", "Apache Parquet Feature Store", "Zero-copy columnar format computing 22 indicators (Parkinson volatility, RSI, MACD, beta) in milliseconds.", COLOR_CYAN),
    ("3. BACKEND SERVING API", "Dockerized FastAPI on Render", "High-speed REST API executing real-time multi-quantile LightGBM inferences and TreeSHAP explainability.", COLOR_EMERALD),
    ("4. DATABASE & FRONTEND", "Supabase PostgreSQL + React 19 on Vercel", "PostgreSQL database with composite PK idempotent upserts, paired with an interactive TradingView terminal.", COLOR_PURPLE),
]

for i, (step_tag, step_title, step_desc, col) in enumerate(arch_steps):
    top = Inches(3.3 + i * 1.55)
    make_card(s3, Inches(0.7), top, Inches(7.1), Inches(1.4), col)
    tb = s3.shapes.add_textbox(Inches(0.9), top + Inches(0.08), Inches(6.7), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = step_tag
    p.font.name = FONT_MONO
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = col

    p2 = tf.add_paragraph()
    p2.text = step_title
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(2)

    p3 = tf.add_paragraph()
    p3.text = step_desc
    p3.font.name = FONT_BODY
    p3.font.size = Pt(11.5)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(3)

add_footer(s3, "Swipe >")


# ==============================================================================
# SLIDE 4: TECH USED
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_bg(s4)
add_header(
    s4,
    "[ 04 / TECHNOLOGIES USED ]",
    "Production Tech Stack",
    "Modern tools and frameworks chosen for speed, scalability, and zero hosting costs.",
)

quads = [
    ("AI & MACHINE LEARNING", COLOR_EMERALD, Inches(0.7), Inches(3.3), [
        ("LightGBM", "Multi-Quantile Pinball loss"),
        ("Scikit-Learn", "Time-series validation"),
        ("TreeSHAP", "Explainable AI attributions"),
        ("NumPy & Pandas", "Vectorized series math"),
    ]),
    ("DATA ENGINEERING", COLOR_CYAN, Inches(4.35), Inches(3.3), [
        ("Apache Parquet", "Columnar zero-copy store"),
        ("DuckDB & PyArrow", "High-speed analytics"),
        ("Technical Indicators", "22 market estimators"),
        ("Automated Cron", "Daily 15:00 SLST ETL"),
    ]),
    ("BACKEND & CLOUD", COLOR_PURPLE, Inches(0.7), Inches(6.3), [
        ("Python FastAPI", "Asynchronous REST API"),
        ("Docker Container", "Isolated deployment"),
        ("Supabase / Postgres", "Database storage"),
        ("GitHub Actions", "CI/CD automation"),
    ]),
    ("FRONTEND & UI", COLOR_ROSE, Inches(4.35), Inches(6.3), [
        ("React 19 & TypeScript", "Modern web app"),
        ("TradingView Charts", "Interactive canvas"),
        ("Vercel Edge", "Global low-latency CDN"),
        ("Pytest", "29-test automated suite"),
    ]),
]

for cat_title, border_col, left, top, items in quads:
    make_card(s4, left, top, Inches(3.45), Inches(2.75), border_col)
    tb = s4.shapes.add_textbox(left + Inches(0.18), top + Inches(0.15), Inches(3.1), Inches(2.45))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = cat_title
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = border_col

    for item_name, item_desc in items:
        p2 = tf.add_paragraph()
        p2.text = f"• {item_name}: {item_desc}"
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11)
        p2.font.color.rgb = COLOR_WHITE
        p2.space_before = Pt(4)

add_footer(s4, "Swipe >")


# ==============================================================================
# SLIDE 5: ACCURACIES & RESULTS
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_bg(s5)
add_header(
    s5,
    "[ 05 / ACCURACIES & RESULTS ]",
    "Empirical Results & Accuracies",
    "Rigorous out-of-sample metrics proving real market edge over random walk baselines.",
)

# 3 Stat Cards
stats = [
    ("58.3%", "DIRECTION ACCURACY", "+8.3% over Random Walk", COLOR_CYAN),
    ("79.4%", "EMPIRICAL COVERAGE", "Inside P10-P90 Risk Cone", COLOR_EMERALD),
    ("26+1", "ASSETS TRACKED", "Equities + ASPI Index", COLOR_PURPLE),
]
for i, (val, label, sub, col) in enumerate(stats):
    left = Inches(0.7 + i * 2.45)
    make_card(s5, left, Inches(3.3), Inches(2.2), Inches(1.9), col)
    tb = s5.shapes.add_textbox(left + Inches(0.1), Inches(3.45), Inches(2.0), Inches(1.6))
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

# Key Takeaway Card
make_card(s5, Inches(0.7), Inches(5.4), Inches(7.1), Inches(1.9), COLOR_EMERALD)
tb5_1 = s5.shapes.add_textbox(Inches(0.9), Inches(5.5), Inches(6.7), Inches(1.7))
tf5_1 = tb5_1.text_frame
tf5_1.word_wrap = True

p = tf5_1.paragraphs[0]
p.text = "KEY ENGINEERING TAKEAWAY"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf5_1.add_paragraph()
p.text = "By replacing naive raw price prediction with stationary 30-day forward returns and purged cross-validation, the model achieves a statistically significant +8.3% directional edge across all 26 CSE blue chips without overfitting."
p.font.name = FONT_BODY
p.font.size = Pt(12)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

# Testing Card
make_card(s5, Inches(0.7), Inches(7.45), Inches(7.1), Inches(1.9), COLOR_CYAN)
tb5_2 = s5.shapes.add_textbox(Inches(0.9), Inches(7.55), Inches(6.7), Inches(1.7))
tf5_2 = tb5_2.text_frame
tf5_2.word_wrap = True

p = tf5_2.paragraphs[0]
p.text = "TESTING & AUDITING"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf5_2.add_paragraph()
p.text = "29 automated Pytest unit tests run in CI/CD pipeline verifying: TreeSHAP exact mathematical additivity, zero lookahead leakage, data pipeline idempotency, and API endpoints."
p.font.name = FONT_BODY
p.font.size = Pt(12)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

add_footer(s5, "[05 / 05]")

# Save PPTX
output_path = Path("docs/linkedin_presentation_deck.pptx")
prs.save(str(output_path))
print(f"5-Metric Clean LinkedIn Carousel PPTX saved successfully: {output_path.resolve()}")
