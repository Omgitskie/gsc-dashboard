import streamlit as st


def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown("# 🏆 Winners & Losers")
    st.markdown(f"*Comparing {start_str}–{end_str} vs previous {period_days} days*")

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
        st.caption("Visible but not being clicked — title/description or position needs improving")
        opps = curr_q[curr_q["impressions"] > 50].copy()
        opps["ctr"] = (opps["clicks"] / opps["impressions"] * 100).round(2)
        opps = opps[opps["ctr"] < 5].sort_values("impressions", ascending=False).head(25)[
            ["query", "segment", "impressions", "clicks", "ctr", "position"]
        ]
        opps.columns = ["Query", "Segment", "Impressions", "Clicks", "CTR %", "Position"]
        st.dataframe(opps, use_container_width=True, hide_index=True)
