import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)


CATEGORY_SEGMENTS = [
    "Brand (Pure)",
    "Brand + Location",
    "Store & Local",
    "Store Intent (Near Me)",
    "Online / National",
    "Generic Sex Shop",
    "Product",
    "Category",
]

SEGMENT_COLORS = {
    "Brand (Pure)": "#FF2D78",
    "Brand + Location": "#FF6BA0",
    "Store & Local": "#00D68F",
    "Store Intent (Near Me)": "#FFB347",
    "Online / National": "#A078FF",
    "Generic Sex Shop": "#FF6B6B",
    "Product": "#4ECDC4",
    "Category": "#45B7D1",
}


def get_period_data(df, granularity):
    df = df.copy()
    if granularity == "Day":
        df["period"] = df["date"]
    elif granularity == "Week":
        df["period"] = df["date"].dt.to_period("W").dt.start_time
    else:
        df["period"] = df["date"].dt.to_period("M").dt.start_time
    return df.groupby("period").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        CTR=("ctr", "mean"),
        Position=("position", "mean")
    ).reset_index()


def chart_layout(height=300):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,18,40,0.95)",
            bordercolor="rgba(255,45,120,0.3)",
            font=dict(color="#E2E4EC", size=12, family="Plus Jakarta Sans")
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.03)",
            color="rgba(226,228,236,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            color="rgba(226,228,236,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        legend=dict(
            orientation="h", y=1.1, x=0,
            font=dict(color="rgba(226,228,236,0.5)", size=11, family="Plus Jakarta Sans"),
            bgcolor="rgba(0,0,0,0)"
        )
    )


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown("""
    <div class="page-title">Search <span class="pink">Categories</span></div>
    <div class="page-subtitle">Select one or more categories to explore combined performance</div>
    """, unsafe_allow_html=True)

    # ── CATEGORY TOGGLE BUTTONS ──────────────────────────────
    if "selected_categories" not in st.session_state:
        st.session_state.selected_categories = ["Brand (Pure)", "Brand + Location"]

    cols = st.columns(len(CATEGORY_SEGMENTS))
    for i, seg in enumerate(CATEGORY_SEGMENTS):
        with cols[i]:
            is_active = seg in st.session_state.selected_categories
            if is_active:
                color = SEGMENT_COLORS.get(seg, "#FF2D78")
                st.markdown(f"""
                <div style="border:1px solid {color}; border-radius:10px; padding:9px 12px;
                    text-align:center; color:{color}; font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:0.75rem; font-weight:700; background:rgba(255,255,255,0.06);
                    backdrop-filter:blur(10px);">{seg}</div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"cat_{seg}", use_container_width=True):
                    if len(st.session_state.selected_categories) > 1:
                        st.session_state.selected_categories.remove(seg)
                    st.rerun()
            else:
                if st.button("", key=f"cat_{seg}", use_container_width=True):
                    st.session_state.selected_categories.append(seg)
                    st.rerun()

    # Hide zero-width button text
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:not(:first-of-type) > div > div > div > .stButton > button {
        opacity: 0 !important;
        position: absolute !important;
        top: 0 !important; left: 0 !important;
        width: 100% !important; height: 100% !important;
        padding: 0 !important;
        z-index: 10 !important;
        cursor: pointer !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    selected = st.session_state.selected_categories
    df_sel = df_filtered[df_filtered["segment"].isin(selected)]
    df_prev_sel = df_prev_filtered[df_prev_filtered["segment"].isin(selected)]

    if df_sel.empty:
        st.info("No data for selected categories.")
        return

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── SUMMARY CARDS ────────────────────────────────────────
    curr_clicks = df_sel["clicks"].sum()
    curr_imp = df_sel["impressions"].sum()
    curr_ctr = round(curr_clicks / curr_imp * 100, 2) if curr_imp > 0 else 0
    curr_pos = round(df_sel["position"].mean(), 1)
    prev_clicks = df_prev_sel["clicks"].sum()
    prev_imp = df_prev_sel["impressions"].sum()
    prev_ctr = round(prev_clicks / prev_imp * 100, 2) if prev_imp > 0 else 0
    prev_pos = round(df_prev_sel["position"].mean(), 1)

    def scorecard(label, value, prev_value, format_fn=lambda x: f"{x:,}"):
        change = calc_change(value, prev_value)
        delta_class = "delta-up" if change >= 0 else "delta-down"
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{format_fn(value)}</div>
            <div class="metric-delta {delta_class}">{arrow} {abs(change)}% vs prev</div>
            <div class="metric-prev">prev: {format_fn(prev_value)}</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: scorecard("Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Impressions", curr_imp, prev_imp)
    with c3: scorecard("Avg CTR", curr_ctr, prev_ctr, lambda x: f"{x}%")
    with c4: scorecard("Avg Position", curr_pos, prev_pos, lambda x: f"{x}")

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── PERFORMANCE CHART ────────────────────────────────────
    st.markdown('<div class="section-header">Performance Over Time</div>', unsafe_allow_html=True)

    granularity = st.selectbox("Granularity", ["Day", "Week", "Month"], index=1, key="cat_gran")
    agg = get_period_data(df_sel, granularity)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["period"], y=agg["Clicks"],
        name="Clicks",
        line=dict(color="#FF2D78", width=2),
        fill="tozeroy", fillcolor="rgba(255,45,120,0.06)",
        hovertemplate="<b>%{y:,}</b> clicks<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=agg["period"], y=agg["Impressions"],
        name="Impressions",
        line=dict(color="rgba(160,120,255,0.7)", width=1.5),
        yaxis="y2",
        hovertemplate="<b>%{y:,}</b> impressions<extra></extra>"
    ))
    layout = chart_layout(320)
    layout["yaxis2"] = dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                             color="rgba(226,228,236,0.3)", tickfont=dict(size=10),
                             zeroline=False, showgrid=False)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── TOP QUERIES ──────────────────────────────────────────
    st.markdown('<div class="section-header">Top Queries</div>', unsafe_allow_html=True)

    top_q = df_sel.groupby(["query", "segment"]).agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        Position=("position", "mean"),
        CTR=("ctr", "mean")
    ).reset_index().sort_values("Clicks", ascending=False).head(50)
    top_q["Position"] = top_q["Position"].round(1)
    top_q["CTR"] = top_q["CTR"].round(2)
    st.dataframe(top_q, use_container_width=True, hide_index=True)

    # ── STORE BREAKDOWN (if store segments selected) ─────────
    store_segs = ["Store & Local", "Brand + Location"]
    if any(s in selected for s in store_segs):
        st.markdown('<div class="section-header">By Store Location</div>', unsafe_allow_html=True)
        store_df = df_sel[df_sel["store"].notna()]
        if not store_df.empty:
            store_agg = store_df.groupby("store").agg(
                Clicks=("clicks", "sum"),
                Impressions=("impressions", "sum"),
                Position=("position", "mean")
            ).reset_index().sort_values("Clicks", ascending=False)
            store_agg["Position"] = store_agg["Position"].round(1)

            fig2 = go.Figure(go.Bar(
                x=store_agg["store"],
                y=store_agg["Clicks"],
                marker=dict(
                    color=store_agg["Clicks"],
                    colorscale=[[0, "rgba(255,45,120,0.3)"], [1, "#FF2D78"]],
                    showscale=False
                ),
                hovertemplate="<b>%{x}</b><br>%{y:,} clicks<extra></extra>"
            ))
            layout2 = chart_layout(280)
            layout2["xaxis"]["tickangle"] = -35
            fig2.update_layout(**layout2)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
