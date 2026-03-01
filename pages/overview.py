import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)


def scorecard(label, value, prev_value, format_fn=lambda x: f"{x:,}"):
    change = calc_change(value, prev_value)
    delta_class = "metric-delta-positive" if change >= 0 else "metric-delta-negative"
    arrow = "▲" if change >= 0 else "▼"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{format_fn(value)}</div>
        <div class="{delta_class}">{arrow} {abs(change)}% vs prev period</div>
    </div>
    """, unsafe_allow_html=True)


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{start_str} → {end_str} &nbsp;·&nbsp; compared to previous {period_days} days</div>', unsafe_allow_html=True)

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
        name="Clicks", line=dict(color="#FF2D78", width=2.5),
        fill="tozeroy", fillcolor="rgba(255,45,120,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=weekly_agg["week"], y=weekly_agg["Impressions"],
        name="Impressions", line=dict(color="rgba(255,255,255,0.4)", width=1.5),
        yaxis="y2"
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", y=1.1,
            font=dict(color="rgba(232,234,240,0.6)", size=12)
        ),
        yaxis=dict(
            title="", gridcolor="rgba(255,255,255,0.05)",
            color="rgba(232,234,240,0.4)", tickfont=dict(size=11)
        ),
        yaxis2=dict(
            title="", overlaying="y", side="right",
            color="rgba(232,234,240,0.4)", tickfont=dict(size=11),
            gridcolor="rgba(0,0,0,0)"
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1A1F2E",
            bordercolor="rgba(255,45,120,0.4)",
            font=dict(color="#E8EAF0", size=12)
        )
    )
    st.plotly_chart(fig, use_container_width=True)

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

    colors = {
        "Brand (Pure)": "#FF2D78",
        "Brand + Location": "#FF6B9D",
        "Store & Local": "#00E5A0",
        "Store Intent (Near Me)": "#FFB347",
        "Online / National": "#7B68EE",
        "Generic Sex Shop": "#FF6B6B",
        "Product": "#4ECDC4",
        "Category": "#45B7D1"
    }

    cols = st.columns(len(seg))
    for i, (_, row) in enumerate(seg.iterrows()):
        with cols[i]:
            color = colors.get(row["segment"], "#666")
            change_color = "#00E5A0" if row["Change"] >= 0 else "#FF4D6D"
            arrow = "▲" if row["Change"] >= 0 else "▼"
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                        border-radius:14px; padding:16px 12px; text-align:center;
                        border-top: 3px solid {color};
                        transition: all 0.3s ease;
                        animation: fadeSlideUp 0.5s ease forwards;">
                <div style="font-size:0.7rem; color:rgba(232,234,240,0.4); text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:8px; font-weight:500;">{row['segment']}</div>
                <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
                            color:#FFFFFF; line-height:1;">{int(row['Clicks']):,}</div>
                <div style="font-size:0.72rem; color:rgba(232,234,240,0.3); margin:3px 0;">clicks</div>
                <div style="font-size:0.8rem; color:{change_color}; font-weight:500; margin-top:6px;">
                    {arrow} {abs(row['Change'])}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Average Position Over Time</div>', unsafe_allow_html=True)

    pos_weekly = df_filtered.copy()
    pos_weekly["week"] = pos_weekly["date"].dt.to_period("W").dt.start_time
    pos_agg = pos_weekly.groupby("week").agg(Position=("position", "mean")).reset_index()
    pos_agg["Position"] = pos_agg["Position"].round(1)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=pos_agg["week"], y=pos_agg["Position"],
        line=dict(color="#FF2D78", width=2),
        fill="tozeroy", fillcolor="rgba(255,45,120,0.05)",
        name="Avg Position"
    ))
    fig2.update_yaxes(
        autorange="reversed",
        gridcolor="rgba(255,255,255,0.05)",
        color="rgba(232,234,240,0.4)",
        tickfont=dict(size=11)
    )
    fig2.update_xaxes(color="rgba(232,234,240,0.4)", tickfont=dict(size=11))
    fig2.update_layout(
        height=240,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#1A1F2E",
            bordercolor="rgba(255,45,120,0.4)",
            font=dict(color="#E8EAF0", size=12)
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
