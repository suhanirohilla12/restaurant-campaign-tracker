import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Restaurant Campaign Performance", layout="wide")

st.markdown("""
<style>
    .kpi-card {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 10px;
        padding: 16px 14px;
        text-align: center;
    }
    .kpi-label {
        font-size: 11px;
        color: #a6adc8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #cdd6f4;
    }
    .section-title {
        font-size: 15px;
        font-weight: 600;
        color: #cdd6f4;
        margin: 22px 0 10px 0;
        border-bottom: 1px solid #313244;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Column definitions ────────────────────────────────────────────────────────

# 5 Bar charts: campaign total vs incremental
BAR_PAIRS = [
    ("GMV",      "AJ", "AK"),
    ("Txns",     "AL", "AM"),
    ("N Txns",   "an", "ao"),
    ("ULV",      "AT", "AV"),
    ("Bookings", "aw", "ay"),
]

# 5 Grouped bar charts: day-wise campaign vs base week
GROUPED_BARS = [
    ("GMV",      "e",  "F"),
    ("Txns",     "h",  "I"),
    ("N Txns",   "k",  "L"),
    ("Bookings", "q",  "r"),
    ("ULV",      "ah", "ai"),
]

# Pie chart bookings split
PIE_FREE = "v"
PIE_PAID = "aa"

# KPI Cards
KPI_COLS = [
    ("Txns Growth", "BA"),
    ("ULV Growth",  "BB"),
    ("CPIT",        "BC"),
    ("Inc Burn",    "bd"),
]

CHART_BASE = dict(
    plot_bgcolor="#1e1e2e",
    paper_bgcolor="#1e1e2e",
    font_color="#cdd6f4",
    margin=dict(t=50, b=30, l=10, r=10),
    xaxis=dict(gridcolor="#313244", showgrid=True),
    yaxis=dict(gridcolor="#313244", showgrid=True),
    legend=dict(bgcolor="#1e1e2e", font=dict(size=11)),
    height=320,
)

BAR_COLORS = [
    ("#89b4fa", "#b4befe"),
    ("#f38ba8", "#fab387"),
    ("#a6e3a1", "#94e2d5"),
    ("#cba6f7", "#f5c2e7"),
    ("#f9e2af", "#eba0ac"),
]


def find_col(df, name):
    """Case-insensitive column lookup."""
    nl = name.lower().strip()
    for col in df.columns:
        if col.lower().strip() == nl:
            return col
    return None


def to_num(series):
    s = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(s, errors="coerce")


def fmt(val):
    try:
        f = float(val)
        if np.isnan(f):
            return "—"
        if abs(f) >= 1_000_000:
            return f"{f/1_000_000:.2f}M"
        if abs(f) >= 1_000:
            return f"{f:,.0f}"
        return f"{f:,.2f}"
    except Exception:
        return str(val) if pd.notna(val) else "—"


def generate_sample_data():
    rng = np.random.default_rng(42)
    cams = ["Burger Palace_w16", "Sushi Zen_w16", "Taco Fiesta_w16"]
    rows = []
    for cam in cams:
        for day_offset in range(5):
            dt = pd.Timestamp("2026-04-22") + pd.Timedelta(days=day_offset)
            rows.append({
                "dt": dt.strftime("%m/%d/%Y"),
                "cam": cam,
                "e":  round(rng.uniform(50000, 200000), 2),
                "F":  round(rng.uniform(40000, 180000), 2),
                "h":  round(rng.uniform(100, 500), 2),
                "I":  round(rng.uniform(80, 400), 2),
                "k":  round(rng.uniform(20, 100), 2),
                "L":  round(rng.uniform(15, 90), 2),
                "q":  round(rng.uniform(50, 200), 2),
                "r":  round(rng.uniform(40, 180), 2),
                "v":  round(rng.uniform(20, 100), 2),
                "aa": round(rng.uniform(10, 80), 2),
                "ah": round(rng.uniform(500, 2000), 2),
                "ai": round(rng.uniform(400, 1800), 2),
                "an": round(rng.uniform(20, 100), 2),
                "ao": round(rng.uniform(10, 60), 2),
                "AJ": round(rng.uniform(200000, 800000), 2),
                "AK": round(rng.uniform(80000, 400000), 2),
                "AL": round(rng.uniform(500, 2000), 2),
                "AM": round(rng.uniform(200, 900), 2),
                "AT": round(rng.uniform(1000, 4000), 2),
                "AV": round(rng.uniform(400, 2000), 2),
                "aw": round(rng.uniform(200, 800), 2),
                "ay": round(rng.uniform(80, 400), 2),
                "BA": round(rng.uniform(1.0, 3.0), 4),
                "BB": round(rng.uniform(1.0, 3.0), 4),
                "BC": round(rng.uniform(-500, 1000), 2),
                "bd": round(rng.uniform(-20000, 50000), 2),
            })
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Campaign Dashboard")
    st.markdown("---")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            st.success(f"Loaded {len(df)} rows")
        except Exception as e:
            st.error(f"Error: {e}")
            df = generate_sample_data()
    else:
        df = generate_sample_data()
        st.info("Showing sample data")

    df.columns = [c.strip() for c in df.columns]
    # Strip string values (handles trailing spaces in campaign names)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    cam_col = "cam" if "cam" in df.columns else df.columns[0]
    st.markdown("---")
    campaigns = sorted(df[cam_col].dropna().unique().tolist())
    selected = st.selectbox("Select Restaurant / Campaign", campaigns)

# ── Filter ────────────────────────────────────────────────────────────────────
sel_df = df[df[cam_col] == selected].copy()
camp_row = sel_df.iloc[0]

if "dt" in sel_df.columns:
    sel_df["_dt"] = pd.to_datetime(sel_df["dt"], format="%m/%d/%Y", errors="coerce")
    if sel_df["_dt"].isna().all():
        sel_df["_dt"] = pd.to_datetime(sel_df["dt"], errors="coerce")
    sel_df = sel_df[sel_df["_dt"].notna()].sort_values("_dt")
    dates = sel_df["_dt"].dt.strftime("%b %d")
else:
    dates = pd.Series(range(len(sel_df)), index=sel_df.index)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"## {selected}")
st.markdown("---")

# ── 1. KPI CARDS ─────────────────────────────────────────────────────────────
present_kpi = [(label, find_col(df, col)) for label, col in KPI_COLS if find_col(df, col)]
if present_kpi:
    st.markdown('<div class="section-title">Campaign KPIs</div>', unsafe_allow_html=True)
    cols = st.columns(len(present_kpi))
    for col_ui, (label, col) in zip(cols, present_kpi):
        col_ui.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{fmt(camp_row.get(col, "—"))}</div>
        </div>""", unsafe_allow_html=True)

# ── 2. BAR CHARTS: Campaign vs Incremental ────────────────────────────────────
present_bars = [(t, find_col(df, b), find_col(df, i))
                for t, b, i in BAR_PAIRS
                if find_col(df, b) and find_col(df, i)]
if present_bars:
    st.markdown('<div class="section-title">Campaign vs Incremental</div>', unsafe_allow_html=True)
    cols = st.columns(len(present_bars))
    for col_ui, (title, base_col, incr_col), (c1, c2) in zip(cols, present_bars, BAR_COLORS):
        base_val = to_num(pd.Series([camp_row.get(base_col, 0)])).iloc[0]
        incr_val = to_num(pd.Series([camp_row.get(incr_col, 0)])).iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Campaign", x=["Campaign"], y=[base_val],
                             marker_color=c1, text=[fmt(base_val)], textposition="outside"))
        fig.add_trace(go.Bar(name="Incremental", x=["Incremental"], y=[incr_val],
                             marker_color=c2, text=[fmt(incr_val)], textposition="outside"))
        fig.update_layout(title=dict(text=title, font=dict(size=13, color="#cdd6f4")),
                          barmode="group", showlegend=False, **CHART_BASE)
        col_ui.plotly_chart(fig, use_container_width=True)

# ── 3. GROUPED BAR CHARTS: Day-wise Campaign vs Base Week ─────────────────────
present_grouped = [(t, find_col(df, c), find_col(df, b))
                   for t, c, b in GROUPED_BARS
                   if find_col(df, c) and find_col(df, b)]
if present_grouped:
    st.markdown('<div class="section-title">Campaign Week vs Base Week (Day-wise)</div>', unsafe_allow_html=True)
    per_row = 3
    for row_start in range(0, len(present_grouped), per_row):
        chunk = present_grouped[row_start:row_start + per_row]
        cols = st.columns(per_row)
        for col_ui, (title, camp_col_name, base_col_name), (c1, c2) in zip(
            cols, chunk, BAR_COLORS[row_start:]
        ):
            c_vals = to_num(sel_df[camp_col_name])
            b_vals = to_num(sel_df[base_col_name])
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Campaign Week", x=dates, y=c_vals,
                                 marker_color=c1))
            fig.add_trace(go.Bar(name="Base Week", x=dates, y=b_vals,
                                 marker_color=c2))
            fig.update_layout(
                title=dict(text=title, font=dict(size=13, color="#cdd6f4")),
                barmode="group",
                showlegend=True,
                legend=dict(orientation="h", y=1.15, x=0,
                            font=dict(size=10, color="#cdd6f4"),
                            bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#313244", showgrid=False, tickangle=-30),
                yaxis=dict(gridcolor="#313244", showgrid=True),
                **{k: v for k, v in CHART_BASE.items() if k not in ("legend", "xaxis", "yaxis")},
            )
            col_ui.plotly_chart(fig, use_container_width=True)

# ── 4. PIE CHART: Bookings Split ─────────────────────────────────────────────
free_col = find_col(df, PIE_FREE)
paid_col = find_col(df, PIE_PAID)
if free_col and paid_col:
    st.markdown('<div class="section-title">Bookings Split</div>', unsafe_allow_html=True)
    left, _ = st.columns([1, 2])
    free_val = to_num(sel_df[free_col]).sum()
    paid_val = to_num(sel_df[paid_col]).sum()
    fig = go.Figure(go.Pie(
        labels=["Free Bookings", "Paid Bookings"],
        values=[free_val, paid_val],
        marker=dict(colors=["#a6e3a1", "#f38ba8"]),
        hole=0.4,
        textinfo="label+percent",
        textfont=dict(color="#cdd6f4", size=12),
    ))
    fig.update_layout(
        plot_bgcolor="#1e1e2e", paper_bgcolor="#1e1e2e",
        font_color="#cdd6f4",
        legend=dict(bgcolor="#1e1e2e", font=dict(size=11)),
        margin=dict(t=40, b=20, l=10, r=10),
        height=320,
    )
    left.plotly_chart(fig, use_container_width=True)

# ── 5. DATA TABLE ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">All Data</div>', unsafe_allow_html=True)


def highlight_row(row_data):
    base      = "background-color: #1e1e2e; color: #cdd6f4"
    highlight = "background-color: #313244; color: #89b4fa; font-weight: 600"
    return [highlight if row_data.get(cam_col) == selected else base] * len(row_data)


display_df = df.drop(columns=["_dt"], errors="ignore").copy()
styled = display_df.style.apply(highlight_row, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

st.download_button(
    label="⬇ Download data as CSV",
    data=df.drop(columns=["_dt"], errors="ignore").to_csv(index=False).encode(),
    file_name="campaign_data.csv",
    mime="text/csv",
)
