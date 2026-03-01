import streamlit as st


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
    st.markdown("# 🌐 Online & National")

    online_df = df_filtered[df_filtered["segment"].isin(["Online / National", "Generic Sex Shop"])]
    online_prev = df_prev_filtered[df_prev_filtered["segment"].isin(["Online / National", "Generic Sex Shop"])]

    c1, c2, c3 = st.columns(3)
    with c1: scorecard("Clicks", online_df["clicks"].sum(), online_prev["clicks"].sum())
    with c2: scorecard("Impressions", online_df["impressions"].sum(), online_prev["impressions"].sum())
    with c3: scorecard("Avg Position", round(online_df["position"].mean(), 1),
                       round(online_prev["position"].mean(), 1), lambda x: f"{x}")

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
