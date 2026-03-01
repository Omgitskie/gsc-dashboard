import streamlit as st
import plotly.graph_objects as go


def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)


def scorecard(label, value, prev_value, format_fn=lambda x: f"{x:,}"):
    change = calc_change(value, prev_value)
    delta_class = "delta-up" if change >= 0 else "delta-down"
    arrow = "▲" if change >= 0 else "▼"
    prev_fmt = format_fn(prev_value)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{format_fn(value)}</div>
        <div class="metric-delta {delta_class}">{arrow} {abs(change)}% vs prev period</div>
        <div class="metric-prev">prev: {prev_fmt}</div>
    </div>
    """, unsafe_allow_html=True)


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


def chart_layout():
    return dict(
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,18,40,0.95)",
            bordercolor="rgba(255,45,120,0.3)",
            font=dict(color="#E2E4EC", size=12, family="Plus Jakarta Sans")
        ),
        legend=dict(
            orientation="h", y=1.1, x=0,
            font=dict(color="rgba(226,228,236,0.5)", size=11, family="Plus Jakarta Sans"),
            bgcolor="rgba(0,0,0,0)"
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
        )
    )


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days, compare_option="Previous Period"):
    st.markdown(f"""
    <div class="page-title">Search <span class="pink">Overview</span></div>
    <div class="page-subtitle">{start_str} &nbsp;→&nbsp; {end_str} &nbsp;·&nbsp; vs {compare_option.lower()}</div>
    """, unsafe_allow_html=True)

    # ── SCORECARDS ───────────────────────────────────────────
    curr_clicks = df_filtered["clicks"].sum()
    curr_imp = df_filtered["impressions"].sum()
    curr_ctr = round(curr_clicks / curr_imp * 100, 2) if curr_imp > 0 else 0
    curr_pos = round(df_filtered["position"].mean(), 1)
    curr_kw = df_filtered["query"].nunique()

    prev_clicks = df_prev_filtered["clicks"].sum()
    prev_imp = df_prev_filtered["impressions"].sum()
    prev_ctr = round(prev_clicks / prev_imp * 100, 2) if prev_imp > 0 else 0
    prev_pos = round(df_prev_filtered["position"].mean(), 1)
    prev_kw = df_prev_filtered["query"].nunique()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: scorecard("Total Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Impressions", curr_imp, prev_imp)
    with c3: scorecard("Avg CTR", curr_ctr, prev_ctr, lambda x: f"{x}%")
    with c4: scorecard("Avg Position", curr_pos, prev_pos, lambda x: f"{x}")
    with c5: scorecard("Keywords", curr_kw, prev_kw)

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── PERFORMANCE CHART ────────────────────────────────────
    st.markdown('<div class="section-header">Performance Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        metrics_selected = st.multiselect(
            "Show metrics",
            ["Clicks", "Impressions", "CTR", "Position"],
            default=["Clicks", "Impressions"],
            key="overview_metrics"
        )
    with ctrl2:
        granularity = st.selectbox("Granularity", ["Day", "Week", "Month"], index=1, key="overview_gran")

    agg = get_period_data(df_filtered, granularity)
    agg["CTR"] = agg["CTR"].round(2)
    agg["Position"] = agg["Position"].round(1)

    METRIC_COLORS = {
        "Clicks": "#FF2D78",
        "Impressions": "rgba(160,120,255,0.7)",
        "CTR": "#00E096",
        "Position": "#FFB347"
    }
    METRIC_YAXIS = {
        "Clicks": "y",
        "Impressions": "y2",
        "CTR": "y3",
        "Position": "y4"
    }

    fig = go.Figure()

    if "Clicks" in metrics_selected:
        fig.add_trace(go.Scatter(
            x=agg["period"], y=agg["Clicks"],
            name="Clicks",
            line=dict(color=METRIC_COLORS["Clicks"], width=2),
            fill="tozeroy", fillcolor="rgba(255,45,120,0.06)",
            yaxis="y",
            hovertemplate="<b>%{y:,}</b> clicks<extra></extra>"
        ))
    if "Impressions" in metrics_selected:
        fig.add_trace(go.Scatter(
            x=agg["period"], y=agg["Impressions"],
            name="Impressions",
            line=dict(color=METRIC_COLORS["Impressions"], width=1.5),
            yaxis="y2",
            hovertemplate="<b>%{y:,}</b> impressions<extra></extra>"
        ))
    if "CTR" in metrics_selected:
        fig.add_trace(go.Scatter(
            x=agg["period"], y=agg["CTR"],
            name="CTR %",
            line=dict(color=METRIC_COLORS["CTR"], width=1.5, dash="dot"),
            yaxis="y3",
            hovertemplate="CTR <b>%{y}%</b><extra></extra>"
        ))
    if "Position" in metrics_selected:
        fig.add_trace(go.Scatter(
            x=agg["period"], y=agg["Position"],
            name="Position",
            line=dict(color=METRIC_COLORS["Position"], width=1.5, dash="dash"),
            yaxis="y4",
            hovertemplate="Position <b>%{y}</b><extra></extra>"
        ))

    layout = chart_layout()
    layout["height"] = 320
    layout["yaxis2"] = dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                             color="rgba(226,228,236,0.3)", tickfont=dict(size=10), zeroline=False, showgrid=False)
    layout["yaxis3"] = dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                             color="rgba(226,228,236,0.3)", tickfont=dict(size=10), zeroline=False,
                             showgrid=False, showticklabels=False)
    layout["yaxis4"] = dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                             color="rgba(226,228,236,0.3)", tickfont=dict(size=10), zeroline=False,
                             showgrid=False, showticklabels=False, autorange="reversed")

    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── SEGMENT BREAKDOWN ────────────────────────────────────
    st.markdown('<div class="section-header">By Segment</div>', unsafe_allow_html=True)

    seg_curr = df_filtered.groupby("segment").agg(Clicks=("clicks", "sum")).reset_index()
    seg_prev = df_prev_filtered.groupby("segment").agg(Clicks_prev=("clicks", "sum")).reset_index()
    seg = seg_curr.merge(seg_prev, on="segment", how="left").fillna(0)
    seg["Change"] = seg.apply(lambda r: calc_change(r["Clicks"], r["Clicks_prev"]), axis=1)
    seg = seg.sort_values("Clicks", ascending=False)

    colors = {
        "Brand (Pure)": "#FF2D78",
        "Brand + Location": "#FF6BA0",
        "Store & Local": "#00D68F",
        "Store Intent (Near Me)": "#FFB347",
        "Online / National": "#A078FF",
        "Generic Sex Shop": "#FF6B6B",
        "Product": "#4ECDC4",
        "Category": "#45B7D1"
    }

    cols = st.columns(len(seg))
    for i, (_, row) in enumerate(seg.iterrows()):
        with cols[i]:
            color = colors.get(row["segment"], "#555")
            change_color = "#00E096" if row["Change"] >= 0 else "#FF4D6D"
            arrow = "▲" if row["Change"] >= 0 else "▼"
            st.markdown(f"""
            <div class="seg-chip" style="border-top: 2px solid {color};">
                <div class="seg-chip-name">{row['segment']}</div>
                <div class="seg-chip-value">{int(row['Clicks']):,}</div>
                <div class="seg-chip-delta" style="color:{change_color};">
                    {arrow} {abs(row['Change'])}%
                </div>
            </div>
            """, unsafe_allow_html=True)
