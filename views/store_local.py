import streamlit as st
import plotly.express as px
from utils.classify import STORE_LOCATIONS


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
    st.markdown('<div class="page-title">Store <span class="pink">&amp; Local</span></div>', unsafe_allow_html=True)

    local_df = df_filtered[df_filtered["segment"].isin(["Store & Local", "Store Intent (Near Me)"])]
    local_prev = df_prev_filtered[df_prev_filtered["segment"].isin(["Store & Local", "Store Intent (Near Me)"])]

    c1, c2, c3 = st.columns(3)
    with c1: scorecard("Local Clicks", local_df["clicks"].sum(), local_prev["clicks"].sum())
    with c2: scorecard("Local Impressions", local_df["impressions"].sum(), local_prev["impressions"].sum())
    with c3: scorecard("Avg Position", round(local_df["position"].mean(), 1),
                       round(local_prev["position"].mean(), 1), lambda x: f"{x}")

    st.markdown("---")
    tab1, tab2 = st.tabs(["By Store Location", "Near Me Searches"])

    with tab1:
        store_df = df_filtered[df_filtered["segment"] == "Store & Local"]
        if store_df.empty:
            st.info("No store location data for this period.")
        else:
            store_agg = store_df.groupby("store").agg(
                Clicks=("clicks", "sum"),
                Impressions=("impressions", "sum"),
                Avg_Position=("position", "mean")
            ).reset_index().sort_values("Clicks", ascending=False)
            store_agg["Avg_Position"] = store_agg["Avg_Position"].round(1)

            def rag(pos):
                if pos <= 3: return "🟢 Strong"
                elif pos <= 7: return "🟡 Average"
                else: return "🔴 Weak"

            store_agg["Status"] = store_agg["Avg_Position"].apply(rag)
            store_agg.columns = ["Store", "Clicks", "Impressions", "Avg Position", "Status"]
            fig = px.bar(store_agg, x="Store", y="Clicks",
                        color="Avg Position", color_continuous_scale="RdYlGn_r",
                        title="Clicks by Store Location (colour = avg position)")
            fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white",
                             xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(store_agg, use_container_width=True, hide_index=True)
            solihull = store_agg[store_agg["Store"] == "Solihull (Closed)"]
            if not solihull.empty:
                st.info(f"ℹ️ Solihull (Closed) — {int(solihull['Clicks'].values[0]):,} clicks this period. Closed competitor location tracked for reference.")

    with tab2:
        near_df = df_filtered[df_filtered["segment"] == "Store Intent (Near Me)"]
        near_q = near_df.groupby("query").agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean")
        ).reset_index().sort_values("Impressions", ascending=False)
        near_q["Position"] = near_q["Position"].round(1)
        near_q["CTR %"] = (near_q["Clicks"] / near_q["Impressions"] * 100).round(2)
        st.dataframe(near_q, use_container_width=True, hide_index=True)
