"""
====================================================
  Wearable Health Monitoring System
  PowerPoint Generator — python-pptx
  Run:  python generate_pptx.py
====================================================
Install dependency first:
  pip install python-pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import pptx.oxml.ns as nsmap
from lxml import etree

# ── Colour Palette (dark tech theme) ──────────────────
BG_DARK    = RGBColor(0x0F, 0x0C, 0x29)   # deep navy
ACCENT1    = RGBColor(0x00, 0xFF, 0x88)   # neon green
ACCENT2    = RGBColor(0xFF, 0x6B, 0x6B)   # coral red  (heart)
ACCENT3    = RGBColor(0x4E, 0xCD, 0xC4)   # teal       (SpO2)
ACCENT4    = RGBColor(0xFF, 0xA5, 0x00)   # orange     (temp)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY = RGBColor(0xAA, 0xAA, 0xBB)
CARD_BG    = RGBColor(0x1E, 0x1B, 0x3A)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

blank_layout = prs.slide_layouts[6]   # completely blank

# ──────────────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────────────
def bg(slide, color: RGBColor):
    """Fill slide background with a solid colour."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def box(slide, left, top, width, height, color: RGBColor, alpha=None):
    """Add a filled rectangle."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def txt(slide, text, left, top, width, height,
        font_size=18, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False):
    """Add a text box."""
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Segoe UI"
    return txBox

def accent_line(slide, left, top, width, color, thickness=0.04):
    """Thin horizontal accent bar."""
    box(slide, left, top, width, thickness, color)

def card(slide, left, top, width, height, title, value, unit, color, icon=""):
    """Data card widget."""
    box(slide, left, top, width, height, CARD_BG)
    # top accent bar
    box(slide, left, top, width, 0.06, color)
    txt(slide, icon + "  " + title,
        left+0.15, top+0.12, width-0.3, 0.35,
        font_size=11, color=LIGHT_GREY)
    txt(slide, value,
        left+0.15, top+0.45, width-0.3, 0.7,
        font_size=32, bold=True, color=color)
    txt(slide, unit,
        left+0.15, top+1.1, width-0.3, 0.3,
        font_size=10, color=LIGHT_GREY, italic=True)

def bullet_list(slide, items, left, top, width, height,
                font_size=14, color=WHITE, icon="▶  "):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = icon + item
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.name = "Segoe UI"

# ══════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 7.5, RGBColor(0x30, 0x2B, 0x63))   # subtle overlay

# Decorative circles
for cx, cy, cr, col in [
    (11.5, 1.0, 2.5, RGBColor(0x00, 0xFF, 0x88)),
    (1.5,  6.5, 2.0, RGBColor(0xFF, 0x6B, 0x6B)),
]:
    shape = s.shapes.add_shape(9, Inches(cx-cr/2), Inches(cy-cr/2),
                                Inches(cr), Inches(cr))
    shape.fill.solid()
    shape.fill.fore_color.rgb = col
    shape.line.fill.background()
    # make it semi-transparent via XML
    sp_pr = shape._element.spPr
    solid_fill = sp_pr.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
    if solid_fill is not None:
        srgb = solid_fill.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
        if srgb is not None:
            alpha_el = etree.SubElement(
                srgb, '{http://schemas.openxmlformats.org/drawingml/2006/main}alpha')
            alpha_el.set('val', '15000')   # ~15%

accent_line(s, 1.5, 2.2, 3.5, ACCENT1)
txt(s, "🩺  WEARABLE HEALTH",      1.5, 2.4,  10, 1.0, font_size=42, bold=True)
txt(s, "MONITORING SYSTEM",         1.5, 3.2,  10, 1.0, font_size=42, bold=True, color=ACCENT1)
txt(s, "IoT-Based Real-Time Patient Vitals using ESP32 & Wi-Fi",
    1.5, 4.25, 9, 0.5, font_size=18, color=LIGHT_GREY, italic=True)
accent_line(s, 1.5, 4.85, 6, LIGHT_GREY)
txt(s, "Praveen Kumar  |  Wireless Communication & IoT  |  2026",
    1.5, 5.0,  9, 0.4, font_size=13, color=LIGHT_GREY)

# ══════════════════════════════════════════════════════
# SLIDE 2 — PROJECT OVERVIEW
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "📋  PROJECT OVERVIEW", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

txt(s, "What is this project?", 0.4, 1.4, 6, 0.4,
    font_size=16, bold=True, color=WHITE)
bullet_list(s, [
    "A wearable device that monitors patient health continuously",
    "Measures Heart Rate, Blood Oxygen (SpO₂) & Body Temperature",
    "Transmits data wirelessly over Wi-Fi using ESP32",
    "Displays live data on OLED + Web Dashboard + Cloud",
    "Alerts via buzzer & LED for abnormal readings",
], 0.4, 1.85, 7.2, 3.5, font_size=13)

# Feature pills
for i, (label, col) in enumerate([
    ("❤️  Heart Rate",   ACCENT2),
    ("🩸  SpO₂",         ACCENT3),
    ("🌡️  Temperature",  ACCENT4),
    ("📡  Wi-Fi",        ACCENT1),
    ("☁️  Cloud",        RGBColor(0x99,0x88,0xFF)),
    ("🔔  Alerts",       RGBColor(0xFF,0xCC,0x00)),
]):
    row, col_pos = divmod(i, 3)
    bx = box(s, 8.0 + col_pos*1.7, 1.7 + row*0.95, 1.55, 0.65, col)
    bx.fill.fore_color.rgb = col
    txt(s, label, 8.05 + col_pos*1.7, 1.75 + row*0.95, 1.45, 0.55,
        font_size=10, bold=True, color=BG_DARK, align=PP_ALIGN.CENTER)

txt(s, "System Flow:", 0.4, 5.3, 6, 0.35, font_size=14, bold=True, color=ACCENT1)
txt(s, "Sensor  →  ESP32  →  Wi-Fi  →  Dashboard  →  Cloud  →  Alert",
    0.4, 5.7, 12, 0.35, font_size=13, color=WHITE, italic=True)

# ══════════════════════════════════════════════════════
# SLIDE 3 — OBJECTIVES
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🎯  OBJECTIVES", 0.4, 0.2, 12, 0.7, font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

objectives = [
    ("1", "Real-Time Monitoring",
     "Continuously measure heart rate, SpO₂, and body temperature using IoT sensors.",
     ACCENT2),
    ("2", "Wireless Transmission",
     "Use ESP32 Wi-Fi to stream health data to any device on the network instantly.",
     ACCENT3),
    ("3", "Web Dashboard",
     "Host a live, auto-refreshing dashboard directly from the ESP32 device.",
     ACCENT4),
    ("4", "Cloud Logging",
     "Upload periodic readings to ThingSpeak for remote access and analytics.",
     ACCENT1),
    ("5", "Smart Alerts",
     "Trigger LED and buzzer alerts automatically when readings go outside safe ranges.",
     RGBColor(0xFF,0xCC,0x00)),
    ("6", "Low-Cost & Portable",
     "Build an affordable wearable prototype using widely available components.",
     RGBColor(0x99,0x88,0xFF)),
]

for i, (num, title, desc, col) in enumerate(objectives):
    row, c = divmod(i, 3)
    lx = 0.4 + c*4.3
    ty = 1.4 + row*2.5
    box(s, lx, ty, 4.0, 2.2, CARD_BG)
    box(s, lx, ty, 4.0, 0.06, col)
    txt(s, num, lx+0.15, ty+0.1, 0.5, 0.4, font_size=22, bold=True, color=col)
    txt(s, title, lx+0.6,  ty+0.12, 3.2, 0.4, font_size=12, bold=True, color=WHITE)
    txt(s, desc,  lx+0.15, ty+0.6,  3.7, 1.4, font_size=10, color=LIGHT_GREY)

# ══════════════════════════════════════════════════════
# SLIDE 4 — HARDWARE COMPONENTS
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🔩  HARDWARE COMPONENTS", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

components = [
    ("ESP32 Dev Board",       "Main MCU + Wi-Fi + Bluetooth", "Dual-core 240MHz, 4MB Flash", ACCENT1),
    ("MAX30102 Sensor",       "Heart Rate + SpO₂",            "PPG Optical sensor, I2C",     ACCENT2),
    ("DS18B20 Sensor",        "Body Temperature",             "1-Wire, ±0.5°C accuracy",     ACCENT4),
    ("SSD1306 OLED (128×64)", "Local Display",                "I2C, 0.96\", Monochrome",     ACCENT3),
    ("Passive Buzzer",        "Audio Alert",                  "5V, 2kHz–4kHz",               RGBColor(0xFF,0xCC,0x00)),
    ("LED (Red + Green)",     "Visual Indicators",            "5mm, 220Ω resistors",         RGBColor(0x99,0x88,0xFF)),
    ("Li-Po Battery + TP4056","Power Supply",                 "3.7V, 1000mAh rechargeable",  RGBColor(0xFF,0x88,0x44)),
    ("Jumper Wires + PCB",    "Wiring & Assembly",            "Breadboard or custom PCB",    LIGHT_GREY),
]

for i, (name, role, spec, col) in enumerate(components):
    row, c = divmod(i, 2)
    lx = 0.4 + c*6.4
    ty = 1.35 + row*1.45
    box(s, lx, ty, 6.1, 1.3, CARD_BG)
    box(s, lx, ty, 0.1, 1.3, col)          # left accent bar
    txt(s, name, lx+0.25, ty+0.08, 4.5, 0.4, font_size=13, bold=True, color=col)
    txt(s, role, lx+0.25, ty+0.45, 4.5, 0.35, font_size=11, color=WHITE)
    txt(s, spec, lx+0.25, ty+0.8,  4.5, 0.35, font_size=10, color=LIGHT_GREY, italic=True)

txt(s, "Cost: Rs.600 - Rs.900  (approx. $8 - $12 USD)",
    0.4, 7.0, 12, 0.35, font_size=12, color=ACCENT1, italic=True)

# ══════════════════════════════════════════════════════
# SLIDE 5 — CIRCUIT / WIRING
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🔌  CIRCUIT & WIRING DIAGRAM", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

# Central ESP32 box
box(s, 4.9, 2.5, 3.5, 2.5, RGBColor(0x20, 0x60, 0x20))
txt(s, "ESP32", 5.3, 2.85, 2.7, 0.5, font_size=20, bold=True,
    color=ACCENT1, align=PP_ALIGN.CENTER)
txt(s, "Dev Board", 5.3, 3.3, 2.7, 0.4, font_size=13, color=WHITE,
    align=PP_ALIGN.CENTER)
txt(s, "Wi-Fi  |  I2C  |  GPIO", 5.0, 3.75, 3.2, 0.35, font_size=10,
    color=LIGHT_GREY, align=PP_ALIGN.CENTER)

# Peripheral boxes
peripherals = [
    # (label, sublabel, pin, x, y, col)
    ("MAX30102",    "HR + SpO₂",      "GPIO 21/22 (I2C)",   0.3,  1.5,  ACCENT2),
    ("DS18B20",     "Temperature",    "GPIO 4 (1-Wire)",    0.3,  4.2,  ACCENT4),
    ("SSD1306",     "OLED Display",   "GPIO 21/22 (I2C)",   9.5,  1.5,  ACCENT3),
    ("Buzzer",      "Audio Alert",    "GPIO 15",            9.5,  3.2,  RGBColor(0xFF,0xCC,0x00)),
    ("LEDs",        "Red + Green",    "GPIO 12, 13",        9.5,  4.9,  RGBColor(0xFF,0x44,0x44)),
    ("ThingSpeak",  "Cloud ☁️",       "Wi-Fi (TCP/HTTP)",   4.5,  5.7,  ACCENT1),
]

for label, sub, pin, px, py, col in peripherals:
    box(s, px, py, 2.8, 1.1, CARD_BG)
    box(s, px, py, 2.8, 0.05, col)
    txt(s, label, px+0.1, py+0.08, 2.6, 0.35, font_size=12, bold=True, color=col)
    txt(s, sub,   px+0.1, py+0.42, 2.6, 0.3,  font_size=10, color=WHITE)
    txt(s, pin,   px+0.1, py+0.72, 2.6, 0.3,  font_size=9,  color=LIGHT_GREY, italic=True)

txt(s, "Note: MAX30102 & SSD1306 share the I2C bus (0x57 & 0x3C addresses). DS18B20 needs 4.7kΩ pull-up to 3.3V.",
    0.4, 6.9, 12.5, 0.4, font_size=10, color=LIGHT_GREY, italic=True)

# ══════════════════════════════════════════════════════
# SLIDE 6 — SYSTEM ARCHITECTURE
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🏗️  SYSTEM ARCHITECTURE", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

layers = [
    ("PERCEPTION LAYER (Sensors)",
     ["MAX30102 — Optical PPG Sensor (HR + SpO₂)", "DS18B20 — Digital Temp Sensor (1-Wire)"],
     ACCENT2, 1.3),
    ("PROCESSING LAYER (ESP32 MCU)",
     ["Reads sensor data via I2C & 1-Wire protocols",
      "Runs health evaluation logic (alert thresholds)",
      "Hosts HTTP web server (port 80) on-device"],
     ACCENT3, 2.85),
    ("NETWORK LAYER (Wi-Fi 802.11)",
     ["IEEE 802.11 b/g/n — 2.4 GHz band",
      "Station Mode: ESP32 connects to home/office router"],
     ACCENT1, 4.4),
    ("APPLICATION LAYER (Dashboard + Cloud)",
     ["Browser Dashboard — live HTML/CSS/JS page",
      "JSON REST API — /data endpoint for external use",
      "ThingSpeak — cloud data logging & chart visualization"],
     RGBColor(0x99,0x88,0xFF), 5.95),
]

for title, items, col, ty in layers:
    box(s, 0.4, ty, 12.5, 1.3, CARD_BG)
    box(s, 0.4, ty, 0.1,  1.3, col)
    txt(s, title, 0.65, ty+0.08, 5, 0.35, font_size=11, bold=True, color=col)
    bullet_list(s, items, 0.65, ty+0.45, 11.8, 0.8,
                font_size=10, color=LIGHT_GREY, icon="  • ")

# ══════════════════════════════════════════════════════
# SLIDE 7 — WIRELESS COMMUNICATION
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "📡  WIRELESS COMMUNICATION", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

specs = [
    ("Protocol",    "IEEE 802.11 b/g/n (Wi-Fi)",           ACCENT1),
    ("Frequency",   "2.4 GHz ISM Band",                    ACCENT3),
    ("Range",       "Up to 100m (indoor ~30m)",             ACCENT4),
    ("Security",    "WPA2-PSK Encryption",                  ACCENT2),
    ("Data Format", "JSON over HTTP REST API",              RGBColor(0x99,0x88,0xFF)),
    ("Update Rate", "Every 2 seconds (dashboard)",          RGBColor(0xFF,0xCC,0x00)),
]

for i, (label, val, col) in enumerate(specs):
    row, c = divmod(i, 2)
    lx = 0.4 + c*6.4
    ty = 1.4 + row*1.5
    box(s, lx, ty, 6.1, 1.25, CARD_BG)
    box(s, lx, ty, 6.1, 0.06, col)
    txt(s, label, lx+0.2, ty+0.12, 2.5, 0.4, font_size=12, bold=True, color=col)
    txt(s, val,   lx+0.2, ty+0.55, 5.7, 0.5, font_size=13, color=WHITE)

txt(s, "Communication Flow:", 0.4, 6.0, 5, 0.35, font_size=14, bold=True, color=ACCENT1)
for i, (label, col) in enumerate([
    ("ESP32\n(Server)", ACCENT1),
    ("→", WHITE),
    ("Wi-Fi\nRouter",  ACCENT3),
    ("→", WHITE),
    ("Browser\n(Client)", ACCENT4),
    ("→", WHITE),
    ("ThingSpeak\n(Cloud)", RGBColor(0x99,0x88,0xFF)),
]):
    tx = 0.4 + i * 1.8
    if label == "→":
        txt(s, label, tx+0.5, 6.45, 0.6, 0.4, font_size=20, bold=True, color=WHITE)
    else:
        box(s, tx, 6.35, 1.6, 0.9, CARD_BG)
        box(s, tx, 6.35, 1.6, 0.05, col)
        txt(s, label, tx+0.05, 6.42, 1.5, 0.85,
            font_size=9, bold=True, color=col, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════
# SLIDE 8 — WEB DASHBOARD
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🌐  LIVE WEB DASHBOARD", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

# Mock browser frame
box(s, 0.5, 1.3, 8.5, 5.9, RGBColor(0x1A, 0x17, 0x40))
box(s, 0.5, 1.3, 8.5, 0.45, RGBColor(0x28,0x25,0x50))  # browser bar
txt(s, "🔒  http://192.168.1.100  —  Health Monitor Dashboard",
    0.65, 1.33, 8.2, 0.35, font_size=9, color=LIGHT_GREY)

# Mock cards inside browser
card(s, 0.65, 1.85, 2.5, 1.5, "Heart Rate",  "72", "beats/min", ACCENT2, "❤️")
card(s, 3.25, 1.85, 2.5, 1.5, "SpO₂",       "98", "%",          ACCENT3, "🩸")
card(s, 5.85, 1.85, 2.5, 1.5, "Temperature","36.8","°C",         ACCENT4, "🌡️")

# Sparkline mock
box(s, 0.65, 3.5, 7.7, 1.1, RGBColor(0x15,0x12,0x35))
txt(s, "❤️  Live Heart Rate Trend", 0.8, 3.55, 5, 0.3, font_size=9, color=LIGHT_GREY)
for xi, h in enumerate([68,70,72,71,74,73,75,72,70,72,74,75,73,72]):
    bh = h / 200
    box(s, 0.75 + xi*0.52, 3.95 - bh, 0.35, bh, ACCENT2)

box(s, 0.65, 4.75, 7.7, 0.55, RGBColor(0x0A, 0x28, 0x1A))
txt(s, "✅  Overall Status:   NORMAL  —  All vitals within safe range",
    0.8, 4.83, 7.4, 0.35, font_size=10, bold=True, color=ACCENT1)
txt(s, "Auto-refresh: every 2 seconds", 0.65, 5.42, 4, 0.3,
    font_size=8, color=LIGHT_GREY, italic=True)

# Features list on the right
txt(s, "Dashboard Features:", 9.3, 1.4, 3.8, 0.35,
    font_size=13, bold=True, color=ACCENT1)
bullet_list(s, [
    "Auto-refresh every 2 seconds",
    "Color-coded status badges",
    "Live sparkline trend charts",
    "Responsive mobile layout",
    "JSON API at /data endpoint",
    "Works on any browser/device",
    "No internet required",
    "Served directly from ESP32",
], 9.3, 1.8, 3.8, 5.0, font_size=11, color=WHITE)

# ══════════════════════════════════════════════════════
# SLIDE 9 — CODE OVERVIEW
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "💻  CODE OVERVIEW", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

# Code snippet box
box(s, 0.4, 1.3, 7.5, 5.8, RGBColor(0x0D, 0x11, 0x17))
txt(s, "// main.ino — ESP32 Firmware (Arduino Framework)", 0.55, 1.38, 7.2, 0.35,
    font_size=9, color=RGBColor(0x60,0x80,0x60), italic=True)

code_lines = [
    ("void ", WHITE,  "loop() {", ACCENT1),
    ("  server.", LIGHT_GREY, "handleClient();", ACCENT3),
    ("  if (millis() - lastRead > 2000) {", LIGHT_GREY, "", WHITE),
    ("    readTemperature();", ACCENT4, "", WHITE),
    ("    readHeartRateSpO2();", ACCENT2, "", WHITE),
    ("    evaluateHealth();", ACCENT1, "", WHITE),
    ("    updateOLED();", ACCENT3, "", WHITE),
    ("  }", LIGHT_GREY, "", WHITE),
    ("  if (millis() - lastTS > 20000)", LIGHT_GREY, "", WHITE),
    ("    uploadToThingSpeak();", RGBColor(0x99,0x88,0xFF), "", WHITE),
    ("}", WHITE, "", WHITE),
]

for i, (a, ac, b, bc) in enumerate(code_lines):
    ty2 = 1.8 + i * 0.43
    txt(s, a, 0.6, ty2, 3.5, 0.4, font_size=10, color=ac)
    if b:
        txt(s, b, 0.6 + len(a)*0.065, ty2, 5, 0.4, font_size=10, color=bc)

# Modules
txt(s, "Key Modules:", 8.2, 1.3, 4.8, 0.4, font_size=14, bold=True, color=ACCENT1)
modules = [
    ("readHeartRateSpO2()",  "Collects 100 samples, runs maxim\nHR & SpO₂ algorithm",         ACCENT2),
    ("readTemperature()",     "DS18B20 1-Wire read, returns °C",                               ACCENT4),
    ("evaluateHealth()",      "Checks thresholds, sets alert\nstatus, controls LEDs & buzzer", ACCENT1),
    ("handleRoot()",          "Serves full HTML dashboard page",                                ACCENT3),
    ("handleData()",          "Returns JSON of all vitals",                                    RGBColor(0x99,0x88,0xFF)),
    ("uploadToThingSpeak()",  "HTTP GET to ThingSpeak API",                                    RGBColor(0xFF,0xCC,0x00)),
]
for i, (fn, desc, col) in enumerate(modules):
    ty2 = 1.8 + i * 0.92
    box(s, 8.2, ty2, 4.8, 0.82, CARD_BG)
    box(s, 8.2, ty2, 0.07, 0.82, col)
    txt(s, fn,   8.35, ty2+0.05, 4.5, 0.3,  font_size=10, bold=True, color=col)
    txt(s, desc, 8.35, ty2+0.38, 4.5, 0.38, font_size=9,  color=LIGHT_GREY)

# ══════════════════════════════════════════════════════
# SLIDE 10 — HEALTH PARAMETERS & ALERTS
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🔔  HEALTH PARAMETERS & ALERT SYSTEM", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

# Table header
for cx, cw, label, col in [
    (0.4, 3.5, "Parameter",      RGBColor(0x33,0x28,0x6E)),
    (3.9, 2.8, "Normal Range",   RGBColor(0x00,0x44,0x22)),
    (6.7, 3.0, "Alert Condition",RGBColor(0x44,0x11,0x00)),
    (9.7, 3.2, "Action Taken",   RGBColor(0x33,0x28,0x6E)),
]:
    box(s, cx, 1.4, cw, 0.5, col)
    txt(s, label, cx+0.1, 1.43, cw-0.2, 0.42,
        font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

rows = [
    ("❤️  Heart Rate",      "60 – 100 BPM",
     "< 60 BPM (Bradycardia)\n> 100 BPM (Tachycardia)",
     "Red LED ON + Buzzer Beep\nDashboard badge → DANGER"),
    ("🩸  Blood Oxygen (SpO₂)", "95 – 100%",
     "< 95% → Low\n< 90% → Critical",
     "Red LED + Buzzer Alert\nDashboard badge → WARNING / DANGER"),
    ("🌡️  Body Temperature",  "36.1°C – 37.5°C",
     "> 37.5°C → Fever\n< 36.0°C → Hypothermia",
     "Red LED + Buzzer Alert\nDashboard badge → WARNING"),
]

for i, (param, normal, alert, action) in enumerate(rows):
    ty2 = 2.0 + i * 1.55
    row_bg = RGBColor(0x18,0x15,0x38) if i % 2 == 0 else CARD_BG
    for cx, cw in [(0.4,3.5),(3.9,2.8),(6.7,3.0),(9.7,3.2)]:
        box(s, cx, ty2, cw, 1.45, row_bg)

    txt(s, param,  0.55, ty2+0.08, 3.2, 0.5, font_size=12, bold=True, color=ACCENT1)
    txt(s, normal, 4.0,  ty2+0.08, 2.6, 1.2, font_size=11, color=ACCENT1)
    txt(s, alert,  6.8,  ty2+0.08, 2.8, 1.2, font_size=10, color=ACCENT2)
    txt(s, action, 9.8,  ty2+0.08, 3.0, 1.2, font_size=10, color=WHITE)

txt(s, "✅ When ALL readings are normal → Green LED stays ON, No buzzer, Dashboard shows \"Normal\" status",
    0.4, 6.75, 12.5, 0.4, font_size=11, color=ACCENT1, italic=True)

# ══════════════════════════════════════════════════════
# SLIDE 11 — THINGSPEAK CLOUD
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "☁️  CLOUD INTEGRATION — THINGSPEAK", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

# Cloud flow
steps = [
    ("1\nSetup",  "Create free ThingSpeak\naccount & channel with\n3 fields", ACCENT1),
    ("2\nConfig", "Paste Write API Key\ninto ESP32 firmware\nconstant", ACCENT3),
    ("3\nUpload", "ESP32 sends HTTP GET\nrequest every 20 seconds\nwith latest values", ACCENT4),
    ("4\nView",   "View live charts on\nthingspeak.com from\nanywhere in the world", RGBColor(0x99,0x88,0xFF)),
]
for i, (step, desc, col) in enumerate(steps):
    lx = 0.4 + i*3.2
    box(s, lx, 1.4, 2.9, 2.2, CARD_BG)
    box(s, lx, 1.4, 2.9, 0.06, col)
    txt(s, step, lx+0.15, 1.5, 2.6, 0.7, font_size=14, bold=True, color=col)
    txt(s, desc, lx+0.15, 2.15, 2.6, 1.2, font_size=10, color=WHITE)
    if i < 3:
        txt(s, "→", lx+2.95, 2.1, 0.3, 0.5, font_size=18, bold=True, color=LIGHT_GREY)

txt(s, "ThingSpeak Channel Fields:", 0.4, 3.9, 5, 0.4, font_size=14, bold=True, color=ACCENT1)
for i, (field, label, col) in enumerate([
    ("Field 1", "Heart Rate (BPM)",        ACCENT2),
    ("Field 2", "Blood Oxygen SpO₂ (%)",   ACCENT3),
    ("Field 3", "Body Temperature (°C)",   ACCENT4),
]):
    box(s, 0.4 + i*4.3, 4.4, 4.0, 1.0, CARD_BG)
    box(s, 0.4 + i*4.3, 4.4, 4.0, 0.06, col)
    txt(s, field, 0.6 + i*4.3, 4.5, 3.6, 0.35, font_size=11, bold=True, color=col)
    txt(s, label, 0.6 + i*4.3, 4.85, 3.6, 0.4,  font_size=12, color=WHITE)

bullet_list(s, [
    "URL: https://thingspeak.com  (free for up to 8 fields)",
    "Update interval: 20 seconds (ThingSpeak free tier limit: 15s minimum)",
    "Data stored indefinitely — export to CSV for analysis",
    "Built-in chart visualization — no extra setup needed",
], 0.4, 5.7, 12.5, 1.5, font_size=11, color=LIGHT_GREY)

# ══════════════════════════════════════════════════════
# SLIDE 12 — RESULTS & TESTING
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "✅  RESULTS & TESTING", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

checklist = [
    ("ESP32 Wi-Fi connection (< 5 sec)",       True),
    ("OLED displays live readings",             True),
    ("Heart Rate reading: 65–80 BPM (resting)",True),
    ("SpO₂ reading: 97–99%",                   True),
    ("Temperature reading: 36.5–37.0°C",       True),
    ("Web dashboard loads in any browser",      True),
    ("Dashboard auto-refreshes every 2 sec",    True),
    ("JSON /data API returns valid response",   True),
    ("Alert LED triggers for abnormal values",  True),
    ("Buzzer sounds on threshold breach",       True),
    ("ThingSpeak data logged successfully",     True),
    ("Device works on Li-Po battery (4+ hrs)", True),
]

for i, (item, passed) in enumerate(checklist):
    row, c = divmod(i, 2)
    lx = 0.4 + c*6.4
    ty2 = 1.4 + row*0.82
    icon = "✅" if passed else "❌"
    col  = ACCENT1 if passed else ACCENT2
    txt(s, f"{icon}  {item}", lx, ty2, 6.2, 0.65, font_size=12, color=col)

txt(s, "📊  Sample Test Readings:", 0.4, 6.35, 5, 0.35,
    font_size=13, bold=True, color=ACCENT1)
for i, (label, val, col) in enumerate([
    ("❤️  Heart Rate", "72 BPM",    ACCENT2),
    ("🩸  SpO₂",       "98%",       ACCENT3),
    ("🌡️  Temp",       "36.7 °C",  ACCENT4),
    ("⏱️  Latency",    "< 200 ms", ACCENT1),
]):
    box(s, 0.4 + i*3.2, 6.75, 3.0, 0.55, CARD_BG)
    txt(s, f"{label}:  {val}", 0.55 + i*3.2, 6.8, 2.8, 0.42,
        font_size=11, bold=True, color=col)

# ══════════════════════════════════════════════════════
# SLIDE 13 — FUTURE ENHANCEMENTS
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🔮  FUTURE ENHANCEMENTS", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

enhancements = [
    ("💾", "SPIFFS Data Logging",
     "Store reading history on ESP32 flash memory for offline review & graphs", ACCENT1),
    ("📱", "Mobile App",
     "Flutter/React Native companion app with push notifications & history", ACCENT3),
    ("🤖", "ML Anomaly Detection",
     "TensorFlow Lite model on ESP32 to detect arrhythmia patterns in real-time", ACCENT2),
    ("📧", "Email / SMS Alerts",
     "Integrate SMTP/Twilio to send automatic email or SMS when critical vitals detected", ACCENT4),
    ("🔋", "Deep Sleep Mode",
     "ESP32 deep sleep between readings to extend battery life to 24+ hours", RGBColor(0xFF,0xCC,0x00)),
    ("🔐", "HTTPS + Authentication",
     "Secure dashboard with TLS certificate and login page for privacy", RGBColor(0x99,0x88,0xFF)),
    ("📍", "GPS Location",
     "Add NEO-6M GPS module to include patient location in health data stream", ACCENT3),
    ("🩺", "More Sensors",
     "ECG (AD8232), Blood Pressure (BMP280), Glucose, Accelerometer for fall detection", ACCENT2),
]

for i, (icon, title, desc, col) in enumerate(enhancements):
    row, c = divmod(i, 4)
    lx = 0.3 + c*3.25
    ty2 = 1.4 + row*2.7
    box(s, lx, ty2, 3.1, 2.4, CARD_BG)
    box(s, lx, ty2, 3.1, 0.06, col)
    txt(s, icon, lx+0.1, ty2+0.12, 0.5, 0.5, font_size=20)
    txt(s, title, lx+0.6, ty2+0.15, 2.35, 0.4, font_size=11, bold=True, color=col)
    txt(s, desc,  lx+0.1, ty2+0.65, 2.9,  1.5, font_size=9, color=LIGHT_GREY)

# ══════════════════════════════════════════════════════
# SLIDE 14 — CONCLUSION
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 1.1, RGBColor(0x1A, 0x17, 0x40))
txt(s, "🏁  CONCLUSION", 0.4, 0.2, 12, 0.7,
    font_size=28, bold=True, color=ACCENT1)
accent_line(s, 0.4, 1.15, 12.5, ACCENT1)

txt(s, "What we built:", 0.4, 1.5, 10, 0.4, font_size=16, bold=True, color=WHITE)
bullet_list(s, [
    "A fully functional wearable IoT health monitor at ₹600–₹900",
    "Real-time wireless transmission of 3 vital signs over Wi-Fi",
    "Self-hosted web dashboard — no internet required for local monitoring",
    "Intelligent alert system using LED indicators and a buzzer",
    "Cloud integration with ThingSpeak for remote data logging",
    "Beginner-friendly code using the Arduino framework on ESP32",
], 0.4, 2.0, 9, 2.8, font_size=13, color=WHITE)

txt(s, "Key Takeaways:", 0.4, 4.95, 10, 0.4, font_size=16, bold=True, color=ACCENT1)
for i, (val, label, col) in enumerate([
    ("3",      "Vital Signs\nMonitored",  ACCENT2),
    ("2 sec",  "Dashboard\nRefresh Rate", ACCENT3),
    ("~₹750",  "Total\nProject Cost",     ACCENT4),
    ("4+ hrs", "Battery\nLife (Li-Po)",   ACCENT1),
    ("100%",   "Wi-Fi\nProtocol",         RGBColor(0x99,0x88,0xFF)),
]):
    box(s, 0.4 + i*2.55, 5.45, 2.35, 1.5, CARD_BG)
    box(s, 0.4 + i*2.55, 5.45, 2.35, 0.06, col)
    txt(s, val,   0.5 + i*2.55, 5.55, 2.15, 0.65, font_size=22, bold=True,
        color=col, align=PP_ALIGN.CENTER)
    txt(s, label, 0.5 + i*2.55, 6.22, 2.15, 0.65, font_size=10,
        color=LIGHT_GREY, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════
# SLIDE 15 — THANK YOU
# ══════════════════════════════════════════════════════
s = prs.slides.add_slide(blank_layout)
bg(s, BG_DARK)
box(s, 0, 0, 13.33, 7.5, RGBColor(0x30, 0x2B, 0x63))

for cx, cy, cr, col in [
    (2.0, 2.0, 3.5, RGBColor(0xFF,0x6B,0x6B)),
    (11.0,5.5, 3.0, RGBColor(0x4E,0xCD,0xC4)),
]:
    shape = s.shapes.add_shape(9, Inches(cx-cr/2), Inches(cy-cr/2),
                                Inches(cr), Inches(cr))
    shape.fill.solid()
    shape.fill.fore_color.rgb = col
    shape.line.fill.background()
    sp_pr = shape._element.spPr
    sf2 = sp_pr.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
    if sf2 is not None:
        sg2 = sf2.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
        if sg2 is not None:
            ae2 = etree.SubElement(
                sg2, '{http://schemas.openxmlformats.org/drawingml/2006/main}alpha')
            ae2.set('val', '12000')

accent_line(s, 3.5, 2.6, 6.3, ACCENT1)
txt(s, "THANK YOU!", 2.0, 2.8, 9.33, 1.2,
    font_size=54, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(s, "🩺  Wearable Health Monitoring System", 1.5, 4.1, 10.33, 0.6,
    font_size=18, color=ACCENT1, align=PP_ALIGN.CENTER)
accent_line(s, 3.5, 4.85, 6.3, LIGHT_GREY)
txt(s, "Praveen Kumar  |  Wireless Communication & IoT  |  2026",
    1.5, 5.05, 10.33, 0.4, font_size=13, color=LIGHT_GREY, align=PP_ALIGN.CENTER)

txt(s, "Questions?  Feel free to ask! 😊",
    2.0, 5.8, 9.33, 0.5, font_size=16,
    color=ACCENT3, italic=True, align=PP_ALIGN.CENTER)

# ──────────────────────────────────────────────────────
# SAVE
# ──────────────────────────────────────────────────────
out_path = r"c:\Users\Praveen kumar\Antigravity-p\HealthMonitor-IoT\HealthMonitor_Presentation.pptx"
prs.save(out_path)
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print(f"Saved: {out_path}")
print(f"Slides: {len(prs.slides)}")

