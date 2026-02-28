import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Pulse & Cocktails | GSC Dashboard",
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
    .metric-delta-up { color: #1A7A4A; font-size: 0.9rem; }
    .metric-delta-down { color: #C0392B; font-size: 0.9rem; }
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

# ── SEGMENT DEFINITIONS ──────────────────────────────────────
BRAND_PURE_TERMS = [
    "pulse and cocktail", "pulse & cocktail", "pulseandcocktail",
    "pulses and cocktail", "cocktails and pulse", "cocktail and pulse",
    "pulse n cocktail", "pulse snd cocktail", "pulse amd cocktail",
    "pulse and coctail", "pulse and cocktsil", "pulse and coxktail",
    "pulse and cicktail", "pulse and coktail", "pulse and.cocktail",
    "pulse and cocktsils", "pulse and covktail", "pulse and cocktaiks",
    "pulse and cocktials", "pulse andcocktail", "pulseandcocktails",
    "pulsea", "pulse snd", "pulse and cock"
]

NOISE_TERMS = [
    "gym", "radio", "rate", "yoga", "pilates", "clinic", "coaching",
    "leisure", "fitness", "hotel", "agency", "care", "sanctuary",
    "pulse bar", "pulse theatre", "pulse outlet", "pulse warehouse",
    "pulse rx", "mediterranean", "pulse rate", "pulse centre",
    "pulse agency", "pulse high heels", "pulse trainers", "pulse solo",
    "pulse ring", "electric pulse", "air pulse", "pulse pantees",
    "pulse butt", "pulse dick", "pulse stroker", "pulse vagina",
    "clitoris pulse", "butt pulse", "pulse bookin", "pulse mark",
    "pulse closing", "pulse open now", "pulse77", "pulse leisure",
    "pulse coaching", "pulse sanctuary", "pulse gym", "pulse radio",
    "pulse pilates", "pulse yoga", "pulse hotel", "pulse agency"
]

STORE_LOCATIONS = {
    "A1 North (Pontefract/Wentbridge)": ["pontefract", "wentbridge", "a1 north", "a1 northbound"],
    "A1 South (Grantham)": ["grantham", "sandy", "a1m", "a1 south"],
    "A1 (General)": ["a1 sex shop", "sex shop a1", "sex shop on a1", "sex shops on a1", "a1 sex shops"],
    "A12 / Essex (Rivenhall)": ["a12", "rivenhall", "witham", "essex", "colchester", "chelmsford"],
    "A38 / Lichfield": ["a38", "lichfield"],
    "A63 / Hull Brough": ["a63", "brough"],
    "Bradford": ["bradford"],
    "Cheltenham": ["cheltenham", "gloucester"],
    "Gateshead / Newcastle": ["gateshead", "newcastle", "blaydon", "north east"],
    "Hull": ["hull"],
    "Ipswich": ["ipswich"],
    "Kettering": ["kettering"],
    "Leeds": ["leeds"],
    "Lincoln / Saxilby": ["lincoln", "saxilby"],
    "Rotherham": ["rotherham"],
    "Scunthorpe": ["scunthorpe"],
    "Sheffield": ["sheffield"],
    "Wolverhampton": ["wolverhampton", "west midlands"],
    "Solihull (Closed)": ["solihull"],
}

NEAR_ME_TERMS = [
    "near me", "nearby", "nearest", "closest", "close to me",
    "local", "near by", "nwar me", "nesr me", "nere me", "mear me",
    "next to me", "around me", "near.me", "nearme", "nesr", "nere",
    "near mr", "near ms", "near mw", "nea rme"
]

ONLINE_TERMS = [
    "online", " uk", "delivery", "next day", "same day",
    "website", "on line", "on-line", "internet"
]

# ── SEGMENT CLASSIFIER ───────────────────────────────────────
def classify_query(query):
    q = query.lower().strip()

    # Check noise first
    if any(n in q for n in NOISE_TERMS):
        if not any(b in q for b in BRAND_PURE_TERMS):
            return "Noise", None

    # Brand pure
    is_brand = any(b in q for b in BRAND_PURE_TERMS)

    # Check store locations
    for store, terms in STORE_LOCATIONS.items():
        for term in terms:
            if term in q:
                # Exclusions
                if store == "A63 / Hull Brough" and "middlesbrough" in q:
                    continue
                if store == "Hull" and "solihull" in q:
                    continue
                if is_brand:
                    return "Brand + Location", store
                else:
                    return "Store & Local", store

    if is_brand:
        return "Brand (Pure)", None

    # Near me
    if any(t in q for t in NEAR_ME_TERMS):
        return "Store Intent (Near Me)", None

    # Online/national
    if any(t in q for t in ONLINE_TERMS):
        return "Online / National", None

    # Generic sex shop
    if "sex shop" in q or "sex shops" in q or "adult shop" in q or "adult store" in q:
        return "Generic Sex Shop", None

    return "Other", None

# ── GSC CONNECTION ───────────────────────────────────────────
@st.cache_resource
def get_gsc_service():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_gsc_data(start_date, end_date):
    service = get_gsc_service()
    if not service:
        return pd.DataFrame()

    property_url = st.secrets["gsc"]["property_url"]

    try:
        response = service.searchanalytics().query(
            siteUrl=property_url,
            body={
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query", "date"],
                "rowLimit": 25000,
                "dataState": "final"
            }
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            return pd.DataFrame()

        data = []
        for row in rows:
            query = row["keys"][0]
            date_val = row["keys"][1]
            segment, store = classify_query(query)
            data.append({
                "query": query,
                "date": date_val,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
                "segment": segment,
                "store": store
            })

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df

    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return pd.DataFrame()

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
        "🔍 Query Explorer"
    ])

    st.markdown("---")
    st.markdown("### Date Range")

    date_option = st.selectbox("Period", [
        "Last 3 months",
        "Last 6 months",
        "Last 12 months",
        "Custom"
    ])

    today = date.today()
    if date_option == "Last 3 months":
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

    # Previous period for comparison
    period_days = (end - start).days
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days)

    st.markdown("---")
    st.markdown("### Filters")
    segment_filter = st.multiselect("Segments", [
        "Brand (Pure)", "Brand + Location", "Store & Local",
        "Store Intent (Near Me)", "Online / National",
        "Generic Sex Shop", "Other"
    ], default=[
        "Brand (Pure)", "Brand + Location", "Store & Local",
        "Store Intent (Near Me)", "Online / National", "Generic Sex Shop"
    ])

    store_filter = st.selectbox("Store Location", ["All Stores"] + list(STORE_LOCATIONS.keys()))

    st.markdown("---")
    st.caption(f"Data: {start_str} → {end_str}")

# ── LOAD DATA ────────────────────────────────────────────────
with st.spinner("Loading GSC data..."):
    df = fetch_gsc_data(start_str, end_str)
    df_prev = fetch_gsc_data(
        prev_start.strftime("%Y-%m-%d"),
        prev_end.strftime("%Y-%m-%d")
    )

if df.empty:
    st.write("Secrets found:", list(st.secrets.keys()))
    st.write("GSC property:", st.secrets["gsc"]["property_url"])
    service = get_gsc_service()
    if service:
        st.success("GSC service connected ✓")
        try:
            test = service.searchanalytics().query(
                siteUrl=st.secrets["gsc"]["property_url"],
                body={
                    "startDate": "2025-11-01",
                    "endDate": "2025-11-30",
                    "dimensions": ["query"],
                    "rowLimit": 5
                }
            ).execute()
            st.write("API response:", test)
        except Exception as e:
            st.error(f"API call failed: {e}")
    else:
        st.error("GSC service failed to connect")
    st.stop()

# Apply filters
df_filtered = df[df["segment"].isin(segment_filter)].copy()
df_prev_filtered = df_prev[df_prev["segment"].isin(segment_filter)].copy()

if store_filter != "All Stores":
    df_filtered = df_filtered[df_filtered["store"] == store_filter]
    df_prev_filtered = df_prev_filtered[df_prev_filtered["store"] == store_filter]

# Exclude noise
df_filtered = df_filtered[df_filtered["segment"] != "Noise"]
df_prev_filtered = df_prev_filtered[df_prev_filtered["segment"] != "Noise"]

# ── HELPER FUNCTIONS ─────────────────────────────────────────
def delta_color(val):
    return "metric-delta-up" if val >= 0 else "metric-delta-down"

def delta_arrow(val):
    return "▲" if val >= 0 else "▼"

def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)

def scorecard(label, value, prev_value, format_fn=lambda x: f"{x:,}"):
    change = calc_change(value, prev_value)
    color = "#1A7A4A" if change >= 0 else "#C0392B"
    arrow = "▲" if change >= 0 else "▼"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{format_fn(value)}</div>
        <div style="color:{color}; font-size:0.9rem;">{arrow} {abs(change)}% vs prev period</div>
    </div>
    """, unsafe_allow_html=True)

# ── PAGE: OVERVIEW ───────────────────────────────────────────
if page == "🏠 Overview":
    st.markdown("# 📊 Overview")
    st.markdown(f"*{start_str} to {end_str} — compared to previous {period_days} days*")

    # Aggregate metrics
    curr_clicks = df_filtered["clicks"].sum()
    curr_imp = df_filtered["impressions"].sum()
    curr_ctr = round(df_filtered["clicks"].sum() / df_filtered["impressions"].sum() * 100, 2) if df_filtered["impressions"].sum() > 0 else 0
    curr_pos = round(df_filtered["position"].mean(), 1)

    prev_clicks = df_prev_filtered["clicks"].sum()
    prev_imp = df_prev_filtered["impressions"].sum()
    prev_ctr = round(df_prev_filtered["clicks"].sum() / df_prev_filtered["impressions"].sum() * 100, 2) if df_prev_filtered["impressions"].sum() > 0 else 0
    prev_pos = round(df_prev_filtered["position"].mean(), 1)

    # Scorecards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        scorecard("Total Clicks", curr_clicks, prev_clicks)
    with c2:
        scorecard("Total Impressions", curr_imp, prev_imp)
    with c3:
        scorecard("Avg CTR", curr_ctr, prev_ctr, lambda x: f"{x}%")
    with c4:
        scorecard("Avg Position", curr_pos, prev_pos, lambda x: f"{x}")

    st.markdown("---")

    # Weekly trend chart
    st.markdown('<div class="section-header">Clicks & Impressions Over Time</div>', unsafe_allow_html=True)
    weekly = df_filtered.copy()
    weekly["week"] = weekly["date"].dt.to_period("W").dt.start_time
    weekly_agg = weekly.groupby("week").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum")
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly_agg["week"], y=weekly_agg["Clicks"],
        name="Clicks", line=dict(color="#2E86AB", width=2.5),
        fill="tozeroy", fillcolor="rgba(46,134,171,0.1)"
    ))
    fig.add_trace(go.Scatter(
        x=weekly_agg["week"], y=weekly_agg["Impressions"],
        name="Impressions", line=dict(color="#E8A838", width=2.5),
        yaxis="y2"
    ))
    fig.update_layout(
        height=350, margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(title="Clicks", gridcolor="#f0f0f0"),
        yaxis2=dict(title="Impressions", overlaying="y", side="right", gridcolor="#f0f0f0"),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Segment breakdown
    st.markdown('<div class="section-header">Performance by Segment</div>', unsafe_allow_html=True)
    seg_curr = df_filtered.groupby("segment").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum")
    ).reset_index()
    seg_prev = df_prev_filtered.groupby("segment").agg(
        Clicks_prev=("clicks", "sum")
    ).reset_index()
    seg = seg_curr.merge(seg_prev, on="segment", how="left").fillna(0)
    seg["Change"] = seg.apply(lambda r: calc_change(r["Clicks"], r["Clicks_prev"]), axis=1)
    seg["Change %"] = seg["Change"].apply(lambda x: f"{'▲' if x >= 0 else '▼'} {abs(x)}%")

    cols = st.columns(len(seg))
    colors = {
        "Brand (Pure)": "#1E3A5F",
        "Brand + Location": "#2E86AB",
        "Store & Local": "#1A7A4A",
        "Store Intent (Near Me)": "#C07A00",
        "Online / National": "#8E44AD",
        "Generic Sex Shop": "#E74C3C"
    }
    for i, (_, row) in enumerate(seg.iterrows()):
        with cols[i]:
            color = colors.get(row["segment"], "#666")
            change_color = "#1A7A4A" if row["Change"] >= 0 else "#C0392B"
            st.markdown(f"""
            <div style="background:white; border-radius:10px; padding:15px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.08);
                        border-top: 4px solid {color}; text-align:center;">
                <div style="font-size:0.75rem; color:#666; margin-bottom:5px;">{row['segment']}</div>
                <div style="font-size:1.5rem; font-weight:700; color:#1E3A5F;">{int(row['Clicks']):,}</div>
                <div style="font-size:0.8rem; color:#888;">clicks</div>
                <div style="font-size:0.85rem; color:{change_color}; margin-top:5px;">{row['Change %']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Position trend
    st.markdown('<div class="section-header">Average Position Over Time</div>', unsafe_allow_html=True)
    pos_weekly = df_filtered.copy()
    pos_weekly["week"] = pos_weekly["date"].dt.to_period("W").dt.start_time
    pos_agg = pos_weekly.groupby("week").agg(Position=("position", "mean")).reset_index()
    pos_agg["Position"] = pos_agg["Position"].round(1)

    fig2 = px.line(pos_agg, x="week", y="Position", color_discrete_sequence=["#E74C3C"])
    fig2.update_traces(line=dict(width=2.5))
    fig2.update_yaxes(autorange="reversed", title="Avg Position (lower = better)", gridcolor="#f0f0f0")
    fig2.update_xaxes(title="")
    fig2.update_layout(
        height=280, margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="white", paper_bgcolor="white"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── PAGE: WINNERS & LOSERS ───────────────────────────────────
elif page == "🏆 Winners & Losers":
    st.markdown("# 🏆 Winners & Losers")
    st.markdown(f"*Comparing {start_str}–{end_str} vs previous {period_days} days*")

    # Aggregate by query for both periods
    curr_q = df_filtered.groupby(["query", "segment"]).agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        position=("position", "mean")
    ).reset_index()

    prev_q = df_prev_filtered.groupby(["query"]).agg(
        clicks_prev=("clicks", "sum"),
        position_prev=("position", "mean")
    ).reset_index()

    merged = curr_q.merge(prev_q, on="query", how="outer").fillna(0)
    merged["click_change"] = merged["clicks"] - merged["clicks_prev"]
    merged["click_change_pct"] = merged.apply(
        lambda r: calc_change(r["clicks"], r["clicks_prev"]), axis=1
    )
    merged["pos_change"] = (merged["position_prev"] - merged["position"]).round(1)
    merged["position"] = merged["position"].round(1)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Click Winners", "📉 Click Losers",
        "⬆️ Position Improvers", "⚠️ CTR Opportunities"
    ])

    with tab1:
        st.markdown('<div class="section-header">Biggest Click Increases</div>', unsafe_allow_html=True)
        winners = merged[merged["clicks_prev"] > 0].nlargest(20, "click_change")[
            ["query", "segment", "clicks", "clicks_prev", "click_change", "click_change_pct", "position"]
        ].copy()
        winners.columns = ["Query", "Segment", "Clicks (Now)", "Clicks (Prev)", "Change", "Change %", "Position"]
        winners["Change %"] = winners["Change %"].apply(lambda x: f"▲ {abs(x)}%")
        st.dataframe(winners, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-header">Biggest Click Drops</div>', unsafe_allow_html=True)
        losers = merged[merged["clicks_prev"] > 0].nsmallest(20, "click_change")[
            ["query", "segment", "clicks", "clicks_prev", "click_change", "click_change_pct", "position"]
        ].copy()
        losers.columns = ["Query", "Segment", "Clicks (Now)", "Clicks (Prev)", "Change", "Change %", "Position"]
        losers["Change %"] = losers["Change %"].apply(lambda x: f"▼ {abs(x)}%")
        st.dataframe(losers, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown('<div class="section-header">Biggest Position Improvements</div>', unsafe_allow_html=True)
        pos_up = merged[merged["position_prev"] > 0].nlargest(20, "pos_change")[
            ["query", "segment", "position", "position_prev", "pos_change", "clicks"]
        ].copy()
        pos_up.columns = ["Query", "Segment", "Position (Now)", "Position (Prev)", "Improvement", "Clicks"]
        st.dataframe(pos_up, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown('<div class="section-header">High Impressions, Low CTR — Opportunity List</div>', unsafe_allow_html=True)
        st.caption("These terms are visible but not getting clicked — title/description or position needs improving")
        opps = curr_q[curr_q["impressions"] > 50].copy()
        opps["ctr"] = (opps["clicks"] / opps["impressions"] * 100).round(2)
        opps = opps[opps["ctr"] < 5].sort_values("impressions", ascending=False).head(25)[
            ["query", "segment", "impressions", "clicks", "ctr", "position"]
        ]
        opps.columns = ["Query", "Segment", "Impressions", "Clicks", "CTR %", "Position"]
        st.dataframe(opps, use_container_width=True, hide_index=True)

# ── PAGE: NEW & LOST ─────────────────────────────────────────
elif page == "🆕 New & Lost Keywords":
    st.markdown("# 🆕 New & Lost Keywords")
    st.markdown(f"*Comparing {start_str}–{end_str} vs previous {period_days} days*")

    curr_queries = set(df_filtered["query"].unique())
    prev_queries = set(df_prev_filtered["query"].unique())

    new_queries = curr_queries - prev_queries
    lost_queries = prev_queries - curr_queries

    tab1, tab2 = st.tabs([f"🆕 New Keywords ({len(new_queries)})", f"❌ Lost Keywords ({len(lost_queries)})"])

    with tab1:
        st.caption("Queries appearing this period that had zero impressions in the previous period")
        new_df = df_filtered[df_filtered["query"].isin(new_queries)].groupby(
            ["query", "segment"]
        ).agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean")
        ).reset_index().sort_values("Clicks", ascending=False)
        new_df["Position"] = new_df["Position"].round(1)
        st.dataframe(new_df, use_container_width=True, hide_index=True)

    with tab2:
        st.caption("Queries that had impressions in the previous period but have disappeared this period")
        lost_df = df_prev_filtered[df_prev_filtered["query"].isin(lost_queries)].groupby(
            ["query", "segment"]
        ).agg(
            Clicks_prev=("clicks", "sum"),
            Impressions_prev=("impressions", "sum"),
            Position_prev=("position", "mean")
        ).reset_index().sort_values("Clicks_prev", ascending=False)
        lost_df["Position_prev"] = lost_df["Position_prev"].round(1)
        lost_df.columns = ["Query", "Segment", "Clicks (Last Period)", "Impressions (Last Period)", "Position (Last Period)"]
        st.dataframe(lost_df, use_container_width=True, hide_index=True)

# ── PAGE: BRAND PERFORMANCE ──────────────────────────────────
elif page == "🏷️ Brand Performance":
    st.markdown("# 🏷️ Brand Performance")

    brand_df = df_filtered[df_filtered["segment"].isin(["Brand (Pure)", "Brand + Location"])]
    brand_prev = df_prev_filtered[df_prev_filtered["segment"].isin(["Brand (Pure)", "Brand + Location"])]

    curr_clicks = brand_df["clicks"].sum()
    curr_imp = brand_df["impressions"].sum()
    curr_ctr = round(curr_clicks / curr_imp * 100, 2) if curr_imp > 0 else 0
    curr_pos = round(brand_df["position"].mean(), 1)

    prev_clicks = brand_prev["clicks"].sum()
    prev_imp = brand_prev["impressions"].sum()
    prev_ctr = round(prev_clicks / prev_imp * 100, 2) if prev_imp > 0 else 0
    prev_pos = round(brand_prev["position"].mean(), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1: scorecard("Brand Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Brand Impressions", curr_imp, prev_imp)
    with c3: scorecard("Brand CTR", curr_ctr, prev_ctr, lambda x: f"{x}%")
    with c4: scorecard("Brand Avg Position", curr_pos, prev_pos, lambda x: f"{x}")

    st.markdown("---")

    tab1, tab2 = st.tabs(["🏷️ Brand Pure", "📍 Brand + Location"])

    with tab1:
        pure_df = df_filtered[df_filtered["segment"] == "Brand (Pure)"]
        pure_q = pure_df.groupby("query").agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            CTR=("ctr", "mean"),
            Position=("position", "mean")
        ).reset_index().sort_values("Clicks", ascending=False)
        pure_q["CTR"] = pure_q["CTR"].round(2)
        pure_q["Position"] = pure_q["Position"].round(1)

        # Highlight if any position > 3
        def highlight_position(val):
            if val > 5:
                return "background-color: #FDECEA"
            elif val > 3:
                return "background-color: #FEF3CD"
            return ""

        st.dataframe(
            pure_q.style.applymap(highlight_position, subset=["Position"]),
            use_container_width=True, hide_index=True
        )

    with tab2:
        loc_df = df_filtered[df_filtered["segment"] == "Brand + Location"]
        if loc_df.empty:
            st.info("No Brand + Location data for this period.")
        else:
            store_perf = loc_df.groupby("store").agg(
                Clicks=("clicks", "sum"),
                Impressions=("impressions", "sum"),
                Avg_Position=("position", "mean")
            ).reset_index().sort_values("Clicks", ascending=False)
            store_perf["Avg_Position"] = store_perf["Avg_Position"].round(1)
            store_perf.columns = ["Store", "Clicks", "Impressions", "Avg Position"]

            fig = px.bar(store_perf, x="Store", y="Clicks",
                        color="Clicks", color_continuous_scale="Blues",
                        title="Brand + Location Clicks by Store")
            fig.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(store_perf, use_container_width=True, hide_index=True)

# ── PAGE: STORE & LOCAL ──────────────────────────────────────
elif page == "📍 Store & Local":
    st.markdown("# 📍 Store & Local Performance")

    local_df = df_filtered[df_filtered["segment"].isin(["Store & Local", "Store Intent (Near Me)"])]
    local_prev = df_prev_filtered[df_prev_filtered["segment"].isin(["Store & Local", "Store Intent (Near Me)"])]

    curr_clicks = local_df["clicks"].sum()
    prev_clicks = local_prev["clicks"].sum()
    curr_imp = local_df["impressions"].sum()
    curr_pos = round(local_df["position"].mean(), 1)

    c1, c2, c3 = st.columns(3)
    with c1: scorecard("Local Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Local Impressions", curr_imp, local_prev["impressions"].sum())
    with c3: scorecard("Avg Position", curr_pos, round(local_prev["position"].mean(), 1), lambda x: f"{x}")

    st.markdown("---")
    tab1, tab2 = st.tabs(["📍 By Store Location", "🔍 Near Me Searches"])

    with tab1:
        store_df = df_filtered[df_filtered["segment"] == "Store & Local"]
        if store_df.empty:
            st.info("No store location data for this period.")
        else:
            store_agg = store_df.groupby("store").agg(
                Clicks=("clicks", "sum"),
                Impressions=("impressions", "sum"),
                Avg_Position=("position", "mean")
            ).reset_index().sort_values("Clicks", ascending=False)
            store_agg["Avg_Position"] = store_agg["Avg_Position"].round(1)

            # RAG status
            def rag(pos):
                if pos <= 3: return "🟢 Strong"
                elif pos <= 7: return "🟡 Average"
                else: return "🔴 Weak"

            store_agg["Status"] = store_agg["Avg_Position"].apply(rag)
            store_agg.columns = ["Store", "Clicks", "Impressions", "Avg Position", "Status"]

            fig = px.bar(store_agg, x="Store", y="Clicks",
                        color="Avg Position", color_continuous_scale="RdYlGn_r",
                        title="Clicks by Store Location (colour = avg position)")
            fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                             xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(store_agg, use_container_width=True, hide_index=True)

            # Solihull note
            solihull = store_agg[store_agg["Store"] == "Solihull (Closed)"]
            if not solihull.empty:
                st.info(f"ℹ️ Solihull (Closed) — {int(solihull['Clicks'].values[0]):,} clicks this period. This is a closed competitor location being tracked for reference.")

    with tab2:
        near_df = df_filtered[df_filtered["segment"] == "Store Intent (Near Me)"]
        near_q = near_df.groupby("query").agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean")
        ).reset_index().sort_values("Impressions", ascending=False)
        near_q["Position"] = near_q["Position"].round(1)
        near_q["CTR %"] = (near_q["Clicks"] / near_q["Impressions"] * 100).round(2)
        st.dataframe(near_q, use_container_width=True, hide_index=True)

# ── PAGE: ONLINE & NATIONAL ──────────────────────────────────
elif page == "🌐 Online & National":
    st.markdown("# 🌐 Online & National")

    online_df = df_filtered[df_filtered["segment"].isin(["Online / National", "Generic Sex Shop"])]
    online_prev = df_prev_filtered[df_prev_filtered["segment"].isin(["Online / National", "Generic Sex Shop"])]

    c1, c2, c3 = st.columns(3)
    with c1: scorecard("Clicks", online_df["clicks"].sum(), online_prev["clicks"].sum())
    with c2: scorecard("Impressions", online_df["impressions"].sum(), online_prev["impressions"].sum())
    with c3: scorecard("Avg Position", round(online_df["position"].mean(), 1), round(online_prev["position"].mean(), 1), lambda x: f"{x}")

    st.markdown("---")

    online_q = online_df.groupby(["query", "segment"]).agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        Position=("position", "mean")
    ).reset_index().sort_values("Clicks", ascending=False)
    online_q["Position"] = online_q["Position"].round(1)
    online_q["CTR %"] = (online_q["Clicks"] / online_q["Impressions"] * 100).round(2)

    st.markdown('<div class="section-header">Opportunity List — High Impressions, Position 5+</div>', unsafe_allow_html=True)
    opps = online_q[(online_q["Impressions"] > 100) & (online_q["Position"] > 5)].head(25)
    st.dataframe(opps, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">All Online & National Queries</div>', unsafe_allow_html=True)
    st.dataframe(online_q, use_container_width=True, hide_index=True)

# ── PAGE: QUERY EXPLORER ─────────────────────────────────────
elif page == "🔍 Query Explorer":
    st.markdown("# 🔍 Query Explorer")
    st.caption("Full query table — filter, sort, and export")

    col1, col2, col3 = st.columns(3)
    with col1:
        min_clicks = st.number_input("Min clicks", min_value=0, value=0)
    with col2:
        min_impressions = st.number_input("Min impressions", min_value=0, value=0)
    with col3:
        keyword_search = st.text_input("Query contains", "")

    pos_range = st.slider("Position range", min_value=1.0, max_value=100.0, value=(1.0, 100.0))

    explorer_df = df_filtered.groupby(["query", "segment", "store"]).agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        CTR=("ctr", "mean"),
        Position=("position", "mean")
    ).reset_index()

    explorer_df["CTR"] = explorer_df["CTR"].round(2)
    explorer_df["Position"] = explorer_df["Position"].round(1)

    # Apply filters
    explorer_df = explorer_df[explorer_df["Clicks"] >= min_clicks]
    explorer_df = explorer_df[explorer_df["Impressions"] >= min_impressions]
    explorer_df = explorer_df[
        (explorer_df["Position"] >= pos_range[0]) &
        (explorer_df["Position"] <= pos_range[1])
    ]
    if keyword_search:
        explorer_df = explorer_df[explorer_df["query"].str.contains(keyword_search, case=False)]

    explorer_df = explorer_df.sort_values("Clicks", ascending=False)
    explorer_df.columns = ["Query", "Segment", "Store", "Clicks", "Impressions", "CTR %", "Position"]

    st.markdown(f"**{len(explorer_df):,} queries** matching current filters")
    st.dataframe(explorer_df, use_container_width=True, hide_index=True, height=600)

    csv = explorer_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f"gsc_queries_{start_str}_{end_str}.csv",
        mime="text/csv"
    )
