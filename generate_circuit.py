"""
Circuit Diagram Generator — Wearable Health Monitor
Uses matplotlib to draw a clean system block diagram
Run: python generate_circuit.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(1, 1, figsize=(18, 11))
fig.patch.set_facecolor('#0F0C29')
ax.set_facecolor('#0F0C29')
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis('off')

# ── helper: rounded box ──────────────────────────────────────
def draw_box(ax, x, y, w, h, bg, border, title, subtitle='', subtitle2='', title_color='white', sub_color='#AAAACC'):
    box = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.1",
        facecolor=bg, edgecolor=border, linewidth=2.5, zorder=3)
    ax.add_patch(box)
    # top accent bar
    accent = FancyBboxPatch((x, y+h-0.18), w, 0.18,
        boxstyle="round,pad=0.0",
        facecolor=border, edgecolor='none', zorder=4)
    ax.add_patch(accent)
    ax.text(x+w/2, y+h-0.42, title, ha='center', va='center',
            fontsize=11, fontweight='bold', color=title_color,
            zorder=5, fontfamily='DejaVu Sans')
    if subtitle:
        ax.text(x+w/2, y+h-0.78, subtitle, ha='center', va='center',
                fontsize=8.5, color=sub_color, zorder=5)
    if subtitle2:
        ax.text(x+w/2, y+0.38, subtitle2, ha='center', va='center',
                fontsize=7.5, color='#888899', zorder=5, style='italic')

def arrow(ax, x1, y1, x2, y2, color='#00FF88', label='', lw=2, style='->', bidirectional=False):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color,
                        lw=lw, connectionstyle='arc3,rad=0.0'), zorder=6)
    if bidirectional:
        ax.annotate('', xy=(x1, y1), xytext=(x2, y2),
            arrowprops=dict(arrowstyle=style, color=color,
                            lw=lw, connectionstyle='arc3,rad=0.0'), zorder=6)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.15, label, ha='center', va='bottom',
                fontsize=7.5, color=color, zorder=7,
                bbox=dict(boxstyle='round,pad=0.2', fc='#0F0C29', ec='none', alpha=0.8))

# ────────────────────────────────────────────────────────────
# TITLE
# ────────────────────────────────────────────────────────────
ax.text(9, 10.5, 'Wearable Health Monitoring System -- Circuit Block Diagram',
        ha='center', va='center', fontsize=16, fontweight='bold',
        color='white', zorder=10)
ax.text(9, 10.1, 'ESP32  +  MAX30102  +  DS18B20  +  SSD1306 OLED  |  Wi-Fi 802.11',
        ha='center', va='center', fontsize=10, color='#AAAACC', zorder=10)

# ────────────────────────────────────────────────────────────
# CENTRAL: ESP32
# ────────────────────────────────────────────────────────────
draw_box(ax, 6.5, 3.8, 5.0, 3.6,
         bg='#1A3A1A', border='#00FF88',
         title='ESP32 Dev Board',
         subtitle='Dual-Core 240MHz | 4MB Flash | Wi-Fi',
         subtitle2='GPIO21(SDA) | GPIO22(SCL) | GPIO4 | GPIO12/13/15',
         title_color='#00FF88')

# Internal labels
for txt, yy in [('I2C Bus → GPIO21/22', 5.8), ('1-Wire → GPIO4', 5.35),
                ('Buzzer → GPIO15', 4.9), ('LEDs → GPIO12/13', 4.45)]:
    ax.text(9.0, yy, txt, ha='center', va='center', fontsize=7.5,
            color='#88EEAA', zorder=6)

# ────────────────────────────────────────────────────────────
# SENSORS (left side)
# ────────────────────────────────────────────────────────────
# MAX30102
draw_box(ax, 0.5, 6.5, 3.8, 2.0,
         bg='#2A1018', border='#FF6B6B',
         title='MAX30102', subtitle='Heart Rate + SpO2',
         subtitle2='VCC:3.3V | SDA | SCL | GND',
         title_color='#FF6B6B')
ax.text(2.4, 7.15, 'Optical PPG Sensor\nI2C Address: 0x57', ha='center',
        va='center', fontsize=8, color='#FFAAAA', zorder=5)

# DS18B20
draw_box(ax, 0.5, 3.8, 3.8, 2.0,
         bg='#2A1A00', border='#FFA500',
         title='DS18B20', subtitle='Body Temperature',
         subtitle2='VCC:5V | Data+4.7kΩ | GND',
         title_color='#FFA500')
ax.text(2.4, 4.55, 'Digital Temp Sensor\n1-Wire Protocol', ha='center',
        va='center', fontsize=8, color='#FFCC88', zorder=5)

# ────────────────────────────────────────────────────────────
# OUTPUT (right side)
# ────────────────────────────────────────────────────────────
# SSD1306 OLED
draw_box(ax, 13.7, 6.5, 3.8, 2.0,
         bg='#0A1A2A', border='#4ECDC4',
         title='SSD1306 OLED', subtitle='128x64 Display',
         subtitle2='VCC:3.3V | SDA | SCL | GND',
         title_color='#4ECDC4')
ax.text(15.6, 7.15, 'Local Visual Display\nI2C Address: 0x3C', ha='center',
        va='center', fontsize=8, color='#88EEFF', zorder=5)

# Buzzer
draw_box(ax, 13.7, 4.5, 3.8, 1.7,
         bg='#2A2800', border='#FFCC00',
         title='Passive Buzzer', subtitle='Audio Alert',
         subtitle2='GPIO15 | GND',
         title_color='#FFCC00')

# LEDs
draw_box(ax, 13.7, 2.5, 3.8, 1.7,
         bg='#1A0A1A', border='#FF4444',
         title='LEDs (Red + Green)', subtitle='Visual Indicator',
         subtitle2='GPIO12(Green) | GPIO13(Red) | 220Ω',
         title_color='#FF6666')

# ────────────────────────────────────────────────────────────
# CLOUD / NETWORK (bottom)
# ────────────────────────────────────────────────────────────
draw_box(ax, 0.5, 0.5, 3.8, 2.4,
         bg='#0A0A2A', border='#9988FF',
         title='Wi-Fi Router', subtitle='IEEE 802.11 b/g/n',
         subtitle2='2.4GHz | WPA2-PSK',
         title_color='#9988FF')
ax.text(2.4, 1.3, 'Wireless\nAccess Point', ha='center',
        va='center', fontsize=9, color='#BBAAFF', zorder=5)

draw_box(ax, 5.5, 0.5, 3.8, 2.4,
         bg='#0A1A0A', border='#00FF88',
         title='Web Dashboard', subtitle='Browser (Any Device)',
         subtitle2='http://ESP32-IP | Auto-refresh 2s',
         title_color='#00FF88')
ax.text(7.4, 1.3, 'Live Charts\nJSON REST API', ha='center',
        va='center', fontsize=9, color='#88FFCC', zorder=5)

draw_box(ax, 10.5, 0.5, 3.8, 2.4,
         bg='#001A2A', border='#4ECDC4',
         title='ThingSpeak Cloud', subtitle='Remote Logging',
         subtitle2='Field1:HR | Field2:SpO2 | Field3:Temp',
         title_color='#4ECDC4')
ax.text(12.4, 1.3, 'Charts & Alerts\nEvery 20 seconds', ha='center',
        va='center', fontsize=9, color='#88EEFF', zorder=5)

# Power block
draw_box(ax, 14.8, 0.5, 2.8, 2.4,
         bg='#1A1A00', border='#FFCC00',
         title='Li-Po Battery', subtitle='3.7V + TP4056',
         subtitle2='1000mAh | USB-C Charging',
         title_color='#FFCC00')

# ────────────────────────────────────────────────────────────
# ARROWS
# ────────────────────────────────────────────────────────────
# MAX30102 → ESP32 (I2C)
arrow(ax, 4.3, 7.5, 6.5, 6.5, color='#FF6B6B', label='I2C (SDA/SCL)', bidirectional=True)
# DS18B20 → ESP32 (1-Wire)
arrow(ax, 4.3, 4.8, 6.5, 5.2, color='#FFA500', label='1-Wire', lw=2)
# ESP32 → OLED (I2C)
arrow(ax, 11.5, 6.5, 13.7, 7.5, color='#4ECDC4', label='I2C (SDA/SCL)', bidirectional=True)
# ESP32 → Buzzer
arrow(ax, 11.5, 5.4, 13.7, 5.35, color='#FFCC00', label='GPIO15')
# ESP32 → LEDs
arrow(ax, 11.5, 4.2, 13.7, 3.35, color='#FF4444', label='GPIO12/13')
# ESP32 → Wi-Fi (down)
arrow(ax, 8.0, 3.8, 2.4, 2.9, color='#9988FF', label='Wi-Fi 802.11', lw=2.5)
# Wi-Fi → Dashboard
arrow(ax, 4.3, 1.7, 5.5, 1.7, color='#00FF88', label='HTTP', lw=2)
# Wi-Fi → ThingSpeak
arrow(ax, 4.3, 1.5, 10.5, 1.5, color='#4ECDC4', label='TCP/HTTP', lw=2)
# Battery → ESP32
arrow(ax, 15.8, 2.9, 11.5, 4.0, color='#FFCC00', label='3.7V Power', lw=1.5)

# ────────────────────────────────────────────────────────────
# LEGEND
# ────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color='#FF6B6B', label='Heart Rate & SpO2 (MAX30102)'),
    mpatches.Patch(color='#FFA500', label='Temperature (DS18B20)'),
    mpatches.Patch(color='#4ECDC4', label='Display (SSD1306 OLED)'),
    mpatches.Patch(color='#00FF88', label='ESP32 MCU / Wi-Fi'),
    mpatches.Patch(color='#FFCC00', label='Alert / Power'),
    mpatches.Patch(color='#9988FF', label='Wireless Network'),
]
legend = ax.legend(handles=legend_items, loc='lower center',
                   ncol=3, bbox_to_anchor=(0.5, -0.01),
                   framealpha=0.2, facecolor='#1A1A2A',
                   edgecolor='#444466', labelcolor='white',
                   fontsize=8.5, handlelength=1.5)

ax.text(9, 0.18, 'Praveen Kumar  |  Wearable Health Monitoring System  |  IoT & Wireless Communication  |  2026',
        ha='center', va='center', fontsize=7.5, color='#666688', zorder=10)

plt.tight_layout(pad=0.5)
out = r"c:\Users\Praveen kumar\Antigravity-p\HealthMonitor-IoT\docs\circuit_diagram.png"
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor='#0F0C29', edgecolor='none')
print(f"Saved: {out}")
plt.close()
