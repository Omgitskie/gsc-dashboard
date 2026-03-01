import streamlit as st


def render(df_filtered, start_str, end_str):
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
