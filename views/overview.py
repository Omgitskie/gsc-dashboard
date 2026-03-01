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
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{format_fn(value)}</div>
        <div class="metric-delta {delta_class}">{arrow} {abs(change)}% vs prev period</div>
    </div>
    """, unsafe_allow_html=True)


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown(f"""
    <div class="page-title">Search <span class="pink">Overview</span></div>
    <div class="page-subtitle">{start_str} &nbsp;→&nbsp; {end_str} &nbsp;·&nbsp; vs previous {period_days} days</div>
    """, unsafe_allow_html=True)

    # ── SCORECARDS ───────────────────────────────────────────
    curr_clicks = df_filtered["clicks"].sum()
    curr_imp = df_filtered["impressions"].sum()
    curr_ctr = round(curr_clicks / curr_imp * 100, 2) if curr_imp > 0 else 0
    curr_pos = round(df_filtered["position"].mean(), 1)
    prev_clicks = df_prev_filtered["clicks"].sum()
    prev_imp = df_prev_filtered["impressions"].sum()
    prev_ctr = round(prev_clicks / prev_imp * 100, 2) if prev_imp > 0 else 0
    prev_pos = round(df_prev_filtered["position"].mean(), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1: scorecard("Total Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Total Impressions", curr_imp, prev_imp)
    with c3: scorecard("Avg CTR", curr_ctr, prev_ctr, lambda x: f"{x}%")
    with c4: scorecard("Avg Position", curr_pos, prev_pos, lambda x: f"{x}")

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── CLICKS CHART ─────────────────────────────────────────
    st.markdown('<div class="section-header">Performance Over Time</div>', unsafe_allow_html=True)

    weekly = df_filtered.copy()
    weekly["week"] = weekly["date"].dt.to_period("W").dt.start_time
    weekly_agg = weekly.groupby("week").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum")
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly_agg["week"], y=weekly_agg["Clicks"],
        name="Clicks",
        line=dict(color="#FF2D78", width=2),
        fill="tozeroy",
        fillcolor="rgba(255,45,120,0.06)",
        hovertemplate="<b>%{y:,}</b> clicks<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=weekly_agg["week"], y=weekly_agg["Impressions"],
        name="Impressions",
        line=dict(color="rgba(200,205,216,0.25)", width=1.5),
        yaxis="y2",
        hovertemplate="<b>%{y:,}</b> impressions<extra></extra>"
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", y=1.12, x=0,
            font=dict(color="rgba(200,205,216,0.45)", size=11, family="Plus Jakarta Sans"),
            bgcolor="rgba(0,0,0,0)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            color="rgba(200,205,216,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        yaxis2=dict(
            overlaying="y", side="right",
            gridcolor="rgba(0,0,0,0)",
            color="rgba(200,205,216,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#151929",
            bordercolor="rgba(255,45,120,0.3)",
            font=dict(color="#E8EAF0", size=12, family="Plus Jakarta Sans")
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── SEGMENT BREAKDOWN ────────────────────────────────────
    st.markdown('<div class="section-header">By Segment</div>', unsafe_allow_html=True)

    seg_curr = df_filtered.groupby("segment").agg(
        Clicks=("clicks", "sum")
    ).reset_index()
    seg_prev = df_prev_filtered.groupby("segment").agg(
        Clicks_prev=("clicks", "sum")
    ).reset_index()
    seg = seg_curr.merge(seg_prev, on="segment", how="left").fillna(0)
    seg["Change"] = seg.apply(lambda r: calc_change(r["Clicks"], r["Clicks_prev"]), axis=1)
    seg = seg.sort_values("Clicks", ascending=False)

    colors = {
        "Brand (Pure)": "#FF2D78",
        "Brand + Location": "#FF6BA0",
        "Store & Local": "#00D68F",
        "Store Intent (Near Me)": "#FFB347",
        "Online / National": "#7B68EE",
        "Generic Sex Shop": "#FF6B6B",
        "Product": "#4ECDC4",
        "Category": "#45B7D1"
    }

    cols = st.columns(len(seg))
    for i, (_, row) in enumerate(seg.iterrows()):
        with cols[i]:
            color = colors.get(row["segment"], "#555")
            change_color = "#00D68F" if row["Change"] >= 0 else "#FF4D6D"
            arrow = "▲" if row["Change"] >= 0 else "▼"
            st.markdown(f"""
            <div class="seg-chip" style="border-top: 2px solid {color};">
                <div>
                    <div class="seg-chip-name">{row['segment']}</div>
                    <div class="seg-chip-value">{int(row['Clicks']):,}</div>
                    <div class="seg-chip-delta" style="color:{change_color};">
                        {arrow} {abs(row['Change'])}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── POSITION CHART ───────────────────────────────────────
    st.markdown('<div class="section-header">Average Position Over Time</div>', unsafe_allow_html=True)

    pos_weekly = df_filtered.copy()
    pos_weekly["week"] = pos_weekly["date"].dt.to_period("W").dt.start_time
    pos_agg = pos_weekly.groupby("week").agg(
        Position=("position", "mean")
    ).reset_index()
    pos_agg["Position"] = pos_agg["Position"].round(1)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pos_agg["week"], y=pos_agg["Position"],
        line=dict(color="#FF2D78", width=2),
        fill="tozeroy",
        fillcolor="rgba(255,45,120,0.05)",
        hovertemplate="Position <b>%{y}</b><extra></extra>"
    ))
    fig2.update_yaxes(
        autorange="reversed",
        gridcolor="rgba(255,255,255,0.04)",
        color="rgba(200,205,216,0.3)",
        tickfont=dict(size=10, family="Plus Jakarta Sans"),
        zeroline=False
    )
    fig2.update_xaxes(
        color="rgba(200,205,216,0.3)",
        tickfont=dict(size=10, family="Plus Jakarta Sans"),
        gridcolor="rgba(0,0,0,0)"
    )
    fig2.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#151929",
            bordercolor="rgba(255,45,120,0.3)",
            font=dict(color="#E8EAF0", size=12, family="Plus Jakarta Sans")
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
