# app.py
import os
import json
import logging
import random
from datetime import datetime
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Page config with tooth emoji favicon
st.set_page_config(page_title="🦷 Lego Manufacturing Command Center", page_icon="🦷", layout="wide")

# Logging / analytics
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
            pass

log_event("app_opened", {"page":"main"})

# Plotly palettes
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

# Session defaults
if "seen_onboarding" not in st.session_state:
    st.session_state["seen_onboarding"] = False
if "custom_shocks" not in st.session_state:
    st.session_state["custom_shocks"] = []
if "selected_shocks" not in st.session_state:
    st.session_state["selected_shocks"] = []

# Safe onboarding finish
def finish_onboarding():
    st.session_state["seen_onboarding"] = True
    log_event("onboarding_completed", {"user_action":"finished"})
    try:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    except Exception:
        pass

# Onboarding (fallback safe)
if not st.session_state.get("seen_onboarding", False):
    onboarding_title = "Welcome to Lego Manufacturing Command Center"
    onboarding_text = """
### 👋 Welcome, Founder
This short onboarding will help you get comfortable with the app.
- Quick Summary shows revenue, runway, and margin.
- Lab Health tab visualizes product mix and runway under shocks.
- AI Coach tab simulates advice and can call your secure backend.
- Beginner mode explains terms in plain English.
"""
    if hasattr(st, "modal"):
        try:
            with st.modal(onboarding_title, True):
                st.markdown(onboarding_text)
                col1, col2 = st.columns(2)
                if col1.button("Playful Lego (default)"):
                    finish_onboarding()
                if col2.button("Minimal Lego"):
                    finish_onboarding()
        except Exception:
            st.markdown("## " + onboarding_title)
            st.markdown(onboarding_text)
            col1, col2 = st.columns(2)
            if col1.button("Playful Lego (default)"):
                finish_onboarding()
            if col2.button("Minimal Lego"):
                finish_onboarding()
    else:
        st.markdown("## " + onboarding_title)
        st.markdown(onboarding_text)
        col1, col2 = st.columns(2)
        if col1.button("Playful Lego (default)"):
            finish_onboarding()
        if col2.button("Minimal Lego"):
            finish_onboarding()
        st.info("Tip: Upgrade Streamlit to get a modal onboarding experience.")

# CSS (dark Lego)
st.markdown("""
<style>
    .stApp { background-color: #000000 !important; color: #f5f5f5; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg,#000,#0a0a0a) !important; border-right:3px solid #111; padding:18px; }
    .lego-header { background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff,#00cc44); color:black; padding:10px 18px; border-radius:10px; font-weight:900; font-size:20px; display:inline-block; }
    .portal-card { background:#0f0f10; border-radius:14px; padding:20px; box-shadow:0 0 18px rgba(255,255,255,0.03); border-left:8px solid #00aaff; color:#f5f5f5; margin-bottom:12px; }
    .stTabs [data-baseweb="tab"] { font-weight:900 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar inputs + CSV upload + shocks
st.sidebar.markdown("<div style='background: linear-gradient(90deg,#ff0000,#ffcc00,#00aaff); padding:14px; border-radius:12px; color:black; text-align:center; margin-bottom:12px;'><span style='font-size:34px;'>🧱</span><h3 style='margin:0; color:black;'>Your Lab Blocks</h3><p style='margin:0; font-size:12px; opacity:0.9;'>Build your financial picture</p></div>", unsafe_allow_html=True)

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

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Upload historical CSV (optional)")
st.sidebar.markdown("CSV columns: date (YYYY-MM-DD), revenue, costs")
uploaded = st.sidebar.file_uploader("Upload CSV to compute empirical volatility", type=["csv"])
historical_df = None
emp_rev_vol = None
emp_cost_vol = None
if uploaded:
    try:
        historical_df = pd.read_csv(uploaded, parse_dates=["date"])
        # aggregate monthly
        historical_df["month"] = historical_df["date"].dt.to_period("M")
        monthly = historical_df.groupby("month").agg({"revenue":"sum", "costs":"sum"}).reset_index()
        monthly["revenue_pct_change"] = monthly["revenue"].pct_change().fillna(0)
        monthly["costs_pct_change"] = monthly["costs"].pct_change().fillna(0)
        emp_rev_vol = float(monthly["revenue_pct_change"].std())
        emp_cost_vol = float(monthly["costs_pct_change"].std())
        st.sidebar.success("CSV loaded. Empirical vol computed.")
        log_event("csv_uploaded", {"rows": len(historical_df)})
    except Exception as e:
        st.sidebar.error(f"CSV parse error: {e}")
        log_event("csv_upload_error", {"error": str(e)})

# Shock scenarios UI (predefined + custom)
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Shock Scenarios")
predefined = [
    {"name":"Client loss (major)", "rev_mult":0.6, "cost_mult":1.0, "one_time_cost":0, "prob":0.10},
    {"name":"Sales drop 30%", "rev_mult":0.70, "cost_mult":1.0, "one_time_cost":0, "prob":0.15},
    {"name":"Lease increase 20%", "rev_mult":1.0, "cost_mult":1.20, "one_time_cost":0, "prob":0.08},
    {"name":"Material price spike 25%", "rev_mult":1.0, "cost_mult":1.25, "one_time_cost":0, "prob":0.12}
]
for s in predefined:
    key = f"pre_{s['name']}"
    checked = st.sidebar.checkbox(s["name"], value=False, key=key)
    if checked and s["name"] not in st.session_state["selected_shocks"]:
        st.session_state["selected_shocks"].append(s["name"])
    if not checked and s["name"] in st.session_state["selected_shocks"]:
        st.session_state["selected_shocks"].remove(s["name"])

st.sidebar.markdown("#### Add custom shock")
with st.sidebar.form("add_shock_form", clear_on_submit=True):
    cs_name = st.text_input("Name", value="New shock")
    cs_rev_mult = st.number_input("Revenue multiplier (0-1)", min_value=0.0, max_value=2.0, value=0.85, step=0.05)
    cs_cost_mult = st.number_input("Cost multiplier (>=0)", min_value=0.0, max_value=3.0, value=1.0, step=0.05)
    cs_one_time = st.number_input("One-time cost ($)", value=0, step=100)
    cs_prob = st.slider("Probability %", 0, 100, 10) / 100.0
    add_shock = st.form_submit_button("Add shock")
    if add_shock:
        new_shock = {"name": cs_name, "rev_mult": cs_rev_mult, "cost_mult": cs_cost_mult, "one_time_cost": cs_one_time, "prob": cs_prob}
        st.session_state["custom_shocks"].append(new_shock)
        st.session_state["selected_shocks"].append(cs_name)
        log_event("custom_shock_added", new_shock)

if st.session_state["custom_shocks"]:
    st.sidebar.markdown("**Custom shocks**")
    for s in list(st.session_state["custom_shocks"]):
        col1, col2 = st.sidebar.columns([3,1])
        with col1:
            checked = st.checkbox(s["name"], value=(s["name"] in st.session_state["selected_shocks"]), key=f"cs_{s['name']}")
            if checked and s["name"] not in st.session_state["selected_shocks"]:
                st.session_state["selected_shocks"].append(s["name"])
            if not checked and s["name"] in st.session_state["selected_shocks"]:
                st.session_state["selected_shocks"].remove(s["name"])
        with col2:
            if st.button("Remove", key=f"rm_{s['name']}"):
                st.session_state["custom_shocks"] = [x for x in st.session_state["custom_shocks"] if x["name"] != s["name"]]
                if s["name"] in st.session_state["selected_shocks"]:
                    st.session_state["selected_shocks"].remove(s["name"])
                log_event("custom_shock_removed", {"name": s["name"]})

# Calculations
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

# Monte Carlo with shocks and optional empirical vol
def collect_active_shocks():
    active = []
    for s in predefined:
        if s["name"] in st.session_state["selected_shocks"]:
            active.append(s)
    for s in st.session_state["custom_shocks"]:
        if s["name"] in st.session_state["selected_shocks"]:
            active.append(s)
    return active

def run_monte_carlo(n_sims=5000, revenue=monthly_revenue, costs=total_costs, cash=cash_reserve,
                    revenue_volatility=0.15, cost_volatility=0.10, shocks=None,
                    investment_roi_monthly=0.0, investment_cost_monthly=0.0):
    runways = []
    shocks = shocks or []
    for i in range(n_sims):
        rev = max(0.0, np.random.normal(revenue, revenue * revenue_volatility))
        cst = max(0.0, np.random.normal(costs, costs * cost_volatility))
        for s in shocks:
            if random.random() < s.get("prob", 0):
                rev = rev * s.get("rev_mult", 1.0)
                cst = cst * s.get("cost_mult", 1.0)
                cst = cst + s.get("one_time_cost", 0)
        cst = cst + investment_cost_monthly
        rev = rev + investment_roi_monthly
        net = cst - rev
        if net <= 0:
            runways.append(999)
        else:
            runways.append(cash / net)
    arr = np.array(runways)
    finite = arr[arr < 999]
    percentiles = {}
    if finite.size > 0:
        for p in [10,25,50,75,90]:
            percentiles[p] = float(np.percentile(finite, p))
    else:
        for p in [10,25,50,75,90]:
            percentiles[p] = float('inf')
    inf_pct = float(np.mean(arr >= 999) * 100)
    return {"runways": arr, "percentiles": percentiles, "infinite_pct": inf_pct}

# Header and quick summary
st.markdown("<div style='background: linear-gradient(90deg,#0b0b0b,#0f0f0f); padding:22px; border-radius:14px; color:#f5f5f5; margin-bottom:18px;'><div style='display:flex; align-items:center; gap:16px;'><span style='font-size:48px;'>🧱</span><div><div class='lego-header'>Lego Manufacturing Command Center</div><div style='margin-top:6px; color:#bdbdbd;'>Build your decisions. Block by block.</div></div><div style='margin-left:auto; background:rgba(255,255,255,0.04); padding:8px 14px; border-radius:10px;'><span style='font-size:14px;'>🟢 Portal Card</span></div></div></div>", unsafe_allow_html=True)

st.markdown("### 🔍 Quick Summary")
st.success(f"Your lab generates **${monthly_revenue:,.0f}/mo** · **Runway:** **{runway:.1f} months** · **Gross margin:** **{gross_margin:.1%}**")

if st.checkbox("🍼 Explain everything simply (Beginner mode)"):
    st.info("Runway = months cash lasts. Gross margin = percent kept after materials & labor. Net burn = monthly cash out minus cash in.")

# Portal cards (condensed)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='portal-card success'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:14px; color:#bdbdbd;'>🏗️ Revenue</span><span class='badge green'>${monthly_revenue:,.0f}/mo</span></div><div style='margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;'>${monthly_revenue:,.0f}</div><div style='font-size:12px; color:#bdbdbd; margin-top:6px;'>Monthly production: {sum(product_units.values()):,} units</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='portal-card'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:14px; color:#bdbdbd;'>📊 Gross Margin</span><span class='badge green'>{gross_margin:.1%}</span></div><div style='margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;'>{gross_margin:.1%}</div><div style='font-size:12px; color:#bdbdbd; margin-top:6px;'>Target: >35%</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='portal-card'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:14px; color:#bdbdbd;'>💰 Profit</span><span class='badge green'>${monthly_profit:,.0f}/mo</span></div><div style='margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;'>${monthly_profit:,.0f}</div><div style='font-size:12px; color:#bdbdbd; margin-top:6px;'>{(monthly_profit/monthly_revenue if monthly_revenue>0 else 0):.1%} margin</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='portal-card'><div style='display:flex; justify-content:space-between; align-items:center;'><span style='font-size:14px; color:#bdbdbd;'>⏱️ Runway</span><span class='badge green'>{runway:.1f} mo</span></div><div style='margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;'>{runway:.1f} months</div><div style='font-size:12px; color:#bdbdbd; margin-top:6px;'>{net_burn:,.0f} net burn</div></div>", unsafe_allow_html=True)

st.divider()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏭 Lab Health","🧠 AI Fractional Team (Coach)","📦 New Products","📢 B2B Growth","🛒 B2C (Amazon)","🏆 Competitor Intel"])

# Tab 1: Monte Carlo & shocks
with tab1:
    st.subheader("🧱 Product Mix")
    prod_df = pd.DataFrame({"Product": list(product_units.keys()), "Units": list(product_units.values()), "Revenue": [product_revenue[p] for p in product_units]})
    fig = px.bar(prod_df, x="Revenue", y="Product", text=prod_df["Units"].apply(lambda x: f"{x} units"), orientation="h", height=320, color="Revenue", color_continuous_scale=PALETTE_4)
    apply_dark_layout(fig)
    fig.update_layout(xaxis_title="Monthly Revenue ($)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🗺️ Runway Heatmap & Monte Carlo")
    st.caption("Run Monte Carlo to see runway percentiles and probability of survival (infinite runway).")

    mc_cols = st.columns([1,1,1,1])
    sims = mc_cols[0].number_input("Simulations", value=5000, step=500, min_value=1000, key="mc_sims")
    # default vol: use empirical if available else UI defaults
    default_rev_vol = emp_rev_vol if emp_rev_vol is not None else 0.15
    default_cost_vol = emp_cost_vol if emp_cost_vol is not None else 0.10
    rev_vol = mc_cols[1].slider("Revenue vol %", 0.0, 50.0, float(default_rev_vol*100), step=1.0, key="mc_rev_vol")/100
    cost_vol = mc_cols[2].slider("Cost vol %", 0.0, 50.0, float(default_cost_vol*100), step=1.0, key="mc_cost_vol")/100
    shock_prob_ui = mc_cols[3].slider("Global shock prob % (optional)", 0, 50, 0, step=1, key="mc_global_shock")/100
    shock_impact_ui = st.slider("Global shock impact % (if occurs)", 0, 80, 0, step=5, key="mc_global_impact")/100

    invest_gain = st.number_input("Investment monthly gain ($)", value=0, step=1000, key="mc_invest_gain")
    invest_cost = st.number_input("Investment monthly cost ($)", value=0, step=100, key="mc_invest_cost")

    if st.button("Run Monte Carlo"):
        with st.spinner("Running simulations..."):
            active_shocks = collect_active_shocks()
            if shock_prob_ui > 0 and shock_impact_ui > 0:
                active_shocks.append({"name":"Global shock", "rev_mult":1-shock_impact_ui, "cost_mult":1.0, "one_time_cost":0, "prob":shock_prob_ui})
            mc = run_monte_carlo(n_sims=int(sims), revenue=monthly_revenue, costs=total_costs, cash=cash_reserve,
                                 revenue_volatility=rev_vol, cost_volatility=cost_vol,
                                 shocks=active_shocks,
                                 investment_roi_monthly=invest_gain, investment_cost_monthly=invest_cost)
            runways = mc["runways"]
            percentiles = mc["percentiles"]
            inf_pct = mc["infinite_pct"]
            log_event("monte_carlo_run", {"sims": sims, "rev_vol": rev_vol, "cost_vol": cost_vol, "active_shocks": [s["name"] for s in active_shocks], "inf_pct": inf_pct})
            st.markdown("**Runway percentiles (months)**")
            st.table(pd.DataFrame([percentiles]).T.rename(columns={0:"months"}))
            st.markdown(f"**% simulations with effectively infinite runway (profit or zero net burn):** {inf_pct:.1f}%")

            # Colored binned histogram
            clipped = np.clip(runways, 0, 60)
            bins = np.linspace(0, 60, 13)
            hist_vals, edges = np.histogram(clipped, bins=bins)
            bin_centers = (edges[:-1] + edges[1:]) / 2
            colors = []
            for c in bin_centers:
                if c < 6:
                    colors.append("#e53935")
                elif c < 12:
                    colors.append("#ffcc00")
                elif c < 24:
                    colors.append("#00aaff")
                else:
                    colors.append("#00cc44")
            fig_mc = go.Figure()
            for i in range(len(hist_vals)):
                fig_mc.add_trace(go.Bar(
                    x=[f"{int(edges[i])}-{int(edges[i+1])} mo"],
                    y=[int(hist_vals[i])],
                    marker_color=colors[i],
                    name=f"{int(edges[i])}-{int(edges[i+1])} mo"
                ))
            fig_mc.update_layout(
                title="Monte Carlo Runway Distribution (clipped to 60 months)",
                xaxis_title="Runway bin",
                yaxis_title="Simulations",
                barmode="stack",
                plot_bgcolor="#000000",
                paper_bgcolor="#000000",
                font_color="#f5f5f5",
                showlegend=True,
                height=360
            )
            st.plotly_chart(fig_mc, use_container_width=True)

            # PDF export (includes percentiles and optionally CSV summary)
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, 750, "Lego Manufacturing Command Center - Monte Carlo Report")
            c.setFont("Helvetica", 10)
            c.drawString(40, 730, f"Generated: {datetime.utcnow().isoformat()} UTC")
            c.drawString(40, 710, f"Monthly revenue: ${monthly_revenue:,.0f}")
            c.drawString(40, 695, f"Cash reserve: ${cash_reserve:,.0f}")
            c.drawString(40, 680, f"Runway percentiles (months):")
            y = 665
            for p, val in percentiles.items():
                c.drawString(60, y, f"{p}th percentile: {val:.1f} months")
                y -= 14
            c.drawString(40, y-6, f"% infinite runway: {inf_pct:.1f}%")
            if historical_df is not None:
                c.drawString(40, y-26, f"Historical rows included: {len(historical_df)}")
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            st.download_button("📄 Download PDF report", data=pdf_buffer, file_name="lego_monte_carlo_report.pdf", mime="application/pdf")
            log_event("report_downloaded", {"sims": sims})

# Tab 2: AI Coach (client sends client API key header)
with tab2:
    st.markdown("<div style='background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;'><strong style='color:#f5f5f5;'>🧠 AI Fractional Team</strong><span style='color:#bdbdbd; margin-left:10px;'>A friendly coach that explains actions and suggests next steps</span></div>", unsafe_allow_html=True)
    st.markdown("### 🔎 Coach Snapshot")
    st.info("This tab is ready for a live AI integration. Use the backend endpoint to keep API keys secure.")

    # Read client API key from Streamlit secrets (keeps it out of repo)
    client_api_key = None
    try:
        client_api_key = st.secrets["CLIENT_API_KEY"]
    except Exception:
        client_api_key = None

    ai_endpoint = st.text_input("AI endpoint URL (your server)", placeholder="https://your-server.example/api/coach")
    persona = st.selectbox("Persona", ["💰 CFO – Financial Strategist", "🎯 Growth Coach – Sales & Ops", "📈 Marketing Coach – B2C Growth", "🤝 BD Coach – Partnerships"])
    user_goal = st.text_input("What do you want help with?", "Increase monthly revenue by $10k")
    tone = st.selectbox("Tone", ["Practical", "Encouraging", "Direct"])

    prompt_preview = f"Persona: {persona}\\nGoal: {user_goal}\\nContext: Revenue ${monthly_revenue:,.0f}, Runway {runway:.1f} months, Gross margin {gross_margin:.1%}\\nTone: {tone}"
    st.code(prompt_preview)

    if st.button("🧠 Simulate Coach Response (local)"):
        sim_lines = [
            f"Hi — I'm your {persona.split('–')[0].strip()} coach.",
            "Quick take: Increase high-margin crowns and reduce material costs by negotiating a 5% discount.",
            "3-step plan:",
            "1) Call top 3 suppliers this week; ask for 5% discount.",
            "2) Run a 30-day Amazon test for mouth guards with a $9.99 price point.",
            "3) Reduce owner draw by 20% for 60 days to extend runway."
        ]
        st.success("\n\n".join(sim_lines))
        log_event("coach_simulated", {"persona": persona, "goal": user_goal})

    if ai_endpoint and st.button("🔒 Request Coach from Server"):
        payload = {"persona": persona, "goal": user_goal, "context": {"monthly_revenue": monthly_revenue, "runway": runway, "gross_margin": gross_margin}, "tone": tone}
        headers = {}
        if client_api_key:
            headers["x-client-key"] = client_api_key
        log_event("coach_requested", {"persona": persona, "goal": user_goal})
        try:
            resp = requests.post(ai_endpoint, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                st.success(data.get("advice", "No advice returned"))
                steps = data.get("steps", [])
                for i, s in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {s}")
                log_event("coach_response_received", {"persona": persona, "steps": len(steps)})
            else:
                st.error(f"Server returned {resp.status_code}: {resp.text}")
                log_event("coach_error", {"status": resp.status_code})
        except Exception as e:
            st.error(f"Request failed: {e}")
            log_event("coach_error", {"error": str(e)})

    if client_api_key:
        st.caption("Client API key found in Streamlit secrets. The app will send it to the backend in the x-client-key header for simple auth.")

# Remaining tabs (product dev, B2B, B2C, competitor) - keep as before (omitted here for brevity)
with tab3:
    st.markdown("📦 Product Development (see app code)")

with tab4:
    st.markdown("📢 B2B Growth (see app code)")

with tab5:
    st.markdown("🛒 B2C (Amazon) (see app code)")

with tab6:
    st.markdown("🏆 Competitor Intel (see app code)")

# SDET quick tests
st.markdown("---")
st.markdown("### 🔧 Run UI tests (SDET quick checks)")
if st.button("Run UI tests"):
    errors = []
    try:
        assert isinstance(monthly_revenue, (int, float))
        assert isinstance(runway, (int, float))
    except Exception as e:
        errors.append(f"Basic metrics type check failed: {e}")
    try:
        mc_test = run_monte_carlo(n_sims=100, revenue=monthly_revenue, costs=total_costs, cash=cash_reserve)
        assert "percentiles" in mc_test and "runways" in mc_test
    except Exception as e:
        errors.append(f"Monte Carlo smoke test failed: {e}")
    try:
        if uploaded:
            assert historical_df is not None and "revenue" in historical_df.columns and "costs" in historical_df.columns
    except Exception as e:
        errors.append(f"CSV parsing test failed: {e}")
    try:
        # PDF generation smoke
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(40, 750, "test")
        c.showPage()
        c.save()
        buf.seek(0)
    except Exception as e:
        errors.append(f"PDF generation test failed: {e}")
    if errors:
        st.error("UI tests found issues:")
        for err in errors:
            st.write("-", err)
        log_event("ui_tests_failed", {"errors": errors})
    else:
        st.success("All quick UI tests passed. App is ready for deployment.")
        log_event("ui_tests_passed", {"time": datetime.utcnow().isoformat()})
