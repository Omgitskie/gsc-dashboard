import streamlit as st
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
    st.markdown('<div class="page-title">Brand <span class="pink">Performance</span></div>', unsafe_allow_html=True)

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
    tab1, tab2 = st.tabs(["Brand Pure", "Brand + Location"])

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
        st.dataframe(pure_q, use_container_width=True, hide_index=True)

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
            fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                             xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(store_perf, use_container_width=True, hide_index=True)
