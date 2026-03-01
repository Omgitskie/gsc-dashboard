import streamlit as st
from datetime import date, timedelta

from utils.classify import ALL_SEGMENTS, STORE_LOCATIONS
from utils.gsc import fetch_gsc_data
from views import overview, winners_losers, new_lost, brand, store_local, online_national, query_explorer, admin

st.set_page_config(
    page_title="P&C | Search Intelligence",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Unbounded:wght@700;800;900&display=swap');

/* ── RESET & BASE ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: #0A0E1A !important;
    color: #C8CDD8 !important;
}
.main { background: #0A0E1A !important; }
.block-container {
    padding: 0 4rem !important;
    max-width: 100% !important;
    background: #0A0E1A !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
div[data-testid="stSidebar"] { display: none; }
div[data-testid="collapsedControl"] { display: none; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0A0E1A; }
::-webkit-scrollbar-thumb { background: #FF2D78; border-radius: 4px; }

/* ── TOP NAV ── */
.nav-wrapper {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(10, 14, 26, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}
.nav-brand {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.1rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 3px;
}
.nav-brand .pink { color: #FF2D78; }
.nav-brand .sub {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.6rem;
    font-weight: 500;
    color: rgba(200,205,216,0.35);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-left: 10px;
    margin-top: 2px;
}
.nav-links {
    display: flex;
    align-items: center;
    gap: 4px;
}
.nav-link {
    font-size: 0.82rem;
    font-weight: 500;
    color: rgba(200,205,216,0.5);
    padding: 7px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    white-space: nowrap;
    text-decoration: none;
}
.nav-link:hover {
    color: #FFFFFF;
    background: rgba(255,255,255,0.05);
}
.nav-link.active {
    color: #FF2D78;
    background: rgba(255, 45, 120, 0.1);
    border-color: rgba(255, 45, 120, 0.2);
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-pill {
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(200,205,216,0.4);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 5px 10px;
    letter-spacing: 0.3px;
}

/* ── PAGE CONTENT WRAPPER ── */
.page-content {
    padding: 40px 64px;
    animation: fadeUp 0.4s ease forwards;
}

/* ── CONTROL BAR ── */
.control-bar {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 16px 24px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 16px;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeUp 0.5s ease forwards;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #FF2D78 50%, transparent 100%);
    opacity: 0.5;
}
.metric-card:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,45,120,0.25);
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(255,45,120,0.08);
}
.metric-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(200,205,216,0.35);
    margin-bottom: 12px;
}
.metric-value {
    font-family: 'Unbounded', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1;
    letter-spacing: -2px;
    margin-bottom: 10px;
}
.metric-delta {
    font-size: 0.78rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
}
.delta-up { color: #00D68F; }
.delta-down { color: #FF4D6D; }

/* ── SECTION HEADER ── */
.section-header {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(200,205,216,0.3);
    margin: 40px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

/* ── PAGE TITLE ── */
.page-title {
    font-family: 'Unbounded', sans-serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 6px;
}
.page-title .pink { color: #FF2D78; }
.page-subtitle {
    font-size: 0.83rem;
    color: rgba(200,205,216,0.35);
    margin-bottom: 36px;
    font-weight: 400;
    letter-spacing: 0.2px;
}

/* ── SEGMENT CHIPS ── */
.seg-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 14px 16px;
    text-align: left;
    transition: all 0.25s ease;
    animation: fadeUp 0.5s ease forwards;
}
.seg-chip:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(255,45,120,0.2);
}
.seg-chip-name {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: rgba(200,205,216,0.4);
}
.seg-chip-value {
    font-family: 'Unbounded', sans-serif;
    font-size: 1.5rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -1px;
    line-height: 1.1;
    margin: 4px 0;
}
.seg-chip-delta { font-size: 0.75rem; font-weight: 600; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: rgba(200,205,216,0.4) !important;
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

/* ── DATAFRAME ── */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #C8CDD8 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #FF2D78 0%, #FF6BA0 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px !important;
    padding: 10px 22px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(255,45,120,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,45,120,0.45) !important;
}

/* ── DOTTED DIVIDER (Maze style) ── */
.dot-divider {
    border: none;
    border-top: 1px dashed rgba(255,255,255,0.08);
    margin: 32px 0;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
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
    background: #0A0E1A;
    animation: fadeUp 0.3s ease;
}
.load-eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #FF2D78;
    margin-bottom: 28px;
    animation: pulse 2s ease infinite;
}
.load-headline {
    font-family: 'Unbounded', sans-serif;
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -2px;
    max-width: 640px;
    background: linear-gradient(135deg, #FFFFFF 20%, #FF2D78 60%, #FFFFFF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
    margin-bottom: 16px;
}
.load-sub {
    font-size: 0.9rem;
    color: rgba(200,205,216,0.3);
    margin-bottom: 56px;
    letter-spacing: 1px;
    font-weight: 400;
}
.load-bar-track {
    width: 180px;
    height: 1px;
    background: rgba(255,255,255,0.08);
    border-radius: 1px;
    overflow: hidden;
}
.load-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF2D78, #FF6BA0);
    animation: loadBar 2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
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
    import time
    time.sleep(2)
    st.session_state.loaded = True
    st.rerun()

# ── NAV PAGES ────────────────────────────────────────────────
NAV_PAGES = [
    ("Overview", "🏠"),
    ("Winners & Losers", "🏆"),
    ("New & Lost", "🆕"),
    ("Brand", "🏷️"),
    ("Store & Local", "📍"),
    ("Online & National", "🌐"),
    ("Query Explorer", "🔍"),
    ("Admin", "⚙️"),
]

if "page" not in st.session_state:
    st.session_state.page = "Overview"


# ── NAV BUTTONS ──────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    gap: 16px !important;
}

div[data-testid="stHorizontalBlock"]:first-of-type {
    background: rgba(10, 14, 26, 0.95);
    backdrop-filter: blur(20px);
    padding: 0 48px;
    position: sticky;
    top: 0;
    z-index: 1000;
    margin-bottom: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: rgba(200,205,216,0.5) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button:hover {
    color: #FFFFFF !important;
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(255,255,255,0.2) !important;
    transform: none !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button:hover {
    color: #FFFFFF !important;
    background: rgba(255,255,255,0.05) !important;
    transform: none !important;
    box-shadow: none !important;
}
/* hide button text when replaced by active div */
div[data-testid="stHorizontalBlock"] > div > div > div > .stButton > button p {
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(NAV_PAGES))
for i, (label, icon) in enumerate(NAV_PAGES):
    with nav_cols[i]:
        is_active = st.session_state.page == label
        if is_active:
            st.markdown(f"""
            <div style="border:1px solid #FF2D78; border-radius:8px; padding:10px 14px;
                        text-align:center; color:#FF2D78; font-family:'Plus Jakarta Sans',sans-serif;
                        font-size:0.82rem; font-weight:700; background:rgba(255,45,120,0.08);">
                {label}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label
                st.rerun()

# ── DATE & FILTER CONTROLS ───────────────────────────────────
with st.expander("⚙️ Date Range & Filters", expanded=False):
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        date_option = st.selectbox("Period", [
            "Last 7 days", "Last 2 weeks", "Last 30 days",
            "Last 3 months", "Last 6 months", "Last 12 months", "Custom"
        ])
    with col2:
        segment_filter = st.multiselect("Segments", ALL_SEGMENTS,
            default=[s for s in ALL_SEGMENTS if s not in ["Other", "Noise", "Not Relevant"]]
        )
    with col3:
        store_filter = st.selectbox("Store", ["All Stores"] + list(STORE_LOCATIONS.keys()))

today = date.today()
if date_option == "Last 7 days":
    start = today - timedelta(days=7)
    end = today - timedelta(days=1)
elif date_option == "Last 2 weeks":
    start = today - timedelta(days=14)
    end = today - timedelta(days=1)
elif date_option == "last 30 days":
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
prev_end = start - timedelta(days=1)
prev_start = prev_end - timedelta(days=period_days)

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
    overview.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Winners & Losers":
    winners_losers.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "New & Lost":
    new_lost.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Brand":
    brand.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Store & Local":
    store_local.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Online & National":
    online_national.render(df_filtered, df_prev_filtered, start_str, end_str, period_days)
elif page == "Query Explorer":
    query_explorer.render(df_filtered, start_str, end_str)
elif page == "Admin":
    admin.render(df)

st.markdown('</div>', unsafe_allow_html=True)
