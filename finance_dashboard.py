import streamlit as st
import numpy_financial as npf
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Financial Economic Model", layout="wide")

# --- CUSTOM CSS FOR "TANK" FEEL ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: GLOBAL INPUTS ---
st.sidebar.title("⚙️ Global Settings")
age = st.sidebar.slider("Current Age", 20, 70, 45)
life_expectancy = st.sidebar.slider("Life Expectancy (End Age)", 80, 100, 95)
inflation = st.sidebar.slider("Annual Inflation (%)", 0.0, 8.0, 3.0) / 100
return_rate = st.sidebar.slider("Market Return (%)", 1.0, 12.0, 7.0) / 100

st.sidebar.markdown("---")
st.sidebar.title("📊 Financial Inputs")
liquid_assets = st.sidebar.number_input("Current Assets ($)", value=500000, step=10000)
liabilities = st.sidebar.number_input("Current Liabilities ($)", value=50000, step=5000)
net_start = liquid_assets - liabilities

# --- SCENARIO COMPARISON INPUTS ---
st.sidebar.markdown("---")
st.sidebar.title("🚀 Scenario Variables")
col_a, col_b = st.sidebar.columns(2)
with col_a:
    retire_a = st.number_input("Retire Age (A)", value=65)
    savings_a = st.number_input("Annual Savings (A)", value=30000)
with col_b:
    retire_b = st.number_input("Retire Age (B)", value=62)
    savings_b = st.number_input("Annual Savings (B)", value=45000)

# --- CALCULATION ENGINE ---
def run_model(r_age, annual_sav):
    # Calculate real rate (Fisher Equation)
    real_r = (1 + return_rate) / (1 + inflation) - 1
    years_grow = r_age - age
    years_retire = life_expectancy - r_age
    
    # 1. Nest Egg at Retirement
    egg = npf.fv(real_r, years_grow, -annual_sav, -net_start)
    
    # 2. Sustainable Annual Withdrawal
    # Using PMT to find how much we can drain until the tank is empty
    income = npf.pmt(real_r, years_retire, -egg, 0)
    return egg, income, years_grow

egg_a, inc_a, grow_a = run_model(retire_a, savings_a)
egg_b, inc_b, grow_b = run_model(retire_b, savings_b)

# --- DASHBOARD MAIN VISUALS ---
st.title("🛡️ Personal Economic Model: Scenario Comparison")
st.write(f"Comparing your current path to an optimized strategy over a **{life_expectancy - age} year** horizon.")

# Metric Row
m1, m2, m3 = st.columns(3)
m1.metric("Current Nest Egg (A)", f"${egg_a:,.0f}")
m2.metric("Optimized Nest Egg (B)", f"${egg_b:,.0f}", delta=f"${(egg_b - egg_a):,.0f}")
m3.metric("Income Lift", f"+${(inc_b - inc_a):,.0f}/yr", delta_color="normal")

st.markdown("---")

# Chart Row
chart_col, table_col = st.columns([2, 1])

with chart_col:
    fig = go.Figure()
    # Scenario A
    fig.add_trace(go.Bar(name='Present Position', x=['Nest Egg', 'Annual Lifestyle Flow'], y=[egg_a, inc_a], marker_color='#94a3b8'))
    # Scenario B
    fig.add_trace(go.Bar(name='Proposed Solution', x=['Nest Egg', 'Annual Lifestyle Flow'], y=[egg_b, inc_b], marker_color='#22c55e'))
    
    fig.update_layout(barmode='group', height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    st.subheader("Quick Analysis")
    st.write(f"**Scenario B** allows you to retire **{retire_a - retire_b} years earlier**.")
    st.write(f"By increasing savings, your monthly lifestyle budget grows by **${(inc_b - inc_a)/12:,.0f}**.")
    
    # Tax Leak Simulation (Simple 25% Estimate)
    st.info(f"💡 Estimated after-tax monthly income (B): **${(inc_b * 0.75 / 12):,.0f}**")

# --- PROJECTION TABLE ---
st.markdown("### 📈 Detailed Growth Breakdown")
comparison_df = pd.DataFrame({
    "Metric": ["Retirement Age", "Years to Accumulate", "Total Nest Egg", "Annual Lifestyle Outflow"],
    "Scenario A": [retire_a, grow_a, f"${egg_a:,.0f}", f"${inc_a:,.0f}"],
    "Scenario B": [retire_b, grow_b, f"${egg_b:,.0f}", f"${inc_b:,.0f}"]
})
st.table(comparison_df)