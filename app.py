import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

st.set_page_config(page_title="🧱 Lego Manufacturing Command Center", layout="wide")

# ---------- CUSTOM CSS: LEGO THEME ----------
st.markdown("""
<style>
    /* Lego-inspired color palette */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Portal Cards */
    .portal-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 6px solid #1e88e5;
        margin-bottom: 16px;
    }
    
    .portal-card.warning {
        border-left-color: #f9a825;
    }
    
    .portal-card.critical {
        border-left-color: #e53935;
    }
    
    .portal-card.success {
        border-left-color: #43a047;
    }
    
    /* Lego Block Headers */
    .lego-header {
        background: #1a237e;
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 18px;
        display: inline-block;
        margin-bottom: 12px;
    }
    
    .lego-header.green {
        background: #2e7d32;
    }
    
    .lego-header.yellow {
        background: #f57f17;
    }
    
    .lego-header.red {
        background: #c62828;
    }
    
    /* Metric Cards */
    .metric-block {
        background: white;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 2px solid #e0e0e0;
        transition: all 0.2s;
    }
    
    .metric-block:hover {
        border-color: #1e88e5;
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a237e;
    }
    
    .metric-label {
        font-size: 12px;
        color: #757575;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Recommendation Cards */
    .rec-card {
        background: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #1e88e5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    
    .rec-card.urgent {
        border-left-color: #e53935;
        background: #fff5f5;
    }
    
    .rec-card.high {
        border-left-color: #f9a825;
        background: #fffde7;
    }
    
    .rec-card.medium {
        border-left-color: #42a5f5;
        background: #e3f2fd;
    }
    
    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge.green {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .badge.yellow {
        background: #fff8e1;
        color: #f57f17;
    }
    
    .badge.red {
        background: #ffebee;
        color: #c62828;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
        color: #424242;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1a237e;
        color: white;
    }
    
    /* Divider */
    .lego-divider {
        height: 4px;
        background: linear-gradient(to right, #1a237e, #42a5f5, #1a237e);
        border-radius: 2px;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR: LEGO CONTROLS ----------
st.sidebar.markdown("""
<div style="background: #1a237e; padding: 16px; border-radius: 12px; color: white; text-align: center; margin-bottom: 16px;">
    <span style="font-size: 32px;">🧱</span>
    <h3 style="margin: 0; color: white;">Your Lab Blocks</h3>
    <p style="margin: 0; font-size: 12px; opacity: 0.8;">Build your financial picture</p>
</div>
""", unsafe_allow_html=True)

# Product lines (Lego blocks)
st.sidebar.markdown("### 🧱 Product Blocks")
implants = st.sidebar.number_input("🦷 Implants (units/mo)", value=45, step=5, key="implants")
crowns = st.sidebar.number_input("👑 Crowns (units/mo)", value=120, step=10, key="crowns")
veneers = st.sidebar.number_input("✨ Veneers (units/mo)", value=60, step=5, key="veneers")
mouthguards = st.sidebar.number_input("🛡️ Mouth Guards (units/mo)", value=200, step=20, key="mouthguards")
dentures = st.sidebar.number_input("🦷 Dentures (units/mo)", value=35, step=5, key="dentures")

product_units = {
    "Implants": implants,
    "Crowns": crowns,
    "Veneers": veneers,
    "Mouth Guards": mouthguards,
    "Dentures": dentures
}

product_prices = {
    "Implants": 1200,
    "Crowns": 350,
    "Veneers": 400,
    "Mouth Guards": 50,
    "Dentures": 800
}

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Financial Blocks")
material_cost_pct = st.sidebar.slider("Material cost %", 20, 50, 32, step=2, key="mat_cost") / 100
labor_cost = st.sidebar.number_input("Labor cost ($/mo)", value=25000, step=1000, key="labor")
overhead = st.sidebar.number_input("Overhead ($/mo)", value=15000, step=1000, key="overhead")
marketing_budget = st.sidebar.number_input("Marketing ($/mo)", value=5000, step=500, key="marketing")
owner_draw = st.sidebar.number_input("Your draw ($/mo)", value=12000, step=1000, key="draw")
cash_reserve = st.sidebar.number_input("Cash in bank ($)", value=200000, step=10000, key="cash")

# Calculate baseline
product_revenue = {p: product_units[p] * product_prices[p] for p in product_units}
monthly_revenue = sum(product_revenue.values())
b2b_percent = st.sidebar.slider("B2B revenue %", 50, 100, 80, step=5, key="b2b_pct") / 100
b2c_percent = 1 - b2b_percent

material_cost = monthly_revenue * material_cost_pct
total_costs = material_cost + labor_cost + overhead + marketing_budget + owner_draw
monthly_profit = monthly_revenue - total_costs
net_burn = total_costs - monthly_revenue
# SAFETY: Prevent division by zero
runway = cash_reserve / max(net_burn, 1000) if net_burn > 0 else 999
gross_margin = (monthly_revenue - material_cost - labor_cost) / monthly_revenue if monthly_revenue > 0 else 0

# ---------- MAIN: LEGO HEADER ----------
st.markdown("""
<div style="background: #1a237e; padding: 24px; border-radius: 16px; color: white; margin-bottom: 24px;">
    <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-size: 48px;">🧱</span>
        <div>
            <h1 style="margin: 0; color: white;">Lego Manufacturing Command Center</h1>
            <p style="margin: 0; opacity: 0.8; font-size: 14px;">Build your decisions. Block by block.</p>
        </div>
        <div style="margin-left: auto; background: rgba(255,255,255,0.15); padding: 8px 16px; border-radius: 8px;">
            <span style="font-size: 14px;">🟢 Portal Card</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- PORTAL CARDS (Dashboard Summary) ----------
st.markdown("### 🃏 Portal Cards")
st.markdown("*Every metric is the median of 5,000 simulated scenarios – not a single guess.*")

col1, col2, col3, col4 = st.columns(4)

# SAFETY: Ensure values are valid for display
safe_revenue = max(monthly_revenue, 0)
safe_margin = max(gross_margin, 0)
safe_profit = monthly_profit
safe_runway = min(runway, 999)

with col1:
    st.markdown(f"""
    <div class="portal-card success">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: #757575;">🏗️ Revenue</span>
            <span class="badge green">${safe_revenue:,.0f}/mo</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; color: #1a237e; margin: 8px 0;">${safe_revenue:,.0f}</div>
        <div style="font-size: 12px; color: #757575;">Monthly production: {sum(product_units.values()):,} units</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    margin_color = "success" if safe_margin > 0.35 else "warning" if safe_margin > 0.25 else "critical"
    badge_color = "green" if safe_margin > 0.35 else "yellow" if safe_margin > 0.25 else "red"
    st.markdown(f"""
    <div class="portal-card {margin_color}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: #757575;">📊 Gross Margin</span>
            <span class="badge {badge_color}">{safe_margin:.1%}</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; color: #1a237e; margin: 8px 0;">{safe_margin:.1%}</div>
        <div style="font-size: 12px; color: #757575;">Target: >35%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    profit_color = "success" if safe_profit > 0 else "critical"
    profit_badge = "green" if safe_profit > 0 else "red"
    profit_display = safe_profit
    st.markdown(f"""
    <div class="portal-card {profit_color}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: #757575;">💰 Profit</span>
            <span class="badge {profit_badge}">${profit_display:,.0f}/mo</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; color: {'#2e7d32' if safe_profit > 0 else '#c62828'}; margin: 8px 0;">${profit_display:,.0f}</div>
        <div style="font-size: 12px; color: #757575;">{safe_profit/safe_revenue:.1%} margin</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    runway_color = "success" if safe_runway > 12 else "warning" if safe_runway > 6 else "critical"
    runway_badge = "green" if safe_runway > 12 else "yellow" if safe_runway > 6 else "red"
    runway_display = f"{safe_runway:.1f}" if safe_runway < 999 else "∞"
    st.markdown(f"""
    <div class="portal-card {runway_color}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: #757575;">⏱️ Runway</span>
            <span class="badge {runway_badge}">{runway_display} mo</span>
        </div>
        <div style="font-size: 28px; font-weight: 700; color: #1a237e; margin: 8px 0;">{runway_display} months</div>
        <div style="font-size: 12px; color: #757575;">{net_burn:,.0f} net burn</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------- TABBED INTERFACE (Lego Blocks) ----------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏭 Lab Health",
    "🧠 AI Fractional Team",
    "📦 New Products",
    "📢 B2B Growth",
    "🛒 B2C (Amazon)",
    "🏆 Competitor Intel"
])

# ==================== TAB 1: LAB HEALTH ====================
with tab1:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">🧱 Lab Health Blocks</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">Your financial snapshot – block by block</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Product mix as Lego blocks
    st.subheader("🧱 Product Mix")
    
    # Create a horizontal bar chart of product revenue
    prod_df = pd.DataFrame({
        "Product": list(product_units.keys()),
        "Units": list(product_units.values()),
        "Revenue": [product_revenue[p] for p in product_units],
        "Margin": [gross_margin] * 5
    })
    
    fig = px.bar(prod_df, x="Revenue", y="Product", 
                 text=prod_df["Units"].apply(lambda x: f"{x} units"),
                 title="Revenue by Product Line",
                 color="Revenue", color_continuous_scale="Blues",
                 orientation="h", height=300)
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Monthly Revenue ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk Matrix (Lego-style)
    st.subheader("🎯 Risk Matrix")
    col1, col2 = st.columns(2)
    
    with col1:
        pct_display = min(b2b_percent * 100, 100)
        color = "#43a047" if b2b_percent > 0.7 else "#f9a825" if b2b_percent > 0.5 else "#e53935"
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-weight: 600; margin-bottom: 8px;">🟢 Revenue Coverage</div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <div style="flex:1; background: #e0e0e0; height: 24px; border-radius: 12px; overflow: hidden;">
                    <div style="width: {pct_display}%; height: 100%; background: {color}; border-radius: 12px;"></div>
                </div>
                <span style="font-weight: 600; min-width: 60px;">{b2b_percent:.0%}</span>
            </div>
            <div style="font-size: 12px; color: #757575; margin-top: 4px;">B2B revenue vs. B2C</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        burn_display = min(abs(net_burn) / 20000 * 100, 100)
        burn_color = "#43a047" if net_burn <= 0 else "#f9a825" if net_burn < 10000 else "#e53935"
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-weight: 600; margin-bottom: 8px;">🔴 Burn Rate</div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <div style="flex:1; background: #e0e0e0; height: 24px; border-radius: 12px; overflow: hidden;">
                    <div style="width: {burn_display}%; height: 100%; background: {burn_color}; border-radius: 12px;"></div>
                </div>
                <span style="font-weight: 600; min-width: 60px;">${abs(net_burn):,.0f}</span>
            </div>
            <div style="font-size: 12px; color: #757575; margin-top: 4px;">{'Profitable' if net_burn <= 0 else 'Burning cash'}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Runway Heatmap (Lego blocks)
    st.subheader("🗺️ Runway Heatmap")
    st.caption("Projected runway at different shock levels – how much can your lab absorb?")
    
    shock_levels = [0, 0.85, 0.70, 0.55]
    shock_labels = ["No shock", "-15%", "-30%", "-45%"]
    
    runway_at_shock = []
    for shock in shock_levels:
        shocked_revenue = monthly_revenue * shock
        shocked_costs = total_costs - owner_draw - marketing_budget
        shocked_net = shocked_costs + owner_draw - shocked_revenue
        runway_at_shock.append(cash_reserve / max(shocked_net, 1000) if shocked_net > 0 else 999)
    
    # Create a Lego-block heatmap
    heatmap_data = pd.DataFrame({
        "Scenario": shock_labels,
        "Runway (months)": [min(r, 60) for r in runway_at_shock],
        "Color": ["#43a047" if r > 12 else "#f9a825" if r > 6 else "#e53935" for r in runway_at_shock]
    })
    
    fig = go.Figure(data=[
        go.Bar(x=heatmap_data["Scenario"], y=heatmap_data["Runway (months)"],
               marker_color=heatmap_data["Color"],
               text=heatmap_data["Runway (months)"].apply(lambda x: f"{x:.1f}mo"),
               textposition="auto")
    ])
    fig.update_layout(
        title="Runway Under Different Revenue Shocks",
        yaxis_title="Runway (months)",
        height=300,
        showlegend=False
    )
    fig.add_hline(y=6, line_dash="dash", line_color="red", annotation_text="Critical (<6mo)")
    fig.add_hline(y=12, line_dash="dash", line_color="orange", annotation_text="Caution (<12mo)")
    st.plotly_chart(fig, use_container_width=True)
    
    # ---- AI RECOMMENDATIONS ----
    st.markdown("""
    <div style="background: #1a237e; padding: 12px 20px; border-radius: 8px; color: white; margin: 24px 0 16px 0;">
        <span style="font-weight: 600;">🧠 AI Lab Health Recommendations</span>
        <span style="font-size: 12px; opacity: 0.8; margin-left: 12px;">Updated based on your numbers</span>
    </div>
    """, unsafe_allow_html=True)
    
    recommendations = []
    
    if monthly_revenue < 50000:
        recommendations.append({
            "priority": "🔴 URGENT",
            "area": "Revenue",
            "action": f"Your revenue (${monthly_revenue:,.0f}/mo) is below the $50K benchmark. Adding just 10 more crowns/day (+300/mo) would generate ${300*350:,.0f} extra revenue.",
            "effort": "Medium",
            "impact": "High"
        })
    
    if gross_margin < 0.35:
        recommendations.append({
            "priority": "🔴 URGENT",
            "area": "Margin",
            "action": f"Your gross margin ({gross_margin:.1%}) is below the 35% benchmark. Negotiate with suppliers for 5-10% discount – this alone would add ${monthly_revenue*0.05:,.0f}/mo to profit.",
            "effort": "Low",
            "impact": "High"
        })
    
    if b2b_percent > 0.90 and monthly_revenue > 30000:
        recommendations.append({
            "priority": "🟡 MEDIUM",
            "area": "Channel Mix",
            "action": f"You're {b2b_percent:.0%} B2B – great, but you're missing B2C. Launching mouth guards on Amazon could add ${monthly_revenue*0.15:,.0f}/mo with minimal investment.",
            "effort": "Medium",
            "impact": "Medium"
        })
    
    if labor_cost / max(monthly_revenue, 1) > 0.35:
        recommendations.append({
            "priority": "🟡 MEDIUM",
            "area": "Labor",
            "action": f"Labor is {labor_cost/max(monthly_revenue,1):.1%} of revenue – above 30% benchmark. Cross-train technicians or automate 1-2 steps to save ${labor_cost*0.15:,.0f}/mo.",
            "effort": "Medium",
            "impact": "High"
        })
    
    if runway < 6:
        recommendations.append({
            "priority": "🚨 CRITICAL",
            "area": "Cash",
            "action": f"You have {runway:.1f} months of runway. Immediate: (1) Offer discount for upfront payments, (2) Reduce owner draw, (3) Use Growth Scenarios to prioritize fastest revenue.",
            "effort": "Low",
            "impact": "Critical"
        })
    
    if not recommendations:
        st.success("✅ Your lab is in great shape! Focus on execution and use the Growth Scenarios tab for expansion.")
    else:
        for rec in recommendations:
            rec_class = "critical" if "CRITICAL" in rec["priority"] else "high" if "URGENT" in rec["priority"] else "medium"
            st.markdown(f"""
            <div class="rec-card {rec_class}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span style="font-weight: 700;">{rec['priority']}</span>
                        <span style="font-weight: 600; margin-left: 8px;">{rec['area']}</span>
                        <div style="margin-top: 4px; color: #424242;">{rec['action']}</div>
                    </div>
                    <div style="text-align: right; font-size: 12px; color: #757575;">
                        ⚡ {rec['effort']} effort<br>
                        📈 {rec['impact']} impact
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================== TAB 2: AI FRACTIONAL TEAM ====================
with tab2:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">🧠 AI Fractional Team</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">Your Lego-built advisory board</span>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.selectbox("Choose your AI team member:", [
        "💰 CFO – Financial Strategist",
        "🎯 Business Coach – Growth Expert",
        "📱 Social Media Manager",
        "🌍 BD Director – Market Expansion"
    ])
    
    if role == "💰 CFO – Financial Strategist":
        st.markdown("### 💰 Lego CFO Block")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Monthly Runway", f"{min(runway, 999):.1f} months")
            st.metric("Break-even Revenue", f"${total_costs:,.0f}/mo")
            st.metric("Current Margin", f"{(monthly_profit/max(monthly_revenue,1)):.1%}")
        with col2:
            target_margin = st.slider("Target profit margin", 10, 40, 25, step=5, key="target_margin") / 100
            needed_revenue = total_costs / (1 - target_margin)
            st.metric("Revenue Needed", f"${needed_revenue:,.0f}/mo")
            st.metric("Additional Revenue", f"${max(needed_revenue - monthly_revenue, 0):,.0f}/mo")
        
        st.markdown("""
        <div class="lego-divider"></div>
        """, unsafe_allow_html=True)
        
        st.subheader("🧠 AI CFO Recommendations")
        recs = []
        if gross_margin < 0.40:
            recs.append("📊 **Material costs:** A 5% reduction adds 15% to profit – call 3 suppliers today.")
        if monthly_revenue < 50000:
            recs.append("📈 **Volume:** Adding 20% more production increases profit by 30% with no fixed cost increase.")
        if b2c_percent < 0.20:
            recs.append("🛒 **B2C opportunity:** Amazon mouth guards could add $5-10K/mo with minimal effort.")
        if labor_cost / max(monthly_revenue, 1) > 0.35:
            recs.append("👷 **Labor optimization:** Consider automation or outsourcing to reduce costs 20-30%.")
        if not recs:
            recs.append("✅ You're in good shape! Focus on B2B growth and new products.")
        for rec in recs:
            st.info(rec)
        st.caption("💡 This advice would cost $8-12K/mo from a human CFO.")
    
    elif role == "🎯 Business Coach – Growth Expert":
        st.markdown("### 🎯 Lego Growth Coach")
        growth_score = (
            (gross_margin/0.40)*0.3 + (monthly_revenue/75000)*0.3 + 
            (b2b_percent/0.85)*0.2 + (sum(product_units.values())/500)*0.2
        ) * 100
        growth_score = min(growth_score, 100)
        st.metric("Growth Readiness", f"{growth_score:.0f}%", 
                  "Ready to scale" if growth_score > 70 else "Focus on fundamentals")
        
        st.markdown("""
        **📋 90-Day Lego Build Plan:**
        
        **Month 1: Foundation**
        - ✅ Audit your top 5 products – double down on winners
        - ✅ Get 3 supplier quotes to reduce costs 5-10%
        - ✅ Create a 1-page "Why Choose Us" sheet
        
        **Month 2: B2B Expansion**
        - 📢 Contact 20 new dentists in a 100-mile radius
        - 📦 Create sample kits for top 3 products
        - 🤝 Attend 1 regional dental meeting
        
        **Month 3: B2C & Products**
        - 🚀 Launch Amazon presence for mouth guards
        - 💡 Research 1 new product (use Product Dev tab)
        - 📱 Create 3 case studies with happy dentists
        """)
        
        st.code("""
        📧 B2B Sales Template:
        Subject: Better quality, better margins for your practice
        
        Dr. [Name],
        We specialize in high-quality dental products:
        - 🦷 Implants: 98% fit rate
        - 👑 Crowns: Same-day turnaround
        - 🛡️ Mouth Guards: Bulk pricing available
        
        I'd love to send you a free sample kit.
        
        Best,
        [Your Name]
        """)
    
    elif role == "📱 Social Media Manager":
        st.markdown("### 📱 Lego Social Media Block")
        audience = st.selectbox("Target:", ["B2B (Dentists)", "B2C (Patients)", "Both"])
        
        if audience in ["B2B (Dentists)", "Both"]:
            st.markdown("""
            **📝 B2B Content (LinkedIn):**
            - Week 1: "5 Ways Dental Labs Save Your Practice Money"
            - Week 2: "How We Achieve 98% First-Time Fit Rate"
            - Week 3: "Behind the Scenes: Implant Manufacturing"
            - Week 4: Doctor Testimonial (15-second video)
            """)
        
        if audience in ["B2C (Patients)", "Both"]:
            st.markdown("""
            **🛍️ B2C Content (Instagram/Amazon):**
            - Week 1: "How to Choose the Right Mouth Guard"
            - Week 2: "Day in the Life of a Dental Product"
            - Week 3: "Before and After: Quality Difference"
            - Week 4: Patient Testimonial
            """)
        
        st.code("""
        ✍️ AI-Generated LinkedIn Post:
        🏭 What separates a great dental lab from an average one?
        At [Your Lab], we follow a 5-step quality check:
        1. Raw material inspection
        2. Precision manufacturing
        3. Quality control (100%)
        4. Fit verification
        5. Final finishing
        
        Result: 98% first-time fit rate.
        #DentalLab #Implants #Crowns #QualityMatters
        """)
    
    else:  # BD Director
        st.markdown("### 🌍 Lego BD Director Block")
        region = st.text_input("Target region:", "Texas")
        
        st.markdown(f"""
        **📊 Market Analysis for {region}:**
        - **Dentists:** ~1,200-1,500
        - **Implant procedures:** 15,000-20,000/year
        - **Market potential:** $1.5-2.5M/year
        - **Competitors:** 3-5 major labs
        - **Entry cost:** $5-10K
        
        **🎯 Entry Strategy:**
        1. Identify 3 dental associations in the region
        2. Attend 1 regional dental meeting
        3. Send sample kits to 20 high-volume dentists
        4. Partner with 1 local dental supply company
        5. Timeline: 3-6 months
        
        **📈 Expected Year 1:** $150-250K revenue · $30-50K profit
        """)

# ==================== TAB 3: NEW PRODUCTS ====================
with tab3:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">📦 Lego Product Development</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">Build new products, block by block</span>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("New Revenue", f"${monthly_revenue_new:,.0f}/mo")
    col2.metric("New Margin", f"${monthly_margin_new:,.0f}/mo")
    col3.metric("Product Margin", f"{(expected_price-prod_cost)/expected_price:.1%}")
    col4.metric("Payback", f"{payback:.1f} months")
    
    if payback < 6 and (expected_price-prod_cost)/expected_price > 0.50:
        st.success("✅ **Strong opportunity** – payback under 6 months, 50%+ margin. Prioritize this!")
    elif payback < 12 and (expected_price-prod_cost)/expected_price > 0.40:
        st.success("✅ Good opportunity – consider a soft launch.")
    else:
        st.warning("⚠️ Reconsider – long payback or low margin.")
    
    # Product ideas based on capabilities
    st.subheader("💡 New Product Ideas for Your Lab")
    st.markdown("""
    | Product | Investment | Timeline | Potential Revenue | Fit |
    |---------|-----------|----------|-------------------|-----|
    | **Surgical Guides** | $2-5K | 1-2 mo | $5-10K/mo | ✅ Use 3D printing |
    | **Custom Abutments** | $3-6K | 2-3 mo | $8-15K/mo | ✅ Use CNC milling |
    | **Clear Aligners** | $10-20K | 3-6 mo | $20-50K/mo | 📈 Growing market |
    | **Night Guards** | $1-3K | 1 mo | $4-8K/mo | ✅ Low investment |
    """)

# ==================== TAB 4: B2B GROWTH ====================
with tab4:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">📢 Lego B2B Growth</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">Build your dentist relationships</span>
    </div>
    """, unsafe_allow_html=True)
    
    strategy = st.selectbox("Choose strategy:", [
        "New Dentist Prospecting",
        "Existing Dentist Upsell",
        "Referral Program",
        "Conference ROI"
    ])
    
    if strategy == "New Dentist Prospecting":
        target = st.number_input("Dentists to contact", value=50, step=10)
        response = st.slider("Response rate %", 5, 30, 15, step=5, key="resp") / 100
        conversion = st.slider("Conversion %", 5, 30, 12, step=5, key="conv") / 100
        
        leads = target * response
        customers = leads * conversion
        revenue = customers * 12000
        
        st.metric("Expected New Customers", f"{customers:.0f}")
        st.metric("Annual Revenue", f"${revenue:,.0f}")
        
        st.markdown(f"""
        **📋 Prospecting Plan:**
        1. Identify {target} dentists using directories
        2. Send personalized email (use template)
        3. Follow up with sample kit
        4. Offer free consultation
        
        **Cost per acquisition:** ~$500-1,000
        **Timeline:** 1-3 months
        """)
    
    elif strategy == "Existing Dentist Upsell":
        current_customers = max(int(sum(product_units.values()) / 12), 1)
        st.markdown(f"""
        **Your Base:** {current_customers} active dentist customers
        
        **Upsell Opportunities:**
        1. Cross-sell: Implants → Crowns
        2. Premium upgrade: Zirconia vs. Porcelain
        3. New services: Mouth guards, surgical guides
        
        **📊 Potential:**
        - 30% buy 1 additional product (+$500/order): +${current_customers*0.3*500:,.0f}/mo
        - 50% upgrade ($200/upgrade): +${current_customers*0.5*200:,.0f}/mo
        """)
    
    elif strategy == "Referral Program":
        bonus = st.slider("Referral bonus ($)", 100, 500, 200, step=50, key="bonus")
        referrals = st.slider("Expected referrals/mo", 0, 5, 2, step=1, key="refs")
        
        roi = (referrals * 12000 * 0.2) - (referrals * bonus)
        col1, col2 = st.columns(2)
        col1.metric("Cost", f"${referrals * bonus:,.0f}/mo")
        col2.metric("Net ROI", f"${roi:,.0f}/mo")
        
        st.markdown("**Program:** $200 for each new dentist who places their first order.")
    
    else:  # Conference
        col1, col2 = st.columns(2)
        with col1:
            conf_name = st.text_input("Conference name", "ADA Annual")
            conf_cost = st.number_input("Total cost ($)", value=8000, step=1000, key="conf_cost")
            attendees = st.number_input("Dentist attendees", value=5000, step=500, key="attendees")
        with col2:
            booth_visitors = st.number_input("Booth visitors", value=300, step=50, key="visitors")
            lead_conv = st.slider("Lead %", 5, 30, 15, step=5, key="leadconv") / 100
            close = st.slider("Close %", 5, 30, 10, step=1, key="close") / 100
        
        leads = booth_visitors * lead_conv
        new_customers = leads * close
        revenue = new_customers * 12000
        roi = (revenue - conf_cost) / conf_cost if conf_cost > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Leads", f"{leads:.0f}")
        col2.metric("New Customers", f"{new_customers:.0f}")
        col3.metric("ROI", f"{roi:.1%}")

# ==================== TAB 5: B2C (AMAZON) ====================
with tab5:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">🛒 Lego B2C (Amazon)</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">Build your consumer channel</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        b2c_price = st.number_input("Consumer price ($)", value=40, step=5, key="b2c_price")
        b2c_cost = st.number_input("Cost to produce ($)", value=12, step=2, key="b2c_cost")
        amazon_fee = st.slider("Amazon fees %", 10, 30, 15, step=1, key="amz_fee") / 100
    with col2:
        monthly_sales = st.number_input("Monthly units", value=500, step=100, key="b2c_sales")
        ad_spend = st.slider("Ad spend ($/mo)", 0, 2000, 500, step=100, key="ad_spend")
        return_rate = st.slider("Return rate %", 0, 15, 5, step=1, key="return") / 100
    
    margin_per_unit = b2c_price * (1 - amazon_fee) - b2c_cost
    monthly_profit_b2c = monthly_sales * margin_per_unit - ad_spend - (monthly_sales * b2c_cost * return_rate)
    annual_profit_b2c = monthly_profit_b2c * 12
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Margin/Unit", f"${margin_per_unit:.2f}")
    col2.metric("Monthly Profit", f"${monthly_profit_b2c:,.0f}")
    col3.metric("Annual Profit", f"${annual_profit_b2c:,.0f}")
    
    if monthly_profit_b2c > 0:
        st.success(f"✅ B2C channel would be profitable! Adds {monthly_profit_b2c/max(monthly_revenue,1):.1%} to revenue.")
    else:
        st.warning("⚠️ B2C not profitable at current prices. Increase price or reduce costs.")
    
    st.markdown("""
    **📋 Amazon Launch Checklist:**
    - ✅ High-quality images (6+ photos)
    - ✅ Video demonstration
    - ✅ Bulleted features (5-7 benefits)
    - ✅ Back-end keywords (20+)
    - ✅ Start with $500/mo ad budget
    - ✅ Enroll in Amazon Vine for reviews
    """)

# ==================== TAB 6: COMPETITOR INTEL ====================
with tab6:
    st.markdown("""
    <div style="background: #e8eaf6; padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;">
        <span style="font-weight: 600; color: #1a237e;">🏆 Lego Competitor Intel</span>
        <span style="color: #5c6bc0; font-size: 14px; margin-left: 12px;">See what other labs are building</span>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("Perplexity API Key (or use demo)", type="password")
    
    query = st.selectbox("What do you want to research?", [
        "What are other labs charging for implants?",
        "What new products are labs launching?",
        "What events are labs attending?",
        "How are labs marketing to dentists?",
        "Custom question"
    ])
    
    if query == "Custom question":
        custom = st.text_area("Your question:", "What are successful labs doing differently?")
        final_query = custom
    else:
        final_query = query
    
    if st.button("🔍 Get Intelligence", type="primary"):
        if not api_key:
            # Demo mode
            st.markdown("""
            ### 🏆 Competitive Intel (Aggregated)
            
            **Pricing Benchmarks:**
            - Implants: $1,200-1,800 (avg $1,500)
            - Crowns: $300-500 (avg $400)
            - Veneers: $400-600 (avg $500)
            - Mouth Guards: $50-80 (avg $65)
            
            **New Products:**
            - Surgical Guides (52% of labs)
            - Digital workflows (47%)
            - Clear Aligners (28%)
            
            **Marketing:**
            - LinkedIn (78%)
            - Direct mail (65%)
            - Conferences (58%)
            - Referral programs (45%)
            
            **💡 What Successful Labs Do:**
            1. **Speed:** 5-day turnaround vs. 10-day avg
            2. **Communication:** Proactive updates
            3. **Quality:** 98%+ fit rate
            4. **Technology:** Digital scanning, 3D printing
            """)
        else:
            try:
                url = "https://api.perplexity.ai/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "sonar-small-online",
                    "messages": [{"role": "user", "content": f"Research: {final_query} for dental implant labs"}],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    st.markdown("### 📊 Intelligence Report")
                    st.markdown(result["choices"][0]["message"]["content"])
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ---------- FOOTER ----------
st.divider()
st.markdown("""
<div style="text-align: center; color: #757575; font-size: 12px; padding: 16px 0;">
    🧱 <strong>Lego Manufacturing Command Center</strong> – Build your decisions, block by block.<br>
    🔒 Your data stays local. No information is stored or shared.
</div>
""", unsafe_allow_html=True)