"""
Generate Minimal, Clean & Simple 5-Slide LinkedIn Carousel Presentation Deck (.pptx)
Matches the 4:5 Mobile Portrait Carousel Aspect Ratio (8.5 x 10.625 inches)
Palette: Plain Deep Dark Canvas (#090D16) with High-Impact Clean Minimal Typography
Tone: Clear, simple, and accessible for everyone (recruiters, engineers, general audience)
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
COLOR_EMERALD = RGBColor(52, 211, 153) # #34d399 positive / solution
COLOR_ROSE = RGBColor(248, 113, 113)   # #f87171 warning / problem
COLOR_PURPLE = RGBColor(192, 132, 252) # #c084fc explainability / metric

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
    p.text = "SKILLS & TECH:  "
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
# SLIDE 1: THE BIG PROBLEM
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_bg(s1)
add_header(
    s1,
    "[ 01 / THE CORE PROBLEM ]",
    "Why Most Stock AI Models Fail",
    "Most beginners make one critical mistake: trying to predict exact stock prices instead of trend and momentum.",
)

# Card 1: The Trap
make_card(s1, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.7), COLOR_ROSE)
tb1 = s1.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.4))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "THE TRAP: PREDICTING RAW PRICES"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ROSE

p = tf1.add_paragraph()
p.text = "The AI Just Copies Yesterday's Price"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf1.add_paragraph()
p.text = "If a stock was Rs. 100 yesterday, the AI predicts Rs. 100 tomorrow. It displays fake 99% accuracy on paper, but gives zero real trading value."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: The Solution
make_card(s1, Inches(0.7), Inches(6.2), Inches(7.1), Inches(2.7), COLOR_EMERALD)
tb2 = s1.shapes.add_textbox(Inches(0.9), Inches(6.35), Inches(6.7), Inches(2.4))
tf2 = tb2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "HOW I SOLVED IT"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf2.add_paragraph()
p.text = "Predicting 30-Day Percentage Return & Direction"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2.add_paragraph()
p.text = "I forced the models to learn whether a stock will grow or fall over the next month, discovering genuine market cycles across 26 top companies."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_skill_pills(s1, Inches(0.7), Inches(9.2), ["Python", "Pandas", "NumPy", "Statistical Modeling"])
add_footer(s1, "Swipe >")


# ==============================================================================
# SLIDE 2: DATA PIPELINE
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_header(
    s2,
    "[ 02 / DATA PIPELINE ]",
    "Automated & Fast Data Pipeline",
    "Good AI requires clean data. I built an end-to-end pipeline that tracks the Colombo Stock Exchange without manual work.",
)

# Card 1: Daily Automation
make_card(s2, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.6), COLOR_CYAN)
tb2_1 = s2.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.3))
tf2_1 = tb2_1.text_frame
tf2_1.word_wrap = True

p = tf2_1.paragraphs[0]
p.text = "DAILY MARKET AUTOMATION"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf2_1.add_paragraph()
p.text = "Syncs Automatically at 3:00 PM Every Weekday"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2_1.add_paragraph()
p.text = "When the Colombo market closes, automated cloud workers fetch closing prices for 26 key companies plus the ASPI index, validate data, and update databases."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: Feature Engine
make_card(s2, Inches(0.7), Inches(6.1), Inches(7.1), Inches(2.7), COLOR_CYAN)
tb2_2 = s2.shapes.add_textbox(Inches(0.9), Inches(6.25), Inches(6.7), Inches(2.4))
tf2_2 = tb2_2.text_frame
tf2_2.word_wrap = True

p = tf2_2.paragraphs[0]
p.text = "FAST FEATURE ENGINE"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf2_2.add_paragraph()
p.text = "22 Market Indicators Calculated in Milliseconds"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf2_2.add_paragraph()
p.text = "Automatically computes price volatility, RSI momentum, moving averages, and market correlations using ultra-fast columnar Parquet storage."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_skill_pills(s2, Inches(0.7), Inches(9.2), ["Automated ETL", "Apache Parquet", "REST APIs", "Data Pipelines"])
add_footer(s2, "Swipe >")


# ==============================================================================
# SLIDE 3: RISK ENVELOPES
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_bg(s3)
add_header(
    s3,
    "[ 03 / MACHINE LEARNING ]",
    "Predicting Risk, Not Just One Number",
    "Nobody can predict the future with 100% certainty. Single price guesses are dangerous, so I built a 3-way risk envelope.",
)

levels = [
    ("DOWNSIDE FLOOR (P10)", "Worst-Case Scenario", "Shows where the stock could fall during bad market conditions so investors protect capital.", COLOR_ROSE),
    ("EXPECTED PATH (P50)", "Most Realistic Outcome", "The realistic expected 30-day trajectory, filtering out daily noise and false spikes.", COLOR_CYAN),
    ("UPSIDE CEILING (P90)", "Best-Case Potential", "Shows the upper resistance level if strong buying momentum continues.", COLOR_EMERALD),
]

for i, (tag_name, title_name, desc_text, col) in enumerate(levels):
    top = Inches(3.3 + i * 1.85)
    make_card(s3, Inches(0.7), top, Inches(7.1), Inches(1.65), col)
    tb = s3.shapes.add_textbox(Inches(0.9), top + Inches(0.12), Inches(6.7), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = tag_name
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = col

    p2 = tf.add_paragraph()
    p2.text = title_name
    p2.font.name = FONT_TITLE
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(3)

    p3 = tf.add_paragraph()
    p3.text = desc_text
    p3.font.name = FONT_BODY
    p3.font.size = Pt(12)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(4)

add_skill_pills(s3, Inches(0.7), Inches(9.2), ["LightGBM", "Quantile AI", "Risk Modeling", "Scikit-Learn"])
add_footer(s3, "Swipe >")


# ==============================================================================
# SLIDE 4: EXPLAINABLE AI
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_bg(s4)
add_header(
    s4,
    "[ 04 / EXPLAINABLE AI ]",
    "Why Did the AI Make This Call?",
    "Most AI models are mysterious 'black boxes'. You cannot trust real money to a black box, so I built full transparency into every prediction.",
)

# Card 1: Feature Impact
make_card(s4, Inches(0.7), Inches(3.3), Inches(7.1), Inches(2.6), COLOR_PURPLE)
tb4_1 = s4.shapes.add_textbox(Inches(0.9), Inches(3.45), Inches(6.7), Inches(2.3))
tf4_1 = tb4_1.text_frame
tf4_1.word_wrap = True

p = tf4_1.paragraphs[0]
p.text = "FEATURE IMPACT BREAKDOWN (SHAP)"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_PURPLE

p = tf4_1.add_paragraph()
p.text = "Every Prediction Explains Its Reasons"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf4_1.add_paragraph()
p.text = "Users see exact factors driving the score: e.g. +2.4% strong momentum, -1.2% high market volatility, and +0.8% sector trend."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

# Card 2: Decision Badges
make_card(s4, Inches(0.7), Inches(6.1), Inches(7.1), Inches(2.7), COLOR_CYAN)
tb4_2 = s4.shapes.add_textbox(Inches(0.9), Inches(6.25), Inches(6.7), Inches(2.4))
tf4_2 = tb4_2.text_frame
tf4_2.word_wrap = True

p = tf4_2.paragraphs[0]
p.text = "HUMAN-READABLE HEALTH BADGES"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

p = tf4_2.add_paragraph()
p.text = "Instant Decision Checklist"
p.font.name = FONT_TITLE
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_WHITE
p.space_before = Pt(6)

p = tf4_2.add_paragraph()
p.text = "Translates complex numbers into clear signals: SUPPORTING (healthy trend), RISK WARNING (overheated price), or NEUTRAL (market consolidation)."
p.font.name = FONT_BODY
p.font.size = Pt(13)
p.font.color.rgb = COLOR_MUTED
p.space_before = Pt(8)

add_skill_pills(s4, Inches(0.7), Inches(9.2), ["SHAP Explainability", "Decision Intelligence", "Transparent AI"])
add_footer(s4, "Swipe >")


# ==============================================================================
# SLIDE 5: FULL-STACK CLOUD ARCHITECTURE
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_bg(s5)
add_header(
    s5,
    "[ 05 / FULL-STACK DEPLOYMENT ]",
    "Built, Tested & Live in the Cloud",
    "Not just a notebook script. A complete, production-grade cloud application running 24/7.",
)

# 3 Stat Cards
stats = [
    ("58.3%", "DIRECTION ACCURACY", "Outperforms 50/50 odds", COLOR_CYAN),
    ("79.4%", "RISK ENVELOPE", "Prices stay within cone", COLOR_EMERALD),
    ("26+1", "COMPANIES & INDEX", "Updated daily on cloud", COLOR_PURPLE),
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
make_card(s5, Inches(0.7), Inches(5.5), Inches(7.1), Inches(3.4), COLOR_CYAN)
tb5 = s5.shapes.add_textbox(Inches(0.9), Inches(5.65), Inches(6.7), Inches(3.1))
tf5 = tb5.text_frame
tf5.word_wrap = True

p = tf5.paragraphs[0]
p.text = "THE COMPLETE SOFTWARE STACK"
p.font.name = FONT_MONO
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_CYAN

stack_items = [
    ("Frontend Dashboard", "React 19 + TypeScript + TradingView interactive charts"),
    ("Backend AI API", "Python FastAPI running inside a Docker container"),
    ("Cloud Database", "PostgreSQL 15 on Supabase with automated backups"),
    ("Cloud Automation", "GitHub Actions daily sync & automated test suite"),
]
for item_name, item_desc in stack_items:
    p = tf5.add_paragraph()
    p.text = f"• {item_name}: {item_desc}"
    p.font.name = FONT_BODY
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(6)

add_skill_pills(s5, Inches(0.7), Inches(9.2), ["React 19", "FastAPI", "Docker", "PostgreSQL", "GitHub Actions CI/CD"])
add_footer(s5, "[05 / 05]")

# Save PPTX
output_path = Path("docs/linkedin_presentation_deck.pptx")
prs.save(str(output_path))
print(f"Simple, Clean LinkedIn Carousel PPTX saved successfully: {output_path.resolve()}")
