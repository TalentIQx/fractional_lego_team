# app.py
import os
import json
import time
import logging
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🦷 Lego Manufacturing Command Center", layout="wide")

# ---------------- LOGGING / ANALYTICS ----------------
# Local analytics file (fallback) and optional remote endpoint
ANALYTICS_ENDPOINT = os.environ.get("ANALYTICS_ENDPOINT")  # e.g., https://your-analytics.example/collect
ANALYTICS_LOCAL_FILE = "analytics.log"

logging.basicConfig(filename=ANALYTICS_LOCAL_FILE, level=logging.INFO, format="%(asctime)s %(message)s")

def log_event(event_name: str, payload: dict):
    """Log analytics event locally and optionally POST to remote endpoint."""
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "event": event_name,
        "payload": payload
    }
    # Local log
    logging.info(json.dumps(record))
    # Remote POST if endpoint configured
    if ANALYTICS_ENDPOINT:
        try:
            requests.post(ANALYTICS_ENDPOINT, json=record, timeout=5)
        except Exception:
            # Do not raise; analytics must not break app
            logging.info(json.dumps({"ts": datetime.utcnow().isoformat()+"Z", "event":"analytics_error", "payload":{"error":"post_failed"}}))

# Example event at app start
log_event("app_opened", {"page":"main"})

# ---------------- PLOTLY PALETTES (tuned) ----------------
# Palette 4: warm Lego gradient (reds -> yellows -> cyan)
PALETTE_4 = ["#ff0000", "#ff6f00", "#ffcc00", "#00aaff"]
# Palette 5: cool Lego gradient (teal -> blue -> purple)
PALETTE_5 = ["#00cc44", "#00aaff", "#3f51b5", "#8e24aa"]

# Apply default template settings for dark background
px.defaults.template = None

def apply_dark_layout(fig):
    fig.update_layout(
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font_color="#f5f5f5",
        legend=dict(font=dict(color="#f5f5f5")),
        xaxis=dict(gridcolor="#111111", zerolinecolor="#111111", tickcolor="#f5f5f5"),
        yaxis=dict(gridcolor="#111111", zerolinecolor="#111111", tickcolor="#f5f5f5")
    )
    return fig

# ---------------- ONBOARDING WIZARD ----------------
if "seen_onboarding" not in st.session_state:
    st.session_state["seen_onboarding"] = False

def finish_onboarding():
    st.session_state["seen_onboarding"] = True
    log_event("onboarding_completed", {"user_action":"finished"})
    st.experimental_rerun()

if not st.session_state["seen_onboarding"]:
    with st.modal("Welcome to Lego Manufacturing Command Center", True):
        st.markdown("### 👋 Welcome, Founder\nThis short onboarding will help you get comfortable with the app.")
        st.markdown("- **Quick Summary** shows revenue, runway, and margin.\n- **Lab Health** tab visualizes product mix and runway under shocks.\n- **AI Coach** tab simulates advice and can call your secure backend.\n- **Beginner mode** explains terms in plain English.")
        st.write("Choose your preferred vibe:")
        c1, c2 = st.columns(2)
        if c1.button("Playful Lego (default)"):
            finish_onboarding()
        if c2.button("Minimal Lego"):
            finish_onboarding()

# ---------------- CUSTOM CSS: FULL BLACK LEGO THEME ----------------
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #f5f5f5; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg,#000,#0a0a0a) !important; border-right:3px solid #111; padding:18px; }
    .lego-header { background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff,#00cc44); color:black; padding:10px 18px; border-radius:10px; font-weight:900; font-size:20px; display:inline-block; }
    .portal-card { background:#0f0f10; border-radius:14px; padding:20px; box-shadow:0 0 18px rgba(255,255,255,0.03); border-left:8px solid #00aaff; color:#f5f5f5; margin-bottom:12px; }
    .portal-card.success { border-left-color:#00cc44; } .portal-card.warning { border-left-color:#ffcc00; } .portal-card.critical { border-left-color:#ff0000; }
    .badge { font-weight:700; border-radius:12px; padding:4px 12px; font-size:12px; }
    .badge.green { background:#003300; color:#00ff55; } .badge.yellow { background:#332b00; color:#ffcc00; } .badge.red { background:#330000; color:#ff4444; }
    .stTabs [data-baseweb="tab-list"] { background:#0b0b0b; padding:12px; border-radius:14px; box-shadow:0 0 18px rgba(255,255,255,0.15); gap:12px; }
    .stTabs [data-baseweb="tab"] { font-weight:900 !important; color:#fff !important; border-radius:10px; padding:12px 24px; background:#222; border:2px solid #333; transition:0.2s; font-size:16px; }
    .stTabs [data-baseweb="tab"]:hover { background:#333; border-color:#ffcc00; transform:translateY(-2px); }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff,#00cc44); color:#000 !important; border:2px solid #fff; box-shadow:0 0 14px rgba(255,255,255,0.4); }
    .stButton>button { background: linear-gradient(90deg,#ff0000,#ffcc00); color:#000; border-radius:10px; padding:8px 18px; font-weight:800; border:none; box-shadow:0 6px 18px rgba(255,255,255,0.06); }
    .stButton>button:hover { transform:translateY(-2px); box-shadow:0 10px 28px rgba(255,255,255,0.12); }
    .rec-card { background:#0f0f10; border-radius:10px; padding:14px; margin-bottom:12px; border-left:6px solid:#00aaff; color:#f5f5f5; }
    .rec-card.urgent { border-left-color:#ff0000; background:#120808; } .rec-card.high { border-left-color:#ffcc00; background:#14120a; } .rec-card.medium { border-left-color:#00aaff; background:#071022; }
    .lego-divider { height:6px; background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff,#00cc44); border-radius:4px; margin:24px 0; }
    .small-muted { color:#bdbdbd; font-size:13px; }
    .metric-value { font-size:28px; font-weight:800; color:#f5f5f5; }
    .stPlotlyChart > div { background: #000000 !important; }
    label, .stMarkdown, .stText, .stMetric { color: #f5f5f5 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.markdown("""
<div style="background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff); padding:14px; border-radius:12px; color:black; text-align:center; margin-bottom:12px;">
    <span style="font-size:34px;">🧱</span>
    <h3 style="margin:0; color:black;">Your Lab Blocks</h3>
    <p style="margin:0; font-size:12px; opacity:0.9;">Build your financial picture</p>
</div>
""", unsafe_allow_html=True)

implants = st.sidebar.number_input("🦷 Implants (units/mo)", value=45, step=5, key="implants")
crowns = st.sidebar.number_input("👑 Crowns (units/mo)", value=120, step=10, key="crowns")
veneers = st.sidebar.number_input("✨ Veneers (units/mo)", value=60, step=5, key="veneers")
mouthguards = st.sidebar.number_input("🛡️ Mouth Guards (units/mo)", value=200, step=20, key="mouthguards")
dentures = st.sidebar.number_input("🦷 Dentures (units/mo)", value=35, step=5, key="dentures")

product_units = {"Implants": implants, "Crowns": crowns, "Veneers": veneers, "Mouth Guards": mouthguards, "Dentures": dentures}
product_prices = {"Implants": 1200, "Crowns": 350, "Veneers": 400, "Mouth Guards": 50, "Dentures": 800}

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Financial Blocks")
material_cost_pct = st.sidebar.slider("Material cost %", 20, 50, 32, step=2, key="mat_cost") / 100
labor_cost = st.sidebar.number_input("Labor cost ($/mo)", value=25000, step=1000, key="labor")
overhead = st.sidebar.number_input("Overhead ($/mo)", value=15000, step=1000, key="overhead")
marketing_budget = st.sidebar.number_input("Marketing ($/mo)", value=5000, step=500, key="marketing")
owner_draw = st.sidebar.number_input("Your draw ($/mo)", value=12000, step=1000, key="draw")
cash_reserve = st.sidebar.number_input("Cash in bank ($)", value=200000, step=10000, key="cash")

# ---------------- CALCULATIONS ----------------
product_revenue = {p: product_units[p] * product_prices[p] for p in product_units}
monthly_revenue = sum(product_revenue.values())
b2b_percent = st.sidebar.slider("B2B revenue %", 50, 100, 80, step=5, key="b2b_pct") / 100
b2c_percent = 1 - b2b_percent

material_cost = monthly_revenue * material_cost_pct
total_costs = material_cost + labor_cost + overhead + marketing_budget + owner_draw
monthly_profit = monthly_revenue - total_costs
net_burn = total_costs - monthly
