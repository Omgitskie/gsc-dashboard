import streamlit as st
from datetime import date, timedelta

from utils.classify import ALL_SEGMENTS, STORE_LOCATIONS
from utils.gsc import fetch_gsc_data
from views import overview, winners_losers, new_lost, categories, query_explorer, admin

st.set_page_config(
    page_title="P&C | Search Intelligence",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Unbounded:wght@700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #E2E4EC !important;
}

.main, .main > div, section.main, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%, rgba(255,45,120,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 100% 100%, rgba(120,40,200,0.15) 0%, transparent 60%),
        linear-gradient(135deg, #0A0D1F 0%, #0D0A22 40%, #0A0E2A 70%, #080B1E 100%) !important;
    background-attachment: fixed !important;
    min-height: 100vh;
}

.block-container {
    padding: 0 0 60px 0 !important;
    max-width: 100% !important;
    background: transparent !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
div[data-testid="stSidebar"] { display: none; }
div[data-testid="collapsedControl"] { display: none; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,45,120,0.5); border-radius: 4px; }

/* ── NAV ROW ── */
div[data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type {
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    padding: 10px 2rem !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    margin-bottom: 0 !important;
    gap: 8px !important;
}

/* ── NAV BUTTONS ── */
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: rgba(226,228,236,0.5) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 9px 12px !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button:hover {
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── PAGE CONTENT ── */
.page-content {
    padding: 36px 3.5rem;
    animation: fadeUp 0.35s ease forwards;
}

[data-testid="stAppViewContainer"] > section > div {
    padding-left: 3.5rem !important;
    padding-right: 3.5rem !important;
}

/* ── GLASS METRIC CARD ── */
.metric-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    height: 100%;
}
.metric-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.01) 100%);
    pointer-events: none;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 20%; right: 20%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,45,120,0.8), transparent);
}
.metric-card:hover {
    background: rgba(255,255,255,0.09);
    border-color: rgba(255,45,120,0.3);
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 0 40px rgba(255,45,120,0.08);
}
.metric-label {
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: rgba(226,228,236,0.4);
    margin-bottom: 14px;
}
.metric-value {
    font-family: 'Unbounded', sans-serif;
    font-size: 2.1rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1;
    letter-spacing: -2px;
    margin-bottom: 10px;
}
.metric-delta { font-size: 0.76rem; font-weight: 600; margin-bottom: 2px; }
.metric-prev { font-size: 0.72rem; color: rgba(226,228,236,0.3); font-weight: 400; }
.delta-up { color: #00E096; }
.delta-down { color: #FF4D6D; }

/* ── GLASS CONTENT CARD ── */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    padding: 28px;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
}
.glass-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
    pointer-events: none;
}

/* ── SEGMENT CHIPS ── */
.seg-chip {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}
.seg-chip:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,45,120,0.25);
    transform: translateY(-2px);
}
.seg-chip-name {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(226,228,236,0.4);
    margin-bottom: 8px;
}
.seg-chip-value {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.5rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 6px;
}
.seg-chip-delta { font-size: 0.73rem; font-weight: 600; }

/* ── PAGE TITLE ── */
.page-title {
    font-family: 'Unbounded', sans-serif;
    font-size: 2.1rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 6px;
}
.page-title .pink { color: #FF2D78; }
.page-subtitle {
    font-size: 0.82rem;
    color: rgba(226,228,236,0.9);
    margin-bottom: 28px;
    font-weight: 400;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(226,228,236,0.9);
    margin: 32px 0 16px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.06), transparent);
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: rgba(226,228,236,0.4) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    border-radius: 0 !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    color: #FF2D78 !important;
    border-bottom: 2px solid #FF2D78 !important;
    background: transparent !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #E2E4EC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── EXPANDER ── */
.stExpander > details > summary {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 14px 20px !important;
    color: rgba(226,228,236,0.55) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
}
.stExpander > details > div {
    background: rgba(255,255,255,0.03) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-top: none !important;
    border-bottom-left-radius: 12px !important;
    border-bottom-right-radius: 12px !important;
    padding: 20px !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: rgba(226,228,236,0.7) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 10px 22px !important;
    transition: all 0.25s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.18) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF2D78 0%, #FF6BA0 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(255,45,120,0.3) !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* ── DIVIDER ── */
.dot-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 28px 0;
}

/* ── CATEGORY TOGGLE BUTTONS ── */
.cat-btn-active {
    display: inline-block;
    border: 1px solid #FF2D78;
    border-radius: 10px;
    padding: 9px 16px;
    text-align: center;
    color: #FF2D78;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    background: rgba(255,45,120,0.1);
    backdrop-filter: blur(10px);
    cursor: pointer;
    width: 100%;
}
.cat-btn-inactive {
    display: inline-block;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 10px;
    padding: 9px 16px;
    text-align: center;
    color: rgba(226,228,236,0.5);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(255,255,255,0.04);
    cursor: pointer;
    width: 100%;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes loadBar {
    0% { width: 0%; }
    70% { width: 80%; }
    100% { width: 100%; }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── LOADING SCREEN ── */
.loading-wrap {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%, rgba(255,45,120,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 100% 100%, rgba(120,40,200,0.18) 0%, transparent 60%),
        linear-gradient(135deg, #0A0D1F 0%, #0D0A22 50%, #0A0E2A 100%);
}
.load-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: #FF2D78;
    margin-bottom: 28px;
    animation: pulse 2s ease infinite;
}
.load-headline {
    font-family: 'Unbounded', sans-serif;
    font-size: 3.4rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -2px;
    max-width: 620px;
    background: linear-gradient(135deg, #FFFFFF 15%, #FF2D78 55%, #FFFFFF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
    margin-bottom: 14px;
}
.load-sub {
    font-size: 0.88rem;
    color: rgba(226,228,236,0.3);
    margin-bottom: 52px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 500;
}
.load-bar-track {
    width: 160px;
    height: 1px;
    background: rgba(255,255,255,0.08);
    border-radius: 1px;
    overflow: hidden;
}
.load-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF2D78, #C020FF);
    animation: loadBar 2.2s cubic-bezier(0.4,0,0.2,1) forwards;
}

[data-testid="stMain"] {
    padding-left: 3.5rem !important;
    padding-right: 3.5rem !important;
}

div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button:empty {
    opacity: 0 !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    z-index: 10 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

# ── LOADING SCREEN ───────────────────────────────────────────
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <div class="loading-wrap">
        <div class="load-eyebrow">Pulse &amp; Cocktails</div>
        <div class="load-headline">Every search<br>tells a story</div>
        <div class="load-sub">Search Intelligence Dashboard</div>
        <div class="load-bar-track"><div class="load-bar-fill"></div></div>
    </div>
    """, unsafe_allow_html=True)
    _end = date.today() - timedelta(days=1)
    _start = _end - timedelta(days=90)
    fetch_gsc_data(_start.strftime("%Y-%m-%d"), _end.strftime("%Y-%m-%d"))
    st.session_state.loaded = True
    st.rerun()

# ── SESSION STATE ────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

NAV_PAGES = [
    "Overview", "Winners & Losers", "New & Lost",
    "Categories", "Query Explorer", "Admin"
]

# ── BRAND HEADER ─────────────────────────────────────────────
st.markdown("""
<div style="padding:14px 2rem 0 2rem; display:flex; align-items:center; gap:10px;">
    <div style="font-family:'Unbounded',sans-serif; font-size:1rem; font-weight:900; color:#FFFFFF;">
        P<span style="color:#FF2D78;">&</span>C
    </div>
    <div style="font-size:0.62rem; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; color:rgba(226,228,236,0.25);">
        Search Intelligence
    </div>
</div>
""", unsafe_allow_html=True)

# ── NAV BUTTONS ──────────────────────────────────────────────
nav_cols = st.columns(len(NAV_PAGES))
for i, label in enumerate(NAV_PAGES):
    with nav_cols[i]:
        is_active = st.session_state.page == label
        if is_active:
            st.markdown(f"""
            <div style="border:1px solid #FF2D78; border-radius:10px; padding:9px 12px;
                text-align:center; color:#FF2D78; font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.8rem; font-weight:700; background:rgba(255,45,120,0.1);
                backdrop-filter:blur(10px);">{label}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()

# ── DATE & FILTER CONTROLS ───────────────────────────────────
_active_period = st.session_state.get("date_option", "Last 3 months")
_active_compare = st.session_state.get("compare_option", "Previous Period")

with st.expander(
    f"Date Range & Filters  ·  {_active_period}  ·  vs {_active_compare}",
    expanded=False
):
    col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
    with col1:
        date_option = st.selectbox("Period", [
            "Last 7 days", "Last 2 weeks", "Last 30 days",
            "Last 3 months", "Last 6 months", "Last 12 months", "Custom"
        ], index=["Last 7 days", "Last 2 weeks", "Last 30 days", "Last 3 months",
                  "Last 6 months", "Last 12 months", "Custom"].index(
            st.session_state.get("date_option", "Last 3 months")
        ))
        st.session_state["date_option"] = date_option
    with col2:
        compare_option = st.selectbox("Compare with", [
            "Previous Period", "Same Period Last Year"
        ], index=["Previous Period", "Same Period Last Year"].index(
            st.session_state.get("compare_option", "Previous Period")
        ))
        st.session_state["compare_option"] = compare_option
    with col3:
        segment_filter = st.multiselect("Segments", ALL_SEGMENTS,
            default=[s for s in ALL_SEGMENTS if s not in ["Other", "Noise", "Not Relevant"]]
        )
    with col4:
        store_filter = st.selectbox("Store", ["All Stores"] + list(STORE_LOCATIONS.keys()))

today = date.today()
if date_option == "Last 7 days":
    start = today - timedelta(days=7)
    end = today - timedelta(days=1)
elif date_option == "Last 2 weeks":
    start = today - timedelta(days=14)
    end = today - timedelta(days=1)
elif date_option == "Last 30 days":
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
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start date", today - timedelta(days=90))
    with col2:
        end = st.date_input("End date", today - timedelta(days=1))

start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")
period_days = (end - start).days

# ── COMPARISON PERIOD ────────────────────────────────────────
if compare_option == "Previous Period":
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days)
else:  # Same Period Last Year
    prev_start = start - timedelta(days=365)
    prev_end = end - timedelta(days=365)

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner(""):
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
    st.error("No data loaded. Check your GSC credentials.")
    st.stop()

# ── APPLY FILTERS ────────────────────────────────────────────
df_filtered = df[df["segment"].isin(segment_filter)].copy()
df_prev_filtered = df_prev[df_prev["segment"].isin(segment_filter)].copy()

if store_filter != "All Stores":
    df_filtered = df_filtered[df_filtered["store"] == store_filter]
    df_prev_filtered = df_prev_filtered[df_prev_filtered["store"] == store_filter]

df_filtered = df_filtered[~df_filtered["segment"].isin(["Noise", "Not Relevant"])]
df_prev_filtered = df_prev_filtered[~df_prev_filtered["segment"].isin(["Noise", "Not Relevant"])]

# ── PAGE CONTENT ─────────────────────────────────────────────
st.markdown('<div class="page-content">', unsafe_allow_html=True)

page = st.session_state.page

if page == "Overview":
    overview.render(df_filtered, df_prev_filtered, start_str, end_str, period_days, compare_option)
elif page == "Winners & Losers":
    winners_losers.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "New & Lost":
    new_lost.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Categories":
    categories.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Query Explorer":
    query_explorer.render(df_filtered, start_str, end_str)
elif page == "Admin":
    admin.render(df)

st.markdown('</div>', unsafe_allow_html=True)
