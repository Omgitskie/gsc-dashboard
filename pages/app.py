import streamlit as st
from datetime import date, timedelta

from utils.classify import ALL_SEGMENTS, STORE_LOCATIONS
from utils.gsc import fetch_gsc_data
from pages import overview, winners_losers, new_lost, brand, store_local, online_national, query_explorer, admin

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="P&C | GSC Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLING ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1E3A5F; }
    .metric-label { font-size: 0.85rem; color: #666; margin-bottom: 5px; }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1E3A5F;
        margin: 20px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 3px solid #2E86AB;
    }
    div[data-testid="stSidebar"] { background-color: #1E3A5F; }
    div[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 GSC Dashboard")
    st.markdown("### Pulse & Cocktails")
    st.markdown("---")

    page = st.radio("Navigate", [
        "🏠 Overview",
        "🏆 Winners & Losers",
        "🆕 New & Lost Keywords",
        "🏷️ Brand Performance",
        "📍 Store & Local",
        "🌐 Online & National",
        "🔍 Query Explorer",
        "⚙️ Admin & Classifications"
    ])

    st.markdown("---")
    st.markdown("### Date Range")

    date_option = st.selectbox("Period", [
        "Last 7 days",
        "Last 2 weeks",
        "Last month",
        "Last 3 months",
        "Last 6 months",
        "Last 12 months",
        "Custom"
    ])

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

    st.markdown("---")
    st.markdown("### Filters")
    segment_filter = st.multiselect(
        "Segments", ALL_SEGMENTS,
        default=[s for s in ALL_SEGMENTS if s not in ["Other", "Noise", "Not Relevant"]]
    )
    store_filter = st.selectbox("Store Location", ["All Stores"] + list(STORE_LOCATIONS.keys()))

    st.markdown("---")
    st.caption(f"Data: {start_str} → {end_str}")

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner("Loading GSC data..."):
    try:
        df = fetch_gsc_data(start_str, end_str)
        df_prev = fetch_gsc_data(
            prev_start.strftime("%Y-%m-%d"),
            prev_end.strftime("%Y-%m-%d")
        )
    except Exception as e:
        st.error(f"Data loading error: {e}")
        df = __import__("pandas").DataFrame()
        df_prev = __import__("pandas").DataFrame()

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
