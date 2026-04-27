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

# D/F/H/J/L: top-level campaign KPI cards
TOP_KPI_COLS = [
    ("GMV",      "Campaign GMV"),
    ("Txns",     "Txns Campaigns"),
    ("ULV",      "ULV campaign"),
    ("N Txns",   "N txns camp"),
    ("Bookings", "Bookings campaign"),
]

# Y–AE: secondary KPI cards
SEC_KPI_COLS = [
    ("Inc Burn",           "Inc burn (Campaign)"),
    ("CPIT",               "CPIT (campaign)"),
    ("Txns Growth",        "TXNS growth"),
    ("ULV Growth",         "ULV Growth"),
    ("Banner Impressions", "Banner impressions"),
    ("Banner Clicks",      "Banner clicks"),
    ("Banner CTR",         "banner ctr"),
]

# D–M: 5 paired bar charts (campaign vs incremental)
BAR_PAIRS = [
    ("GMV",      "Campaign GMV",      "Inc GMV Campaign"),
    ("Txns",     "Txns Campaigns",    "Inc txns camp"),
    ("ULV",      "ULV campaign",      "Inc ulv campaign"),
    ("N Txns",   "N txns camp",       "Inc N txns camp"),
    ("Bookings", "Bookings campaign", "Inc Bookings camp"),
]

# N–W: 5 paired line charts (campaign week vs base week)
LINE_PAIRS = [
    ("GMV",      "gmv",           "base week gmv"),
    ("ULV",      "ulv_",          "base week ulv"),
    ("Txns",     "txns",          "base week txns"),
    ("N Txns",   "n_txns",        "base week n txns"),
    ("Bookings", "bookings_made", "base week bookings"),
]

U2T_COL = "u2t"

CHART_BASE = dict(
    plot_bgcolor="#1e1e2e",
    paper_bgcolor="#1e1e2e",
    font_color="#cdd6f4",
    margin=dict(t=40, b=20, l=10, r=10),
    xaxis=dict(gridcolor="#313244", showgrid=True),
    yaxis=dict(gridcolor="#313244", showgrid=True),
    legend=dict(bgcolor="#1e1e2e", font=dict(size=11)),
    height=300,
)

BAR_COLORS = [
    ("#89b4fa", "#b4befe"),
    ("#f38ba8", "#fab387"),
    ("#a6e3a1", "#94e2d5"),
    ("#cba6f7", "#f5c2e7"),
    ("#f9e2af", "#eba0ac"),
]

LINE_COLORS = [
    ("#89b4fa", "#585b70"),
    ("#a6e3a1", "#2d6a2d"),
    ("#f38ba8", "#7d3354"),
    ("#fab387", "#7d5437"),
    ("#cba6f7", "#6c4fa0"),
]


def fmt(val):
    try:
        f = float(val)
        if np.isnan(f):
            return "—"
        if abs(f) >= 1_000_000:
            return f"{f/1_000_000:.2f}M"
        if abs(f) >= 1_000:
            return f"{f:,.1f}"
        return f"{f:,.2f}"
    except Exception:
        return str(val) if pd.notna(val) else "—"


def generate_sample_data():
    rng = np.random.default_rng(42)
    cams = ["Burger Palace_w16", "Sushi Zen_w16", "Taco Fiesta_w16", "Pizza Heaven_w16"]
    rows = []
    for cam in cams:
        for day_offset in range(7):
            dt = pd.Timestamp("2026-04-13") + pd.Timedelta(days=day_offset)
            bg, bt, bu, bn, bb = (rng.uniform(100_000, 500_000), rng.uniform(50, 200),
                                   rng.uniform(300, 1500), rng.uniform(10, 60), rng.uniform(20, 100))
            rows.append({
                "dt": dt.strftime("%m/%d/%Y"),
                "city": rng.choice(["Delhi", "Mumbai", "Bangalore"]),
                "cam": cam,
                "Campaign GMV":       round(bg, 2),
                "Inc GMV Campaign":   round(bg * rng.uniform(0.4, 0.7), 2),
                "Txns Campaigns":     round(bt, 2),
                "Inc txns camp":      round(bt * rng.uniform(0.3, 0.6), 2),
                "ULV campaign":       round(bu, 2),
                "Inc ulv campaign":   round(bu * rng.uniform(0.2, 0.5), 2),
                "N txns camp":        round(bn, 2),
                "Inc N txns camp":    round(bn * rng.uniform(0.3, 0.7), 2),
                "Bookings campaign":  round(bb, 2),
                "Inc Bookings camp":  round(bb * rng.uniform(0.4, 0.8), 2),
                "gmv":                round(bg * rng.uniform(0.8, 1.1), 2),
                "base week gmv":      round(bg * rng.uniform(0.6, 0.85), 2),
                "ulv_":               round(bu * rng.uniform(0.9, 1.05), 2),
                "base week ulv":      round(bu * rng.uniform(0.7, 0.9), 2),
                "txns":               round(bt * rng.uniform(0.9, 1.1), 2),
                "base week txns":     round(bt * rng.uniform(0.6, 0.85), 2),
                "n_txns":             round(bn * rng.uniform(0.85, 1.1), 2),
                "base week n txns":   round(bn * rng.uniform(0.6, 0.85), 2),
                "bookings_made":      round(bb * rng.uniform(0.85, 1.1), 2),
                "base week bookings": round(bb * rng.uniform(0.6, 0.85), 2),
                "u2t":                round(rng.uniform(5, 25), 2),
                "Inc burn (Campaign)":round(rng.uniform(-20000, 50000), 2),
                "CPIT (campaign)":    round(rng.uniform(-500, 1000), 2),
                "TXNS growth":        round(rng.uniform(1.0, 3.5), 4),
                "ULV Growth":         round(rng.uniform(1.0, 3.5), 4),
                "Banner impressions": round(rng.uniform(10000, 200000)),
                "Banner clicks":      round(rng.uniform(100, 5000)),
                "banner ctr":         round(rng.uniform(0.005, 0.05), 4),
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
            st.error(f"Error reading file: {e}")
            df = generate_sample_data()
    else:
        df = generate_sample_data()
        st.info("Showing sample data")

    df.columns = [c.strip() for c in df.columns]

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    cam_col = "cam" if "cam" in df.columns else df.columns[0]

    st.markdown("---")
    campaigns = sorted(df[cam_col].dropna().unique().tolist())
    selected = st.selectbox("Select Restaurant / Campaign", campaigns)

# ── Filter ────────────────────────────────────────────────────────────────────
sel_df = df[df[cam_col] == selected].copy()
camp_row = sel_df.iloc[0]

if "dt" in sel_df.columns:
    raw = sel_df["dt"].astype(str).str.strip()
    parsed = pd.to_datetime(raw, format="%m/%d/%Y", errors="coerce")
    # Fallback: Excel serial date numbers (e.g. 46022.9999 → Apr 22 2026)
    still_nat = parsed.isna()
    if still_nat.any():
        numeric = pd.to_numeric(sel_df.loc[still_nat, "dt"], errors="coerce")
        excel = pd.to_datetime("1899-12-30") + pd.to_timedelta(numeric.fillna(0), unit="D")
        parsed[still_nat] = excel
    sel_df["_dt"] = parsed.dt.normalize()
    sel_df = sel_df[sel_df["_dt"].notna()].sort_values("_dt")
    dates = sel_df["_dt"]
else:
    dates = pd.Series(range(len(sel_df)), index=sel_df.index)

# ── Header ────────────────────────────────────────────────────────────────────
city = camp_row.get("city", "")
st.markdown(f"## {selected}" + (f"  —  {city}" if city else ""))
st.markdown("---")

# ── 1. TOP KPI CARDS (D/F/H/J/L: campaign values) ────────────────────────────
present_top = [(label, col) for label, col in TOP_KPI_COLS if col in df.columns]
if present_top:
    st.markdown('<div class="section-title">Campaign Performance</div>', unsafe_allow_html=True)
    cols = st.columns(len(present_top))
    for col_ui, (label, col) in zip(cols, present_top):
        col_ui.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{fmt(camp_row.get(col, "—"))}</div>
        </div>
        """, unsafe_allow_html=True)

# ── 2. SECONDARY KPI CARDS (Y–AE) ────────────────────────────────────────────
present_sec = [(label, col) for label, col in SEC_KPI_COLS if col in df.columns]
if present_sec:
    st.markdown('<div class="section-title">Campaign KPIs</div>', unsafe_allow_html=True)
    cols = st.columns(len(present_sec))
    for col_ui, (label, col) in zip(cols, present_sec):
        col_ui.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{fmt(camp_row.get(col, "—"))}</div>
        </div>
        """, unsafe_allow_html=True)

# ── 3. BAR CHARTS (Campaign vs Incremental) ───────────────────────────────────
present_bars = [(t, b, i) for t, b, i in BAR_PAIRS if b in df.columns and i in df.columns]
if present_bars:
    st.markdown('<div class="section-title">Campaign vs Incremental</div>', unsafe_allow_html=True)
    cols = st.columns(len(present_bars))
    for col_ui, (title, base_col, incr_col), (c1, c2) in zip(cols, present_bars, BAR_COLORS):
        base_val = camp_row.get(base_col, 0)
        incr_val = camp_row.get(incr_col, 0)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Campaign", x=["Campaign"], y=[base_val],
            marker_color=c1, text=[fmt(base_val)], textposition="outside",
        ))
        fig.add_trace(go.Bar(
            name="Incremental", x=["Incremental"], y=[incr_val],
            marker_color=c2, text=[fmt(incr_val)], textposition="outside",
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color="#cdd6f4")),
            barmode="group", showlegend=False, **CHART_BASE,
        )
        col_ui.plotly_chart(fig, use_container_width=True)

# ── 4. TREND LINES (Campaign Week vs Base Week) ───────────────────────────────
present_lines = [(t, c, b) for t, c, b in LINE_PAIRS if c in df.columns and b in df.columns]
if present_lines:
    st.markdown('<div class="section-title">Campaign Week vs Base Week</div>', unsafe_allow_html=True)
    per_row = 3
    for row_start in range(0, len(present_lines), per_row):
        chunk = present_lines[row_start:row_start + per_row]
        cols = st.columns(per_row)
        for col_ui, (title, camp_col, base_col), (c_camp, c_base) in zip(
            cols, chunk, LINE_COLORS[row_start:]
        ):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=sel_df[camp_col], mode="lines+markers",
                line=dict(color=c_camp, width=2), marker=dict(size=5), name="Campaign Week",
            ))
            fig.add_trace(go.Scatter(
                x=dates, y=sel_df[base_col], mode="lines+markers",
                line=dict(color=c_base, width=2, dash="dot"), marker=dict(size=5), name="Base Week",
            ))
            fig.update_layout(
                title=dict(text=title, font=dict(size=13, color="#cdd6f4")),
                showlegend=True,
                legend=dict(
                    orientation="h", x=0, y=1.15,
                    font=dict(size=11, color="#cdd6f4"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                **{k: v for k, v in CHART_BASE.items() if k != "legend"},
            )
            col_ui.plotly_chart(fig, use_container_width=True)

# ── 5. U2T TREND ──────────────────────────────────────────────────────────────
u2t_col_name = next((c for c in df.columns if c.strip().lower() == "u2t"), None)
if u2t_col_name:
    st.markdown('<div class="section-title">U2T Trend</div>', unsafe_allow_html=True)
    left, _ = st.columns([1, 2])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=sel_df[u2t_col_name], mode="lines+markers",
        line=dict(color="#f9e2af", width=2), marker=dict(size=5), name="U2T",
    ))
    fig.update_layout(
        title=dict(text="U2T", font=dict(size=13, color="#cdd6f4")),
        showlegend=False, **CHART_BASE,
    )
    left.plotly_chart(fig, use_container_width=True)

# ── 6. DATA TABLE ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">All Data</div>', unsafe_allow_html=True)


def highlight_row(row_data):
    base      = "background-color: #1e1e2e; color: #cdd6f4"
    highlight = "background-color: #313244; color: #89b4fa; font-weight: 600"
    return [highlight if row_data.get(cam_col) == selected else base] * len(row_data)


display_df = df.drop(columns=["_dt"], errors="ignore").copy()
styled = display_df.style.apply(highlight_row, axis=1)
st.dataframe(styled, width="stretch", hide_index=True)

st.download_button(
    label="⬇ Download data as CSV",
    data=df.drop(columns=["_dt"], errors="ignore").to_csv(index=False).encode(),
    file_name="campaign_data.csv",
    mime="text/csv",
)
