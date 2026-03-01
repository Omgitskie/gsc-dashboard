import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


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


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown("# 📊 Overview")
    st.markdown(f"*{start_str} to {end_str} — compared to previous {period_days} days*")

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

    st.markdown("---")
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
        yaxis2=dict(title="Impressions", overlaying="y", side="right"),
        hovermode="x unified"
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
        "Brand (Pure)": "#1E3A5F",
        "Brand + Location": "#2E86AB",
        "Store & Local": "#1A7A4A",
        "Store Intent (Near Me)": "#C07A00",
        "Online / National": "#8E44AD",
        "Generic Sex Shop": "#E74C3C",
        "Product": "#E67E22",
        "Category": "#16A085"
    }

    cols = st.columns(len(seg))
    for i, (_, row) in enumerate(seg.iterrows()):
        with cols[i]:
            color = colors.get(row["segment"], "#666")
            change_color = "#1A7A4A" if row["Change"] >= 0 else "#C0392B"
            arrow = "▲" if row["Change"] >= 0 else "▼"
            st.markdown(f"""
            <div style="background:white; border-radius:10px; padding:15px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.08);
                        border-top: 4px solid {color}; text-align:center;">
                <div style="font-size:0.75rem; color:#666; margin-bottom:5px;">{row['segment']}</div>
                <div style="font-size:1.5rem; font-weight:700; color:#1E3A5F;">{int(row['Clicks']):,}</div>
                <div style="font-size:0.8rem; color:#888;">clicks</div>
                <div style="font-size:0.85rem; color:{change_color}; margin-top:5px;">{arrow} {abs(row['Change'])}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Average Position Over Time</div>', unsafe_allow_html=True)
    pos_weekly = df_filtered.copy()
    pos_weekly["week"] = pos_weekly["date"].dt.to_period("W").dt.start_time
    pos_agg = pos_weekly.groupby("week").agg(Position=("position", "mean")).reset_index()
    pos_agg["Position"] = pos_agg["Position"].round(1)
    fig2 = px.line(pos_agg, x="week", y="Position", color_discrete_sequence=["#E74C3C"])
    fig2.update_traces(line=dict(width=2.5))
    fig2.update_yaxes(autorange="reversed", title="Avg Position (lower = better)", gridcolor="#f0f0f0")
    fig2.update_xaxes(title="")
    fig2.update_layout(height=280, margin=dict(l=0, r=0, t=20, b=0),
                       plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)
