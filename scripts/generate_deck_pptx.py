"""
Generate Minimal, Clean 5-Slide LinkedIn Carousel Presentation Deck (.pptx)
Matches the 4:5 Mobile Portrait Carousel Aspect Ratio (8.5 x 10.625 inches)
Palette: Plain Deep Dark Canvas (#090D16) with High-Impact Minimal Typography
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
COLOR_EMERALD = RGBColor(52, 211, 153) # #34d399 bullish / pivot
COLOR_ROSE = RGBColor(248, 113, 113)   # #f87171 bearish / risk / trap
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
    tb_tag = slide.shapes.add_textbox(Inches(0.7), Inches(0.7), Inches(7.1), Inches(0.35))
    tf_tag = tb_tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_CYAN

    # Title
    tb_t = slide.shapes.add_textbox(Inches(0.7), Inches(1.1), Inches(7.1), Inches(1.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_TITLE
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Desc
    tb_d = slide.shapes.add_textbox(Inches(0.7), Inches(2.35), Inches(7.1), Inches(0.9))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]
    p_d.text = desc
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = COLOR_MUTED


def add_footer(slide, index_str):
    tb = slide.shapes.add_textbox(Inches(0.7), Inches(9.8), Inches(7.1), Inches(0.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "COLOMBO STOCK EXCHANGE (CSE) MLOPS"
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
# SLIDE 1: HOOK & THE PROBLEM
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_bg(s1)
add_header(
    s1,
    "[ 01 / PROBLEM & PIVOT ]",
    "Why Predicting Stock Prices is an Anti-Pattern",
    "Predicting raw price points (P_t+30) creates a delayed echo of yesterday. Real financial ML forecasts stationary forward returns.",
)

# Card 1: The Mistake
make_card(s1, Inches(0.7), Inches(3.6), Inches(7.1), Inches(2.6), COLOR_ROSE)
tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(3.75), Inches(6.7), Inches(2.3))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "[ THE MISTAKE: RAW NOMINAL PRICE ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf1.add_paragraph()
p.text = "P_hat(t+30) ~= P_t"
p.font.name = FONT_TITLE
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf1.add_paragraph()
p.text = "Non-stationary prices trick models into outputting today's price as tomorrow's forecast with synthetic 98% R^2 and zero actual alpha."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: The Fix
make_card(s1, Inches(0.7), Inches(6.5), Inches(7.1), Inches(2.6), COLOR_EMERALD)
tb2 = s1.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(6.7), Inches(2.3))
tf2 = tb2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "[ THE FIX: 30-DAY FORWARD LOG RETURN ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf2.add_paragraph()
p.text = "y_t = ln( P_{t+30} / P_t )"
p.font.name = FONT_TITLE
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2.add_paragraph()
p.text = "Enforces stationarity across all 26 Colombo Stock Exchange equities, forcing models to learn genuine momentum and cyclical turning points."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_footer(s1, "Swipe >")


# ==============================================================================
# SLIDE 2: UNCERTAINTY CONES
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_header(
    s2,
    "[ 02 / UNCERTAINTY CONES ]",
    "Replacing Point Estimates with Risk Envelopes",
    "Markets are probabilistic. We train three Multi-Quantile LightGBM models minimizing Pinball Loss.",
)

cones = [
    ("P10 Floor", "Quantile 0.10", "Downside Value-at-Risk support boundary. Penalizes extreme drawdowns 9x more than upside misses.", COLOR_ROSE),
    ("P50 Median", "Quantile 0.50", "Expected median return trajectory. Minimizes MAE, robust against illiquid price spikes.", COLOR_CYAN),
    ("P90 Ceiling", "Quantile 0.90", "Bullish expansion envelope indicating upper momentum resistance levels.", COLOR_EMERALD),
]
for i, (name, q_val, desc, col) in enumerate(cones):
    top = Inches(3.6 + i * 1.95)
    make_card(s2, Inches(0.7), top, Inches(7.1), Inches(1.7), col)
    tb = s2.shapes.add_textbox(Inches(0.9), top + Inches(0.12), Inches(6.7), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = f"{name}   "
    p.font.name = FONT_TITLE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = col

    r = p.add_run()
    r.text = f"[{q_val}]"
    r.font.name = FONT_MONO
    r.font.size = Pt(11)
    r.font.color.rgb = COLOR_DIM

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(13)
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(6)

add_footer(s2, "Swipe >")


# ==============================================================================
# SLIDE 3: LEAKAGE-FREE VALIDATION
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_bg(s3)
add_header(
    s3,
    "[ 03 / VALIDATION RIGOR ]",
    "Zero Lookahead Leakage: Purged & Embargoed CV",
    "A 30-day forward return target leaks data if standard K-Fold CV is used. We enforce a 30-day purge buffer.",
)

# Diagram Card
make_card(s3, Inches(0.7), Inches(3.6), Inches(7.1), Inches(2.6), COLOR_CYAN)
tb3 = s3.shapes.add_textbox(Inches(0.9), Inches(3.75), Inches(6.7), Inches(2.3))
tf3 = tb3.text_frame
tf3.word_wrap = True
p = tf3.paragraphs[0]
p.text = "[ 5-FOLD EXPANDING TIMELINE WITH EMBARGO ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf3.add_paragraph()
p.text = (
    "Fold 1: [== Train ==] [Purge: 30d] [Test: 60d] [Embargo: 30d]\n"
    "Fold 2: [==== Train ====] [Purge: 30d] [Test: 60d] [Embargo: 30d]\n"
    "Fold 3: [====== Train ======] [Purge: 30d] [Test: 60d] ..."
)
p.font.name = FONT_MONO
p.font.size = Pt(10)
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(10)

# Bottom 2 Cards
make_card(s3, Inches(0.7), Inches(6.5), Inches(3.45), Inches(2.6), COLOR_CYAN)
tb_b1 = s3.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(3.05), Inches(2.3))
tf_b1 = tb_b1.text_frame
tf_b1.word_wrap = True
p = tf_b1.paragraphs[0]
p.text = "30-DAY PURGE"
p.font.name = FONT_MONO
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN
p = tf_b1.add_paragraph()
p.text = "Drops training samples whose 30-day horizon overlaps with test dates."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

make_card(s3, Inches(4.35), Inches(6.5), Inches(3.45), Inches(2.6), COLOR_EMERALD)
tb_b2 = s3.shapes.add_textbox(Inches(4.55), Inches(6.65), Inches(3.05), Inches(2.3))
tf_b2 = tb_b2.text_frame
tf_b2.word_wrap = True
p = tf_b2.paragraphs[0]
p.text = "30-DAY EMBARGO"
p.font.name = FONT_MONO
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD
p = tf_b2.add_paragraph()
p.text = "Blocks post-test auto-correlation spillover into future folds."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_footer(s3, "Swipe >")


# ==============================================================================
# SLIDE 4: DUAL-LAYER EXPLAINABILITY
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_bg(s4)
add_header(
    s4,
    "[ 04 / EXPLAINABLE AI ]",
    "Solving the Black-Box Dilemma",
    "Bridging mathematical Shapley attributions with institutional trader heuristic cards.",
)

# Layer 1
make_card(s4, Inches(0.7), Inches(3.6), Inches(7.1), Inches(2.6), COLOR_PURPLE)
tb4_1 = s4.shapes.add_textbox(Inches(0.9), Inches(3.75), Inches(6.7), Inches(2.3))
tf4_1 = tb4_1.text_frame
tf4_1.word_wrap = True
p = tf4_1.paragraphs[0]
p.text = "[ LAYER 1: MATHEMATICAL TREESHAP ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_PURPLE

p = tf4_1.add_paragraph()
p.text = "Exact Additive Shapley Values"
p.font.name = FONT_TITLE
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf4_1.add_paragraph()
p.text = "Decomposes predicted return into exact basis-point contributions: Parkinson Volatility, RSI momentum, and ASPI relative alpha."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Layer 2
make_card(s4, Inches(0.7), Inches(6.5), Inches(7.1), Inches(2.6), COLOR_CYAN)
tb4_2 = s4.shapes.add_textbox(Inches(0.9), Inches(6.65), Inches(6.7), Inches(2.3))
tf4_2 = tb4_2.text_frame
tf4_2.word_wrap = True
p = tf4_2.paragraphs[0]
p.text = "[ LAYER 2: DOMAIN HEURISTIC ALIGNMENT ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf4_2.add_paragraph()
p.text = "Trader Intuition Validation"
p.font.name = FONT_TITLE
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf4_2.add_paragraph()
p.text = "Cross-verifies setup across Wilder RSI, 20/50 SMA trend, Parkinson volatility, and Volume surge into Supporting, Risk, or Neutral badges."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_footer(s4, "Swipe >")


# ==============================================================================
# SLIDE 5: EMPIRICAL RESULTS & STACK
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_bg(s5)
add_header(
    s5,
    "[ 05 / RESULTS & STACK ]",
    "Empirical Results & Live Architecture",
    "Validated out-of-sample edge deployed on a zero-cost 100% free cloud architecture.",
)

# 3 Stat Cards
stats = [
    ("58.3%", "DIRECTION ACCURACY", "+8.3% over Random Walk", COLOR_CYAN),
    ("79.4%", "EMPIRICAL COVERAGE", "Inside P10-P90 Cone", COLOR_EMERALD),
    ("26+1", "EQUITIES + ASPI", "Automated Daily Sync", COLOR_PURPLE),
]
for i, (val, label, sub, col) in enumerate(stats):
    left = Inches(0.7 + i * 2.45)
    make_card(s5, left, Inches(3.6), Inches(2.2), Inches(2.3), col)
    tb = s5.shapes.add_textbox(left + Inches(0.1), Inches(3.8), Inches(2.0), Inches(1.9))
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
    p2.font.size = Pt(9.5)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(4)

    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = sub
    p3.font.name = FONT_BODY
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = COLOR_DIM
    p3.space_before = Pt(4)

# Cloud Stack Card
make_card(s5, Inches(0.7), Inches(6.2), Inches(7.1), Inches(2.9), COLOR_CYAN)
tb5 = s5.shapes.add_textbox(Inches(0.9), Inches(6.35), Inches(6.7), Inches(2.6))
tf5 = tb5.text_frame
tf5.word_wrap = True

p = tf5.paragraphs[0]
p.text = "[ ZERO-COST PRODUCTION STACK ]"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

stack_lines = [
    ("Frontend Terminal", "React 19 + TypeScript on Vercel Edge"),
    ("Serving REST API", "FastAPI Container on Render"),
    ("Cloud Database", "PostgreSQL 15 on Supabase"),
    ("Post-Market Pipeline", "Automated Cron (15:00 SLST) on GitHub Actions"),
]
for comp, desc in stack_lines:
    p = tf5.add_paragraph()
    p.text = f"• {comp:<20} : {desc}"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_footer(s5, "[05 / 05]")

# Save PPTX
output_path = Path("docs/linkedin_presentation_deck.pptx")
prs.save(str(output_path))
print(f"Minimal LinkedIn Carousel PPTX saved successfully: {output_path.resolve()}")
