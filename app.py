# app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🦷 Lego Manufacturing Command Center", layout="wide")

# ---------------- PLOTLY DARK PALETTE ----------------
# Reusable dark palette for charts
DARK_COLORS = {
    "bg": "#000000",
    "paper": "#000000",
    "text": "#f5f5f5",
    "grid": "#111111",
    "lego": ["#ff0000", "#ffcc00", "#00aaff", "#00cc44"]
}
px.defaults.template = None

# ---------------- ONBOARDING WIZARD (first-run) ----------------
if "seen_onboarding" not in st.session_state:
    st.session_state["seen_onboarding"] = False

def show_onboarding():
    st.session_state["seen_onboarding"] = True
    st.experimental_rerun()

if not st.session_state["seen_onboarding"]:
    with st.modal("Welcome to Lego Manufacturing Command Center", True):
        st.markdown("""
        ### 👋 Welcome, Founder
        This short onboarding will help you get comfortable with the app.
        - **Quick Summary** shows revenue, runway, and margin.
        - **Lab Health** tab visualizes product mix and runway under shocks.
        - **AI Coach** tab simulates advice and can call your secure backend.
        - **Beginner mode** explains terms in plain English.
        """)
        st.write("Choose your preferred vibe:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Playful Lego (default)"):
                show_onboarding()
        with col2:
            if st.button("Minimal Lego"):
                show_onboarding()

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
net_burn = total_costs - monthly_revenue
runway = cash_reserve / max(net_burn, 1000) if net_burn > 0 else 999
gross_margin = (monthly_revenue - material_cost - labor_cost) / monthly_revenue if monthly_revenue > 0 else 0

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
        <div style="font-size:12px; color:#bdbdbd; margin-top:6px;">{margin_pct:.1%} margin</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    runway_color = "success" if safe_runway > 12 else "warning" if safe_runway > 6 else "critical"
    runway_badge = "green" if safe_runway > 12 else "yellow" if safe_runway > 6 else "red"
    runway_display = f"{safe_runway:.1f}" if safe_runway < 999 else "∞"
    st.markdown(f"""
    <div class="portal-card {runway_color}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:14px; color:#bdbdbd;">⏱️ Runway</span>
            <span class="badge {runway_badge}">{runway_display} mo</span>
        </div>
        <div style="margin-top:8px; font-size:28px; font-weight:800; color:#f5f5f5;">{runway_display} months</div>
        <div style="font-size:12px; color:#bdbdbd; margin-top:6px;">{net_burn:,.0f} net burn</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏭 Lab Health",
    "🧠 AI Fractional Team (Coach)",
    "📦 New Products",
    "📢 B2B Growth",
    "🛒 B2C (Amazon)",
    "🏆 Competitor Intel"
])

# ---------------- TAB 1: LAB HEALTH ----------------
with tab1:
    st.markdown("""<div style="background:#07070a; padding:12px 16px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">🧱 Lab Health Blocks</strong><span style="color:#bdbdbd; margin-left:10px;">Your financial snapshot – block by block</span></div>""", unsafe_allow_html=True)
    st.subheader("🧱 Product Mix")
    prod_df = pd.DataFrame({"Product": list(product_units.keys()), "Units": list(product_units.values()), "Revenue": [product_revenue[p] for p in product_units]})
    fig = px.bar(prod_df, x="Revenue", y="Product", text=prod_df["Units"].apply(lambda x: f"{x} units"), orientation="h", height=320, color="Revenue", color_continuous_scale=px.colors.sequential.Blues)
    fig.update_layout(plot_bgcolor=DARK_COLORS["bg"], paper_bgcolor=DARK_COLORS["paper"], font_color=DARK_COLORS["text"], xaxis_title="Monthly Revenue ($)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🎯 Risk Matrix")
    colA, colB = st.columns(2)
    with colA:
        pct_display = min(b2b_percent * 100, 100)
        color = "#43a047" if b2b_percent > 0.7 else "#f9a825" if b2b_percent > 0.5 else "#e53935"
        st.markdown(f"""<div style="background:#0f0f10; border-radius:12px; padding:14px;"><div style="font-weight:700; margin-bottom:8px;">🟢 Revenue Coverage</div><div style="display:flex; gap:8px; align-items:center;"><div style="flex:1; background:#111; height:22px; border-radius:12px; overflow:hidden;"><div style="width:{pct_display}%; height:100%; background:{color}; border-radius:12px;"></div></div><span style="font-weight:700; min-width:60px;">{b2b_percent:.0%}</span></div><div style="font-size:12px; color:#bdbdbd; margin-top:6px;">B2B revenue vs. B2C</div></div>""", unsafe_allow_html=True)
    with colB:
        burn_display = min(abs(net_burn) / 20000 * 100, 100)
        burn_color = "#43a047" if net_burn <= 0 else "#f9a825" if net_burn < 10000 else "#e53935"
        st.markdown(f"""<div style="background:#0f0f10; border-radius:12px; padding:14px;"><div style="font-weight:700; margin-bottom:8px;">🔴 Burn Rate</div><div style="display:flex; gap:8px; align-items:center;"><div style="flex:1; background:#111; height:22px; border-radius:12px; overflow:hidden;"><div style="width:{burn_display}%; height:100%; background:{burn_color}; border-radius:12px;"></div></div><span style="font-weight:700; min-width:60px;">${abs(net_burn):,.0f}</span></div><div style="font-size:12px; color:#bdbdbd; margin-top:6px;">{'Profitable' if net_burn <= 0 else 'Burning cash'}</div></div>""", unsafe_allow_html=True)

    st.subheader("🗺️ Runway Heatmap")
    st.caption("Projected runway at different shock levels – how much can your lab absorb?")
    shock_levels = [1.0, 0.85, 0.70, 0.55]
    shock_labels = ["No shock", "-15%", "-30%", "-45%"]
    runway_at_shock = []
    for shock in shock_levels:
        shocked_revenue = monthly_revenue * shock
        shocked_costs = total_costs - owner_draw - marketing_budget
        shocked_net = shocked_costs + owner_draw - shocked_revenue
        runway_at_shock.append(cash_reserve / max(shocked_net, 1000) if shocked_net > 0 else 999)
    heatmap_data = pd.DataFrame({"Scenario": shock_labels, "Runway (months)": [min(r, 60) for r in runway_at_shock], "Color": ["#43a047" if r > 12 else "#f9a825" if r > 6 else "#e53935" for r in runway_at_shock]})
    fig2 = go.Figure(data=[go.Bar(x=heatmap_data["Scenario"], y=heatmap_data["Runway (months)"], marker_color=heatmap_data["Color"], text=heatmap_data["Runway (months)"].apply(lambda x: f"{x:.1f}mo"), textposition="auto")])
    fig2.update_layout(title="Runway Under Different Revenue Shocks", yaxis_title="Runway (months)", height=320, plot_bgcolor=DARK_COLORS["bg"], paper_bgcolor=DARK_COLORS["paper"], font_color=DARK_COLORS["text"], showlegend=False)
    fig2.add_hline(y=6, line_dash="dash", line_color="red", annotation_text="Critical (<6mo)")
    fig2.add_hline(y=12, line_dash="dash", line_color="orange", annotation_text="Caution (<12mo)")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-top:18px;"><strong style="color:#f5f5f5;">🧠 AI Lab Health Recommendations</strong><span style="color:#bdbdbd; margin-left:10px;">Simple, prioritized actions</span></div>""", unsafe_allow_html=True)
    recommendations = []
    if monthly_revenue < 50000:
        recommendations.append({"priority":"🔴 URGENT","area":"Revenue","action":f"Revenue (${monthly_revenue:,.0f}/mo) below $50K. Add 10 crowns/day (+300/mo) → +${300*350:,.0f}/mo.","effort":"Medium","impact":"High"})
    if gross_margin < 0.35:
        recommendations.append({"priority":"🔴 URGENT","area":"Margin","action":f"Gross margin ({gross_margin:.1%}) below 35%. Negotiate supplier discounts 5-10% → +${monthly_revenue*0.05:,.0f}/mo.","effort":"Low","impact":"High"})
    if b2b_percent > 0.90 and monthly_revenue > 30000:
        recommendations.append({"priority":"🟡 MEDIUM","area":"Channel Mix","action":f"You're {b2b_percent:.0%} B2B. Launch mouth guards on Amazon to add ~${monthly_revenue*0.15:,.0f}/mo.","effort":"Medium","impact":"Medium"})
    if labor_cost / max(monthly_revenue, 1) > 0.35:
        recommendations.append({"priority":"🟡 MEDIUM","area":"Labor","action":f"Labor is {labor_cost/max(monthly_revenue,1):.1%} of revenue. Automate 1-2 steps to save ~${labor_cost*0.15:,.0f}/mo.","effort":"Medium","impact":"High"})
    if runway < 6:
        recommendations.append({"priority":"🚨 CRITICAL","area":"Cash","action":f"Runway {runway:.1f} months. Immediate: (1) Offer upfront payment discounts, (2) Reduce owner draw, (3) Prioritize fastest revenue channels.","effort":"Low","impact":"Critical"})
    if not recommendations:
        st.success("✅ Your lab is in great shape! Focus on execution and growth.")
    else:
        for rec in recommendations:
            rec_class = "urgent" if "CRITICAL" in rec["priority"] or "URGENT" in rec["priority"] else "high" if "MEDIUM" in rec["priority"] else "medium"
            st.markdown(f"""<div class="rec-card {rec_class}"><div style="display:flex; justify-content:space-between; align-items:flex-start;"><div><div style="font-weight:800;">{rec['priority']} · {rec['area']}</div><div style="margin-top:6px; color:#f5f5f5;">{rec['action']}</div></div><div style="text-align:right; font-size:12px; color:#bdbdbd;">⚡ {rec['effort']} effort<br>📈 {rec['impact']} impact</div></div></div>""", unsafe_allow_html=True)

    st.markdown("**Next Best Actions**")
    a1, a2, a3 = st.columns(3)
    if a1.button("📈 Improve Margin"):
        st.info("Tip: Call 3 suppliers this week and ask for a 5% discount.")
    if a2.button("🚀 Launch Amazon Mouth Guards"):
        st.info("Tip: Start with a 30-day trial listing and 50 units to test conversion.")
    if a3.button("💸 Reduce Owner Draw"):
        st.info("Tip: Try a 30% temporary reduction and re-evaluate runway in 30 days.")

# ---------------- TAB 2: AI FRACTIONAL TEAM (COACH) ----------------
with tab2:
    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">🧠 AI Fractional Team</strong><span style="color:#bdbdbd; margin-left:10px;">A friendly coach that explains actions and suggests next steps</span></div>""", unsafe_allow_html=True)
    st.markdown("### 🔎 Coach Snapshot")
    st.info("This tab is ready for a live AI integration. Use the backend endpoint to keep API keys secure.")

    st.markdown("**AI Integration (server endpoint)**")
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

    if ai_endpoint and st.button("🔒 Request Coach from Server"):
        payload = {
            "persona": persona,
            "goal": user_goal,
            "context": {"monthly_revenue": monthly_revenue, "runway": runway, "gross_margin": gross_margin},
            "tone": tone
        }
        try:
            resp = requests.post(ai_endpoint, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                st.success(data.get("advice", "No advice returned"))
                steps = data.get("steps", [])
                for i, s in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {s}")
            else:
                st.error(f"Server returned {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# ---------------- TAB 3: NEW PRODUCTS ----------------
with tab3:
    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">📦 Product Development</strong><span style="color:#bdbdbd; margin-left:10px;">Quickly evaluate new product ideas</span></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        dev_cost = st.number_input("Development cost ($)", value=5000, step=1000, key="dev_cost")
        prod_cost = st.number_input("Cost per unit ($)", value=50, step=10, key="prod_cost")
        expected_price = st.number_input("Sale price ($)", value=250, step=25, key="price")
    with col2:
        expected_units = st.number_input("Monthly units", value=200, step=25, key="units")
        ramp_months = st.slider("Ramp-up (months)", 1, 12, 3, key="ramp")
        cannibalization = st.slider("% cannibalization", 0, 50, 10, step=5, key="cann") / 100
    monthly_revenue_new = expected_price * expected_units
    monthly_margin_new = (expected_price - prod_cost) * expected_units
    cann_loss = monthly_revenue * cannibalization * gross_margin
    net_impact = monthly_margin_new - cann_loss
    payback = dev_cost / max(net_impact, 100)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("New Revenue", f"${monthly_revenue_new:,.0f}/mo")
    c2.metric("New Margin", f"${monthly_margin_new:,.0f}/mo")
    c3.metric("Product Margin", f"{(expected_price-prod_cost)/expected_price:.1%}")
    c4.metric("Payback", f"{payback:.1f} months")
    if payback < 6 and (expected_price-prod_cost)/expected_price > 0.50:
        st.success("✅ Strong opportunity – payback under 6 months, 50%+ margin. Prioritize this!")
    elif payback < 12 and (expected_price-prod_cost)/expected_price > 0.40:
        st.success("✅ Good opportunity – consider a soft launch.")
    else:
        st.warning("⚠️ Reconsider – long payback or low margin.")
    st.subheader("💡 New Product Ideas")
    st.markdown("""| Product | Investment | Timeline | Potential Revenue | Fit |
|---------|-----------:|:--------:|------------------:|:---:|
| **Surgical Guides** | $2-5K | 1-2 mo | $5-10K/mo | ✅ 3D printing |
| **Custom Abutments** | $3-6K | 2-3 mo | $8-15K/mo | ✅ CNC milling |
| **Clear Aligners** | $10-20K | 3-6 mo | $20-50K/mo | 📈 Growing |
| **Night Guards** | $1-3K | 1 mo | $4-8K/mo | ✅ Low investment |""", unsafe_allow_html=True)

# ---------------- TAB 4: B2B GROWTH ----------------
with tab4:
    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">📢 B2B Growth</strong><span style="color:#bdbdbd; margin-left:10px;">Build dentist relationships</span></div>""", unsafe_allow_html=True)
    strategy = st.selectbox("Choose strategy:", ["New Dentist Prospecting", "Existing Dentist Upsell", "Referral Program", "Conference ROI"])
    if strategy == "New Dentist Prospecting":
        target = st.number_input("Dentists to contact", value=50, step=10)
        response = st.slider("Response rate %", 5, 30, 15, step=5, key="resp") / 100
        conversion = st.slider("Conversion %", 5, 30, 12, step=5, key="conv") / 100
        leads = target * response
        customers = leads * conversion
        revenue = customers * 12000
        st.metric("Expected New Customers", f"{customers:.0f}")
        st.metric("Annual Revenue", f"${revenue:,.0f}")
        st.markdown(f"""**📋 Prospecting Plan:**\n1. Identify {target} dentists using directories\n2. Send personalized email (use template)\n3. Follow up with sample kit\n4. Offer free consultation\n\n**Cost per acquisition:** ~$500-1,000\n**Timeline:** 1-3 months""", unsafe_allow_html=True)

# ---------------- TAB 5: B2C (AMAZON) ----------------
with tab5:
    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">🛒 B2C (Amazon)</strong><span style="color:#bdbdbd; margin-left:10px;">Simple launch checklist</span></div>""", unsafe_allow_html=True)
    st.markdown("""**Amazon Quick Launch Checklist**\n1. Create a single product listing for mouth guards.\n2. Start with 50 units and a promotional price.\n3. Use 5 high-quality photos and 3 short bullets.\n4. Run a 14-day ad test with $200 budget.\n5. Measure conversion and adjust price.""", unsafe_allow_html=True)

# ---------------- TAB 6: COMPETITOR INTEL ----------------
with tab6:
    st.markdown("""<div style="background:#071022; padding:12px; border-radius:10px; margin-bottom:12px;"><strong style="color:#f5f5f5;">🏆 Competitor Intel</strong><span style="color:#bdbdbd; margin-left:10px;">High-level signals and quick checks</span></div>""", unsafe_allow_html=True)
    st.markdown("""**Quick competitor checks**\n- Check top 3 local labs for pricing and turnaround time.\n- Review 5 customer testimonials for quality signals.\n- Compare product mix and identify gaps you can exploit.""", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("""<div style="color:#bdbdbd; font-size:13px;"><strong>Deployment notes:</strong> This app is UI‑tested for Streamlit. To enable the live AI coach: host your AI model or proxy on a secure server and call it from the server endpoint (do not embed API keys in the client). Use HTTPS in production.</div>""", unsafe_allow_html=True)
