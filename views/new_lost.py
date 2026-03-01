import streamlit as st


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown("# 🆕 New & Lost Keywords")
    st.markdown(f"*Comparing {start_str}–{end_str} vs previous {period_days} days*")

    curr_queries = set(df_filtered["query"].unique())
    prev_queries = set(df_prev_filtered["query"].unique())
    new_queries = curr_queries - prev_queries
    lost_queries = prev_queries - curr_queries

    tab1, tab2 = st.tabs([
        f"🆕 New Keywords ({len(new_queries)})",
        f"❌ Lost Keywords ({len(lost_queries)})"
    ])

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
        st.caption("Queries that had impressions previously but have disappeared this period")
        lost_df = df_prev_filtered[df_prev_filtered["query"].isin(lost_queries)].groupby(
            ["query", "segment"]
        ).agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean")
        ).reset_index().sort_values("Clicks", ascending=False)
        lost_df["Position"] = lost_df["Position"].round(1)
        lost_df.columns = ["Query", "Segment", "Clicks (Last Period)", "Impressions (Last Period)", "Position (Last Period)"]
        st.dataframe(lost_df, use_container_width=True, hide_index=True)
