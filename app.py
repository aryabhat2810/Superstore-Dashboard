"""
╔══════════════════════════════════════════════════════════════════════════╗
║          SUPERSTORE ANALYTICS DASHBOARD  — Streamlit + Plotly           ║
║  Features: KPIs · 12 Charts · Slicers · Filters · Insights Panel        ║
╚══════════════════════════════════════════════════════════════════════════╝

Run:  streamlit run superstore_dashboard.py
Deps: pip install streamlit pandas plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0.  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1.  COLOUR PALETTE  (consistent throughout)
# ─────────────────────────────────────────────
PALETTE = {
    "primary":   "#4361EE",
    "secondary": "#3A0CA3",
    "accent":    "#F72585",
    "success":   "#4CC9F0",
    "warning":   "#F4A261",
    "danger":    "#E63946",
    "bg":        "#0F1117",
    "card":      "#1A1D27",
    "text":      "#EAEAEA",
    "muted":     "#9CA3AF",
}

CAT_COLORS   = ["#4361EE", "#F72585", "#4CC9F0", "#F4A261", "#7209B7",
                "#3A0CA3", "#E63946", "#06D6A0", "#FB8500", "#8338EC"]
REGION_CLRS  = {"West": "#4361EE", "East": "#F72585",
                "Central": "#4CC9F0", "South": "#F4A261"}

# ─────────────────────────────────────────────
# 2.  GLOBAL CSS INJECTION
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ---------- Base ---------- */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
    background-color: #0F1117;
    color: #EAEAEA;
}
/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #13151F;
    border-right: 1px solid #2A2D3E;
}

/* Sidebar text (light + readable) */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #E5E7EB !important;
    font-size: 0.85rem;
}
/* ---------- KPI Cards ---------- */
.kpi-card {
    background: linear-gradient(145deg, #1A1D27, #21253A);
    border: 1px solid #2A2D3E;
    border-radius: 14px;
    padding: 20px 22px 16px;
    margin-bottom: 6px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    height: 3px; width: 100%;
}
.kpi-card.blue::before  { background: #4361EE; }
.kpi-card.pink::before  { background: #F72585; }
.kpi-card.cyan::before  { background: #4CC9F0; }
.kpi-card.amber::before { background: #F4A261; }
.kpi-card.green::before { background: #06D6A0; }

.kpi-label  { font-size: 0.72rem; color: #9CA3AF; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 4px; }
.kpi-value  { font-size: 1.72rem; font-weight: 700; color: #EAEAEA; line-height: 1.1; }
.kpi-delta  { font-size: 0.75rem; margin-top: 4px; }
.kpi-delta.pos { color: #06D6A0; }
.kpi-delta.neg { color: #E63946; }
.kpi-icon   { position: absolute; right: 18px; top: 16px; font-size: 1.6rem; opacity: .35; }

/* ---------- Section Headers ---------- */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1E3A8A;  /* dark blue */
    letter-spacing: .05em;
    text-transform: uppercase;
    padding: 6px 0;
    border-bottom: 2px solid #374151;
    margin-bottom: 16px;
}

/* ---------- Insight Cards ---------- */
.insight-card {
    background: #1A1D27;
    border-left: 3px solid #4361EE;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: .84rem;
    color: #C4C9D4;
    line-height: 1.55;
}
.insight-card b { color: #4CC9F0; }

/* ---------- Plotly Chart Container ---------- */
.chart-box {
    background: #1A1D27;
    border: 1px solid #2A2D3E;
    border-radius: 12px;
    padding: 12px 4px;
    margin-bottom: 10px;
}

/* ---------- Divider ---------- */
hr { border-color: #2A2D3E; }

/* ---------- Hide Streamlit branding ---------- */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3.  DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # ── Try common paths; fall back to local CSV ──────────────────────────
    paths = [
        "Sample_-_Superstore.csv",
        "/mnt/user-data/uploads/Sample_-_Superstore.csv",
    ]
    df = None
    for p in paths:
        try:
            df = pd.read_csv(p, encoding="latin1")
            break
        except FileNotFoundError:
            continue
    if df is None:
        st.error("⚠️  Dataset not found. Place 'Sample_-_Superstore.csv' in the same folder.")
        st.stop()

    # ── Date Parsing ────────────────────────────────────────────────────
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=False)
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=False)
    df["Year"]       = df["Order Date"].dt.year
    df["Month"]      = df["Order Date"].dt.to_period("M").astype(str)
    df["YearMonth"]  = df["Order Date"].dt.to_period("M")
    df["Quarter"]    = df["Order Date"].dt.to_period("Q").astype(str)

    # ── Derived Columns ──────────────────────────────────────────────────
    df["Profit Margin (%)"] = (df["Profit"] / df["Sales"] * 100).round(2)
    df["Discount Band"] = pd.cut(df["Discount"],
                                  bins=[-0.01, 0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                  labels=["No Discount","0-20%","20-40%","40-60%","60-80%","80-100%"])
    return df

df_raw = load_data()

# ─────────────────────────────────────────────
# 4.  SIDEBAR  — SLICERS (user-controlled UI)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Superstore")
    st.markdown("<p style='color:#9CA3AF;font-size:.78rem;'>Analytics Dashboard · v2025</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Date Range SLICER ──────────────────────────────────────────────
    st.markdown("### 📅 Date Range")
    min_d = df_raw["Order Date"].min().date()
    max_d = df_raw["Order Date"].max().date()
    date_range = st.date_input("Select Range", value=(min_d, max_d),
                                min_value=min_d, max_value=max_d)

    st.markdown("---")

    # ── Region SLICER ─────────────────────────────────────────────────
    st.markdown("### 🌎 Region")
    regions = st.multiselect("Select Region(s)",
                              options=sorted(df_raw["Region"].unique()),
                              default=sorted(df_raw["Region"].unique()))

    # ── Category SLICER ───────────────────────────────────────────────
    st.markdown("### 📦 Category")
    categories = st.multiselect("Select Category",
                                  options=sorted(df_raw["Category"].unique()),
                                  default=sorted(df_raw["Category"].unique()))

    # ── Sub-Category SLICER ───────────────────────────────────────────
    available_sub = sorted(df_raw[df_raw["Category"].isin(categories)]["Sub-Category"].unique())
    st.markdown("### 🗂 Sub-Category")
    sub_cats = st.multiselect("Select Sub-Category",
                               options=available_sub,
                               default=available_sub)

    # ── Segment SLICER ────────────────────────────────────────────────
    st.markdown("### 👥 Segment")
    segments = st.multiselect("Select Segment",
                               options=sorted(df_raw["Segment"].unique()),
                               default=sorted(df_raw["Segment"].unique()))

    # ── Ship Mode SLICER ─────────────────────────────────────────────
    st.markdown("### 🚚 Ship Mode")
    ship_modes = st.multiselect("Select Ship Mode",
                                 options=sorted(df_raw["Ship Mode"].unique()),
                                 default=sorted(df_raw["Ship Mode"].unique()))

    st.markdown("---")
    st.markdown("<p style='color:#9CA3AF;font-size:.72rem;'>All charts & KPIs update based on selected filters.</p>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 5.  BACKEND FILTER (data logic layer)
# ─────────────────────────────────────────────
# Guard for single-date selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    d_start, d_end = df_raw["Order Date"].min(), df_raw["Order Date"].max()

df = df_raw[
    (df_raw["Order Date"] >= d_start) &
    (df_raw["Order Date"] <= d_end) &
    (df_raw["Region"].isin(regions)) &
    (df_raw["Category"].isin(categories)) &
    (df_raw["Sub-Category"].isin(sub_cats)) &
    (df_raw["Segment"].isin(segments)) &
    (df_raw["Ship Mode"].isin(ship_modes))
].copy()

if df.empty:
    st.warning("⚠️  No data matches your filter selection. Please widen your criteria.")
    st.stop()

# ─────────────────────────────────────────────
# 6.  PLOTLY CHART THEME HELPER
# ─────────────────────────────────────────────
def dark_layout(fig, title="", height=340):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#162443"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF", size=11),
        margin=dict(l=40, r=20, t=42, b=40),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(gridcolor="#2A2D3E", linecolor="#2A2D3E", zerolinecolor="#2A2D3E"),
        yaxis=dict(gridcolor="#2A2D3E", linecolor="#2A2D3E", zerolinecolor="#2A2D3E"),
    )
    return fig

# ─────────────────────────────────────────────
# 7.  COMPUTE KPIs
# ─────────────────────────────────────────────
total_sales    = df["Sales"].sum()
total_profit   = df["Profit"].sum()
profit_margin  = total_profit / total_sales * 100 if total_sales else 0
total_orders   = df["Order ID"].nunique()
avg_order_val  = df.groupby("Order ID")["Sales"].sum().mean()
total_qty      = df["Quantity"].sum()
best_cat       = df.groupby("Category")["Profit"].sum().idxmax()
best_region    = df.groupby("Region")["Profit"].sum().idxmax()
num_customers  = df["Customer ID"].nunique()

# ─────────────────────────────────────────────
# 8.  DASHBOARD HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='display:flex;align-items:center;gap:14px;padding:8px 0 20px'>
  <span style='font-size:2.6rem'>🛒</span>
  <div>
    <h1 style='margin:0;font-size:1.75rem;font-weight:800;color:#111827;letter-spacing:.02em'>
      Superstore Analytics Dashboard
    </h1>
    <p style='margin:2px 0 0;color:#9CA3AF;font-size:.84rem'>
      Sales · Profit · Customers · Geography · Trends &nbsp;|&nbsp;
      <span style='color:#4361EE'>Interactive</span> — use the sidebar to slice the data
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 9.  KPI CARDS  (row of 5)
# ─────────────────────────────────────────────
kpi_cols = st.columns(5)

kpi_data = [
    ("blue",  "💰", "Total Sales",      f"${total_sales:,.0f}",     None),
    ("pink",  "📈", "Total Profit",     f"${total_profit:,.0f}",    None),
    ("cyan",  "📊", "Profit Margin",    f"{profit_margin:.1f}%",    None),
    ("amber", "🧾", "Avg Order Value",  f"${avg_order_val:,.0f}",   None),
    ("green", "👤", "Unique Customers", f"{num_customers:,}",       None),
]

for col, (color, icon, label, val, delta) in zip(kpi_cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card {color}">
          <span class="kpi-icon">{icon}</span>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10.  CHART SECTION  ── Row 1: Sales Trend + Category Bar
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Sales & Profit Overview</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])

# ── LINE CHART: Monthly Sales Trend ─────────────────────────────────────
# Why: Shows temporal patterns / seasonality across months
with c1:
    monthly = (df.groupby("Month")
                 .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
                 .reset_index()
                 .sort_values("Month"))
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Sales"],
        name="Sales", mode="lines+markers",
        line=dict(color="#4361EE", width=2.5),
        marker=dict(size=5), fill="tozeroy",
        fillcolor="rgba(67,97,238,0.12)"))
    fig_line.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="#F72585", width=2, dash="dot"),
        marker=dict(size=4)))
    fig_line.update_xaxes(tickangle=45, tickfont_size=9, nticks=12)
    dark_layout(fig_line, "📈 Monthly Sales & Profit Trend", height=320)
    st.plotly_chart(fig_line, use_container_width=True)

# ── BAR CHART: Sales by Category ─────────────────────────────────────
# Why: Discrete comparison across 3 categories; bar is most readable
with c2:
    cat_df = (df.groupby("Category")
                .agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
                .reset_index()
                .sort_values("Sales", ascending=True))
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=cat_df["Category"], x=cat_df["Sales"], name="Sales",
        orientation="h", marker_color="#4361EE",
        text=cat_df["Sales"].map("${:,.0f}".format), textposition="outside",
        textfont_size=10))
    fig_bar.add_trace(go.Bar(
        y=cat_df["Category"], x=cat_df["Profit"], name="Profit",
        orientation="h", marker_color="#F72585",
        text=cat_df["Profit"].map("${:,.0f}".format), textposition="outside",
        textfont_size=10))
    fig_bar.update_layout(barmode="group")
    dark_layout(fig_bar, "📦 Sales & Profit by Category", height=320)
    st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────
# ── Row 2: Pie/Donut + Region Bar + Scatter
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Segment, Region & Correlation</div>', unsafe_allow_html=True)
c3, c4, c5 = st.columns(3)

# ── DONUT CHART: Sales by Segment ───────────────────────────────────
# Why: Shows proportional share of three segments clearly
with c3:
    seg_df = df.groupby("Segment")["Sales"].sum().reset_index()
    fig_donut = px.pie(seg_df, names="Segment", values="Sales",
                        hole=0.55, color_discrete_sequence=CAT_COLORS[:3])
    fig_donut.update_traces(textinfo="percent+label", textfont_size=11,
                             pull=[0.03]*3)
    dark_layout(fig_donut, "🧩 Sales Share by Segment", height=310)
    st.plotly_chart(fig_donut, use_container_width=True)

# ── STACKED BAR: Region × Segment ────────────────────────────────────
# Why: Compares both regional and segment composition simultaneously
with c4:
    reg_seg = (df.groupby(["Region","Segment"])["Sales"]
                 .sum().reset_index())
    fig_stk = px.bar(reg_seg, x="Region", y="Sales", color="Segment",
                      color_discrete_sequence=CAT_COLORS,
                      text_auto=".2s", barmode="stack")
    fig_stk.update_traces(textfont_size=9)
    dark_layout(fig_stk, "📊 Stacked Sales: Region × Segment", height=310)
    st.plotly_chart(fig_stk, use_container_width=True)

# ── SCATTER PLOT: Sales vs Profit ─────────────────────────────────────
# Why: Reveals profit-sales correlation, high-sales-low-profit items
with c5:
    scat_df = (df.groupby("Sub-Category")
                 .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                      Qty=("Quantity","sum"))
                 .reset_index())
    fig_scat = px.scatter(scat_df, x="Sales", y="Profit",
                           size="Qty", color="Sub-Category",
                           hover_name="Sub-Category",
                           color_discrete_sequence=CAT_COLORS,
                           text="Sub-Category")
    fig_scat.update_traces(textposition="top center", textfont_size=8)
    fig_scat.add_hline(y=0, line_dash="dot", line_color="#E63946", opacity=0.7)
    dark_layout(fig_scat, "🔵 Sales vs Profit (Sub-Category)", height=310)
    st.plotly_chart(fig_scat, use_container_width=True)

# ─────────────────────────────────────────────
# ── Row 3: Area Chart + Treemap
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">📐 Cumulative Trends & Hierarchy</div>', unsafe_allow_html=True)
c6, c7 = st.columns([3, 2])

# ── AREA CHART: Cumulative Quarterly Sales by Category ──────────────
# Why: Shows growth momentum over time for each category (stacked = additive view)
with c6:
    qtr_cat = (df.groupby(["Quarter","Category"])["Sales"]
                 .sum().reset_index()
                 .sort_values("Quarter"))
    fig_area = px.area(qtr_cat, x="Quarter", y="Sales", color="Category",
                        color_discrete_sequence=CAT_COLORS,
                        line_group="Category")
    fig_area.update_xaxes(tickangle=35, nticks=16, tickfont_size=9)
    dark_layout(fig_area, "📉 Quarterly Sales Trend by Category", height=320)
    st.plotly_chart(fig_area, use_container_width=True)

# ── TREEMAP: Hierarchical Category → Sub-Category Revenue ───────────
# Why: Best for hierarchical, nested proportional data
with c7:
    tree_df = (df.groupby(["Category","Sub-Category"])["Sales"]
                 .sum().reset_index())
    fig_tree = px.treemap(tree_df, path=["Category","Sub-Category"],
                           values="Sales",
                           color="Sales",
                           color_continuous_scale=["#0F1117","#4361EE","#F72585"])
    fig_tree.update_traces(textinfo="label+value", textfont_size=11)
    dark_layout(fig_tree, "🗺 Treemap: Category → Sub-Category Sales", height=320)
    st.plotly_chart(fig_tree, use_container_width=True)

# ─────────────────────────────────────────────
# ── Row 4: Heatmap + Histogram + Box Plot
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🧪 Distribution, Spread & Patterns</div>', unsafe_allow_html=True)
c8, c9, c10 = st.columns(3)

# ── HEATMAP: Avg Profit by Region × Category ────────────────────────
# Why: Intensity matrix instantly shows which combinations win/lose
with c8:
    heat_df = (df.groupby(["Region","Category"])["Profit"]
                 .sum().unstack(fill_value=0))
    fig_heat = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0,"#E63946"],[0.5,"#1A1D27"],[1,"#4361EE"]],
        text=heat_df.values.round(0),
        texttemplate="$%{text:,.0f}",
        showscale=True, colorbar=dict(len=0.8)))
    dark_layout(fig_heat, "🌡 Profit Heatmap: Region × Category", height=290)
    st.plotly_chart(fig_heat, use_container_width=True)

# ── HISTOGRAM: Sales Distribution ───────────────────────────────────
# Why: Shows spread and skewness of order-level sales values
with c9:
    fig_hist = px.histogram(df, x="Sales", nbins=60,
                             color_discrete_sequence=["#4CC9F0"])
    fig_hist.update_traces(marker_line_color="#0F1117", marker_line_width=0.5)
    dark_layout(fig_hist, "📊 Sales Distribution (Histogram)", height=290)
    st.plotly_chart(fig_hist, use_container_width=True)

# ── BOX PLOT: Profit Distribution by Category ───────────────────────
# Why: Shows median, IQR, and outliers across categories
with c10:
    fig_box = px.box(df, x="Category", y="Profit",
                      color="Category",
                      color_discrete_sequence=CAT_COLORS,
                      notched=True, points=False)
    dark_layout(fig_box, "📦 Profit Spread by Category (Box Plot)", height=290)
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ─────────────────────────────────────────────
# ── Row 5: Sub-Category Profit Bar + Discount Impact + Ship Mode
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🔎 Deep-Dive: Sub-Category, Discounts & Logistics</div>', unsafe_allow_html=True)
c11, c12 = st.columns([3, 2])

# ── HORIZONTAL BAR: Sub-Category Profit (winner/loser view) ─────────
with c11:
    sub_profit = (df.groupby("Sub-Category")["Profit"]
                    .sum().reset_index()
                    .sort_values("Profit"))
    sub_profit["Color"] = sub_profit["Profit"].apply(
        lambda v: "#E63946" if v < 0 else "#4361EE")
    fig_subbar = go.Figure(go.Bar(
        y=sub_profit["Sub-Category"], x=sub_profit["Profit"],
        orientation="h",
        marker_color=sub_profit["Color"],
        text=sub_profit["Profit"].map("${:,.0f}".format),
        textposition="outside", textfont_size=9))
    fig_subbar.add_vline(x=0, line_color="#9CA3AF", line_dash="dash", line_width=1)
    dark_layout(fig_subbar, "🏆 Profit by Sub-Category (Red = Loss)", height=380)
    st.plotly_chart(fig_subbar, use_container_width=True)

# ── PIE: Ship Mode Distribution + Discount Band bar ─────────────────
with c12:
    # Ship Mode Donut
    ship_df = df["Ship Mode"].value_counts().reset_index()
    ship_df.columns = ["Ship Mode", "Count"]
    fig_ship = px.pie(ship_df, names="Ship Mode", values="Count",
                       hole=0.45, color_discrete_sequence=CAT_COLORS)
    fig_ship.update_traces(textinfo="percent+label", textfont_size=10)
    dark_layout(fig_ship, "🚚 Orders by Ship Mode", height=280)
    st.plotly_chart(fig_ship, use_container_width=True)

    # Discount Band → Avg Profit bar
    disc_df = (df.groupby("Discount Band")["Profit"]
                 .mean().reset_index()
                 .sort_values("Discount Band"))
    disc_df["Color"] = disc_df["Profit"].apply(lambda v: "#E63946" if v < 0 else "#4CC9F0")
    fig_disc = go.Figure(go.Bar(
        x=disc_df["Discount Band"], y=disc_df["Profit"],
        marker_color=disc_df["Color"],
        text=disc_df["Profit"].round(1),
        textposition="outside", textfont_size=9))
    dark_layout(fig_disc, "💸 Avg Profit by Discount Band", height=245)
    st.plotly_chart(fig_disc, use_container_width=True)

# ─────────────────────────────────────────────
# ── Row 6: Map — State-level Sales
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">🗺 Geographic Performance</div>', unsafe_allow_html=True)

state_map = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
    "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO",
    "Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ",
    "New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH",
    "Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
    "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

# FIRST aggregate
state_df = (df.groupby("State")
              .agg(Sales=("Sales","sum"), Profit=("Profit","sum"),
                   Orders=("Order ID","nunique"))
              .reset_index())

# THEN map
state_df["State Code"] = state_df["State"].map(state_map)

# Optional but smart: drop invalid mappings
state_df = state_df.dropna(subset=["State Code"])

fig_map = px.choropleth(
    state_df,
    locations="State Code",
    locationmode="USA-states",
    color="Sales",
    hover_name="State",
    hover_data={"Sales":":.0f","Profit":":.0f","Orders":True},
    scope="usa",
    color_continuous_scale=[
        "#1E3A8A",  # dark blue
        "#3B82F6",  # blue
        "#60A5FA",  # light blue
        "#A78BFA",  # violet
        "#C084FC",  # soft purple
        "#F472B6",  # pink
        "#F9A8D4"   # light pink highlight
    ],
    labels={"Sales":"Total Sales ($)"},
)

fig_map.update_layout(
    geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
             landcolor="#1A1D27", subunitcolor="#2A2D3E"),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9CA3AF"),
    margin=dict(l=0, r=0, t=40, b=0),
    height=400,
    coloraxis_colorbar=dict(title="Sales ($)", tickfont=dict(color="#9CA3AF")),
    title=dict(text="🗺 State-Level Sales Performance (USA)", font=dict(size=13, color="#111827"), x=0.01),
)

st.plotly_chart(fig_map, use_container_width=True)

# ─────────────────────────────────────────────
# 11.  INSIGHTS PANEL
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">💡 Key Insights</div>', unsafe_allow_html=True)

# Re-compute insight values from filtered df
ins_top_state  = state_df.sort_values("Sales", ascending=False).iloc[0]
ins_worst_sub  = df.groupby("Sub-Category")["Profit"].sum().idxmin()
ins_worst_val  = df.groupby("Sub-Category")["Profit"].sum().min()
ins_best_sub   = df.groupby("Sub-Category")["Profit"].sum().idxmax()
ins_best_val   = df.groupby("Sub-Category")["Profit"].sum().max()
ins_disc_0     = df[df["Discount"]==0]["Profit"].mean()
ins_disc_hi    = df[df["Discount"]>=0.4]["Profit"].mean()
yoy            = df.groupby("Year")["Sales"].sum()
yoy_growth     = ((yoy.iloc[-1] - yoy.iloc[-2]) / yoy.iloc[-2] * 100) if len(yoy) >= 2 else 0
cons_share     = df[df["Segment"]=="Consumer"]["Sales"].sum() / df["Sales"].sum() * 100
tech_margin    = df[df["Category"]=="Technology"]["Profit"].sum() / df[df["Category"]=="Technology"]["Sales"].sum()*100
furn_margin    = df[df["Category"]=="Furniture"]["Profit"].sum() / df[df["Category"]=="Furniture"]["Sales"].sum()*100
same_day_pct   = (df[df["Ship Mode"]=="Same Day"].shape[0] / df.shape[0])*100
top_city_sales = df.groupby("City")["Sales"].sum().idxmax()

insights = [
    (f"<b>West</b> is the top-performing region by both Sales & Profit. "
     f"<b>{best_region}</b> leads profit contribution."),
    (f"<b>{ins_top_state['State']}</b> is the #1 state with "
     f"${ins_top_state['Sales']:,.0f} in sales and {ins_top_state['Orders']:,} orders."),
    (f"<b>Technology</b> is the most profitable category ({tech_margin:.1f}% margin), "
     f"while <b>Furniture</b> barely breaks even ({furn_margin:.1f}% margin)."),
    (f"<b>{ins_best_sub}</b> is the best sub-category by profit (${ins_best_val:,.0f}), "
     f"while <b>{ins_worst_sub}</b> is the worst (${ins_worst_val:,.0f})."),
    (f"<b>Discounts ≥ 40%</b> average a profit of <b>${ins_disc_hi:,.1f}</b> — "
     f"vs ${ins_disc_0:,.1f} with no discount. Heavy discounting destroys margins."),
    (f"<b>Consumer</b> segment drives {cons_share:.1f}% of total revenue, "
     f"making it the most critical segment to retain."),
    (f"Year-over-year sales growth (latest year): <b>{yoy_growth:+.1f}%</b>. "
     f"The business shows a positive upward trajectory."),
    (f"<b>Standard Class</b> shipping accounts for ~60% of orders — "
     f"customers predominantly choose economy shipping."),
    (f"<b>Tables</b> and <b>Bookcases</b> are chronically loss-making sub-categories "
     f"— pricing or sourcing review recommended."),
    (f"<b>{top_city_sales}</b> is the #1 city by sales. "
     f"Urban concentration is high — regional diversification may unlock growth."),
    (f"Profit margin overall stands at <b>{profit_margin:.1f}%</b>. "
     f"Reducing high-discount orders could push it above 15%."),
    (f"<b>Same-Day</b> shipping is used in only {same_day_pct:.1f}% of orders, "
     f"suggesting premium logistics is under-utilized."),
]

# Display in 2 columns
ins_left, ins_right = st.columns(2)
for i, ins in enumerate(insights):
    target = ins_left if i % 2 == 0 else ins_right
    with target:
        st.markdown(f'<div class="insight-card">💡 {ins}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 12.  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;color:#4A4F6B;font-size:.75rem;padding:12px 0;
     border-top:1px solid #2A2D3E;'>
  Superstore Analytics Dashboard &nbsp;·&nbsp; Built with Streamlit + Plotly
  &nbsp;·&nbsp; Data: Sample Superstore (9,994 rows)
</div>
""", unsafe_allow_html=True)