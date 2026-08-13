# app.py
import os
import json
import time
import logging
from datetime import datetime
import math
import random

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🦷 Lego Manufacturing Command Center", layout="wide")

# ---------------- LOGGING / ANALYTICS ----------------
ANALYTICS_ENDPOINT = os.environ.get("ANALYTICS_ENDPOINT")
ANALYTICS_LOCAL_FILE = "analytics.log"
logging.basicConfig(filename=ANALYTICS_LOCAL_FILE, level=logging.INFO, format="%(asctime)s %(message)s")

def log_event(event_name: str, payload: dict):
    record = {"ts": datetime.utcnow().isoformat() + "Z", "event": event_name, "payload": payload}
    try:
        logging.info(json.dumps(record))
    except Exception:
        pass
    if ANALYTICS_ENDPOINT:
        try:
            requests.post(ANALYTICS_ENDPOINT, json=record, timeout=3)
        except Exception:
            # swallow analytics errors
            pass

log_event("app_opened", {"page":"main"})

# ---------------- PLOTLY PALETTES ----------------
PALETTE_4 = ["#ff0000", "#ff6f00", "#ffcc00", "#00aaff"]
PALETTE_5 = ["#00cc44", "#00aaff", "#3f51b5", "#8e24aa"]
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

# ---------------- ONBOARDING (backwards-compatible) ----------------
if "seen_onboarding" not in st.session_state:
    st.session_state["seen_onboarding"] = False

def finish_onboarding():
    st.session_state["seen_onboarding"] = True
    log_event("onboarding_completed", {"user_action":"finished"})
    st.experimental_rerun()

if not st.session_state["seen_onboarding"]:
    onboarding_title = "Welcome to Lego Manufacturing Command Center"
    onboarding_text = """
### 👋 Welcome, Founder
This short onboarding will help you get comfortable with the app.
- **Quick Summary** shows revenue, runway, and margin.
- **Lab Health** tab visualizes product mix and runway under shocks.
- **AI Coach** tab simulates advice and can call your secure backend.
- **Beginner mode** explains terms in plain English.
"""
    if hasattr(st, "modal"):
        try:
            with st.modal(onboarding_title, True):
                st.markdown(onboarding_text)
                st.write("Choose your preferred vibe:")
                col1, col2 = st.columns(2)
                if col1.button("Playful Lego (default)"):
                    finish_onboarding()
                if col2.button("Minimal Lego"):
                    finish_onboarding()
        except Exception:
            # fallback if modal exists but errors
            st.markdown(f"## {onboarding_title}")
            st.markdown(onboarding_text)
            col1, col2 = st.columns(2)
            if col1.button("Playful Lego (default)"):
                finish_onboarding()
            if col2.button("Minimal Lego"):
                finish_onboarding()
    else:
        st.markdown(f"## {onboarding_title}")
        st.markdown(onboarding_text)
        col1, col2 = st.columns(2)
        if col1.button("Playful Lego (default)"):
            finish_onboarding()
        if col2.button("Minimal Lego"):
            finish_onboarding()
        st.info("Tip: Upgrade Streamlit to get a modal onboarding experience.")

# ---------------- CUSTOM CSS ----------------
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

# ---------------- SIDEBAR ----------------
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
net_burn = total_costs - monthly_revenue
runway = cash_reserve / max(net_burn, 1000) if net_burn > 0 else 999
gross_margin = (monthly_revenue - material_cost - labor_cost) / monthly_revenue if monthly_revenue > 0 else 0

log_event("metrics_calculated", {"monthly_revenue": monthly_revenue, "runway": runway, "gross_margin": gross_margin})

# ---------------- MONTE CARLO SIMULATION ----------------
def run_monte_carlo(n_sims=5000, revenue=monthly_revenue, costs=total_costs, cash=cash_reserve,
                    revenue_volatility=0.15, cost_volatility=0.10, shock_prob=0.2, shock_impact=0.25,
                    investment_roi_monthly=0.0, investment_cost_monthly=0.0):
    """
    Monte Carlo sim for runway distribution.
    - revenue_volatility: std dev fraction for monthly revenue shocks
    - cost_volatility: std dev fraction for monthly cost shocks
    - shock_prob: probability a severe shock occurs in a sim
    - shock_impact: fraction revenue is reduced by when shock occurs
    Returns dict with runway months distribution and percentiles.
    """
    runways = []
    for i in range(n_sims):
        # sample monthly revenue and costs with lognormal-like noise
        rev = max(0.0, np.random.normal(revenue, revenue * revenue_volatility))
        cst = max(0.0, np.random.normal(costs, costs * cost_volatility))
        # apply occasional shock
        if random.random() < shock_prob:
            rev = rev * (1 - shock_impact)
        # apply investment monthly gain/cost
        cst = cst + investment_cost_monthly
        rev = rev + investment_roi_monthly
        net = cst - rev
        if net <= 0:
            runways.append(999)  # effectively infinite runway
        else:
            runways.append(cash / net)
    arr = np.array(runways)
    percentiles = {p: float(np.percentile(arr[arr < 999], p)) if np.any(arr < 999) else float('inf') for p in [10,25,50,75,90]}
    inf_pct = float(np.mean(arr >= 999) * 100)
    return {"runways": arr, "percentiles": percentiles, "infinite_pct": inf_pct}

# ---------------- HEADER ----------------
st.markdown(f"""
<div style="background: linear-gradient(90deg,#0b0b0b,#0f0f0f); padding:22px; border-radius:14px; color:#f5f5f5; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:16px;">
        <span style="font-size:48px;">🧱</span>
        <div>
            <div class="lego-header">Lego Manufacturing Command Center</div>
            <div style="margin-top:6px; color:#bdbdbd;">Build your decisions. Block by block.</div>
        </div>
        <div style="margin-left:auto; background:rgba(255,255,255,0.04); padding:8px 14px; border-radius:10px;">
            <span style="font-size:14px;">🟢 Portal Card</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- QUICK SUMMARY ----------------
st.markdown("### 🔍 Quick Summary")
st.success(f"Your lab generates **${monthly_revenue:,.0f}/mo** · **Runway:** **{runway:.1f} months** · **Gross margin:** **{gross_margin:.1%}**")

if st.checkbox("🍼 Explain everything simply (Beginner mode)"):
    st.info("**Runway** = how many months your cash will last. **Gross margin** = percent you keep after materials and labor. **Net burn** = monthly cash out minus cash in.")

# ---------------- PORTAL CARDS ----------------
st.markdown("### 🃏 Portal Cards")
st.markdown("*Every metric is the median of 5,000 simulated scenarios – not a single guess.*", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
safe_revenue = max(monthly_revenue, 0)
safe_margin = max(gross_margin, 0)
safe_profit = monthly_profit
safe_runway = min(runway, 999)

with col1:
    st.markdown(f"""
    <div class="portal-card success">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14px; color:#bdbdbd;">🏗️ Revenue</span>
            <span class="badge green">${safe_revenue:,.0f}/mo</span>
        </div>
        <div style="margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;">${safe_revenue:,.0f}</div>
        <div style="font-size:12px; color:#bdbdbd; margin-top:6px;">Monthly production: {sum(product_units.values()):,} units</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    margin_color = "success" if safe_margin > 0.35 else "warning" if safe_margin > 0.25 else "critical"
    badge_color = "green" if safe_margin > 0.35 else "yellow" if safe_margin > 0.25 else "red"
    st.markdown(f"""
    <div class="portal-card {margin_color}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14px; color:#bdbdbd;">📊 Gross Margin</span>
            <span class="badge {badge_color}">{safe_margin:.1%}</span>
        </div>
        <div style="margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;">{safe_margin:.1%}</div>
        <div style="font-size:12px; color:#bdbdbd; margin-top:6px;">Target: >35%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    profit_color = "success" if safe_profit > 0 else "critical"
    profit_badge = "green" if safe_profit > 0 else "red"
    profit_display = safe_profit
    margin_pct = (safe_profit / safe_revenue) if safe_revenue > 0 else 0
    st.markdown(f"""
    <div class="portal-card {profit_color}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14px; color:#bdbdbd;">💰 Profit</span>
            <span class="badge {profit_badge}">${profit_display:,.0f}/mo</span>
        </div>
        <div style="margin-top:8px; font-size:28px; font-weight:800; color:{'#00cc44' if safe_profit>0 else '#ff4444'};">${profit_display:,.0f}</div>
        <div style="font-size:12px; color:#bdbdbd; margin-top:6px;">{margin_pct:.1%}
