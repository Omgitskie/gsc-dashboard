import streamlit as st
from datetime import date, timedelta

from utils.classify import ALL_SEGMENTS, STORE_LOCATIONS
from utils.gsc import fetch_gsc_data
from pages import overview, winners_losers, new_lost, brand, store_local, online_national, query_explorer, admin

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="P&C | Search Intelligence",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PREMIUM STYLING ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #080B12;
        color: #E8EAF0;
    }
    .main { background: #080B12; }
    .block-container { padding: 2rem 2.5rem; background: #080B12; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #120818 60%, #0D0511 100%);
        border-right: 1px solid rgba(255, 45, 120, 0.15);
    }
    div[data-testid="stSidebar"] * { color: #E8EAF0 !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #080B12; }
    ::-webkit-scrollbar-thumb { background: #FF2D78; border-radius: 3px; }

    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        animation: fadeSlideUp 0.5s ease forwards;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #FF2D78, transparent);
        opacity: 0.7;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 45, 120, 0.3);
        box-shadow: 0 20px 40px rgba(255, 45, 120, 0.1);
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1;
        margin: 8px 0 6px 0;
        letter-spacing: -1px;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: rgba(232, 234, 240, 0.45);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }
    .metric-delta-positive { font-size: 0.82rem; color: #00E5A0; font-weight: 500; }
    .metric-delta-negative { font-size: 0.82rem; color: #FF4D6D; font-weight: 500; }

    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 28px 0 16px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 45, 120, 0.2);
        letter-spacing: 0.3px;
    }

    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.9rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 0.83rem;
        color: rgba(232, 234, 240, 0.4);
        margin-bottom: 28px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: rgba(232, 234, 240, 0.5) !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 45, 120, 0.15) !important;
        color: #FF2D78 !important;
        border: 1px solid rgba(255, 45, 120, 0.25) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #FF2D78, #FF6B9D) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 45, 120, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 45, 120, 0.5) !important;
    }

    hr { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 24px 0; }

    .sidebar-label {
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: rgba(232,234,240,0.3) !important;
        margin-bottom: 8px;
        margin-top: 4px;
        display: block;
    }

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes loadBar {
        0% { width: 0%; }
        60% { width: 75%; }
        100% { width: 100%; }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
</style>
""", unsafe_allow_html=True)

# ── LOADING SCREEN ───────────────────────────────────────────
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <style>
    .loading-wrap {
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        min-height: 80vh; text-align: center;
        animation: fadeIn 0.4s ease;
    }
    .load-brand {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 5px; text-transform: uppercase;
        color: #FF2D78; margin-bottom: 24px;
        animation: pulse 2s ease infinite;
    }
    .load-headline {
        font-family: 'Syne', sans-serif;
        font-size: 3rem; font-weight: 800;
        line-height: 1.15; max-width: 580px;
        background: linear-gradient(135deg, #FFFFFF 0%, #FF2D78 50%, #FFFFFF 100%);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
        margin-bottom: 14px;
    }
    .load-sub {
        font-size: 0.95rem;
        color: rgba(232,234,240,0.35);
        margin-bottom: 52px;
        letter-spacing: 0.5px;
    }
    .load-bar-track {
        width: 200px; height: 2px;
        background: rgba(255,255,255,0.08);
        border-radius: 2px; overflow: hidden;
    }
    .load-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #FF2D78, #FF6B9D);
        border-radius: 2px;
        animation: loadBar 1.8s ease forwards;
    }
    </style>
    <div class="loading-wrap">
        <div class="load-brand">Pulse &amp; Cocktails</div>
        <div class="load-headline">Turning searches<br>into strategy</div>
        <div class="load-sub">Search Intelligence Dashboard</div>
        <div class="load-bar-track"><div class="load-bar-fill"></div></div>
    </div>
    """, unsafe_allow_html=True)
    import time
    time.sleep(2)
    st.session_state.loaded = True
    st.rerun()

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <div style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:#FFFFFF;">
            P<span style="color:#FF2D78;">&</span>C
        </div>
        <div style="font-size:0.68rem; color:rgba(232,234,240,0.3); letter-spacing:2px; text-transform:uppercase; margin-top:2px;">
            Search Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px; background:rgba(255,45,120,0.2); margin-bottom:16px;"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-label">Navigation</span>', unsafe_allow_html=True)

    page = st.radio("", [
        "🏠 Overview",
        "🏆 Winners & Losers",
        "🆕 New & Lost Keywords",
        "🏷️ Brand Performance",
        "📍 Store & Local",
        "🌐 Online & National",
        "🔍 Query Explorer",
        "⚙️ Admin & Classifications"
    ], label_visibility="collapsed")

    st.markdown('<div style="height:1px; background:rgba(255,255,255,0.06); margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-label">Date Range</span>', unsafe_allow_html=True)

    date_option = st.selectbox("", [
        "Last 7 days", "Last 2 weeks", "Last month",
        "Last 3 months", "Last 6 months", "Last 12 months", "Custom"
    ], label_visibility="collapsed")

    today = date.today()
    if date_option == "Last 7 days":
        start = today - timedelta(days=7)
        end = today - timedelta(days=1)
    elif date_option == "Last 2 weeks":
        start = today - timedelta(days=14)
        end = today - timedelta(days=1)
    elif date_option == "Last month":
        start = today - timedelta(days=30)
        end = today - timedelta(days=1)
    elif date_option == "Last 3 months":
        start = today - timedelta(days=90)
        end = today - timedelta(days=1)
    elif date_option == "Last 6 months":
        start = today - timedelta(days=180)
        end = today - timedelta(days=1)
    elif date_option == "Last 12 months":
        start = today - timedelta(days=365)
        end = today - timedelta(days=1)
    else:
        start = st.date_input("Start date", today - timedelta(days=90))
        end = st.date_input("End date", today - timedelta(days=1))

    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    period_days = (end - start).days
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days)

    st.markdown('<div style="height:1px; background:rgba(255,255,255,0.06); margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-label">Filters</span>', unsafe_allow_html=True)

    segment_filter = st.multiselect("", ALL_SEGMENTS,
        default=[s for s in ALL_SEGMENTS if s not in ["Other", "Noise", "Not Relevant"]],
        label_visibility="collapsed"
    )
    store_filter = st.selectbox("", ["All Stores"] + list(STORE_LOCATIONS.keys()), label_visibility="collapsed")

    st.markdown('<div style="height:1px; background:rgba(255,255,255,0.06); margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.7rem; color:rgba(232,234,240,0.25);">{start_str} → {end_str}</div>', unsafe_allow_html=True)

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner("Fetching search data..."):
    try:
        df = fetch_gsc_data(start_str, end_str)
        df_prev = fetch_gsc_data(
            prev_start.strftime("%Y-%m-%d"),
            prev_end.strftime("%Y-%m-%d")
        )
    except Exception as e:
        st.error(f"Data loading error: {e}")
        import pandas as pd
        df = pd.DataFrame()
        df_prev = pd.DataFrame()

if df.empty:
    st.error("No data loaded. Check your GSC credentials and property URL in Streamlit secrets.")
    st.stop()

# ── APPLY FILTERS ────────────────────────────────────────────
df_filtered = df[df["segment"].isin(segment_filter)].copy()
df_prev_filtered = df_prev[df_prev["segment"].isin(segment_filter)].copy()

if store_filter != "All Stores":
    df_filtered = df_filtered[df_filtered["store"] == store_filter]
    df_prev_filtered = df_prev_filtered[df_prev_filtered["store"] == store_filter]

df_filtered = df_filtered[~df_filtered["segment"].isin(["Noise", "Not Relevant"])]
df_prev_filtered = df_prev_filtered[~df_prev_filtered["segment"].isin(["Noise", "Not Relevant"])]

# ── ROUTING ──────────────────────────────────────────────────
if page == "🏠 Overview":
    overview.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "🏆 Winners & Losers":
    winners_losers.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "🆕 New & Lost Keywords":
    new_lost.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "🏷️ Brand Performance":
    brand.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "📍 Store & Local":
    store_local.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "🌐 Online & National":
    online_national.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "🔍 Query Explorer":
    query_explorer.render(df_filtered, start_str, end_str)
elif page == "⚙️ Admin & Classifications":
    admin.render(df)
