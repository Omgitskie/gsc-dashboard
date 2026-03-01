import streamlit as st
import pandas as pd
from utils.classify import ALL_SEGMENTS, STORE_LOCATIONS
from utils.sheets import (
    load_classifications,
    save_classification,
    delete_classification,
    export_unclassified_to_sheet
)


def render(df):
    st.markdown('<div class="page-title">Admin <span class="pink">&amp; Classifications</span></div>', unsafe_allow_html=True)
    st.caption("Manually assign or override keyword classifications. Saved to Google Sheets and applied automatically.")

    manual_classifications = load_classifications()

    tab1, tab2, tab3 = st.tabs([
        "Unclassified Keywords",
        "Reclassify Any Keyword",
        "All Manual Classifications"
    ])

    # ── TAB 1: UNCLASSIFIED ──────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">Unclassified Keywords</div>', unsafe_allow_html=True)
        st.caption("Assign segments below, or export to Google Sheets for bulk classification.")

        other_df = df[df["segment"] == "Other"].groupby("query").agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean")
        ).reset_index().sort_values("Impressions", ascending=False)
        other_df["Position"] = other_df["Position"].round(1)

        st.markdown(f"**{len(other_df):,} unclassified queries**")

        if other_df.empty:
            st.success("✓ No unclassified queries — everything has been assigned.")
        else:
            col_exp1, col_exp2 = st.columns([3, 1])
            with col_exp2:
                if st.button("📤 Export to Google Sheet", key="export_unclassified", type="secondary"):
                    count = export_unclassified_to_sheet(other_df)
                    if count > 0:
                        st.success(f"✓ Exported {count} new queries to Google Sheet. Fill in column B with segments, then reload the dashboard.")
                    else:
                        st.info("All queries already exist in the sheet.")
            with col_exp1:
                st.caption("Export all unclassified queries to Google Sheets, fill in segments there, then reload.")

            st.markdown("---")

            segment_options = ["— Skip —"] + ALL_SEGMENTS
            store_options = ["None"] + list(STORE_LOCATIONS.keys())
            assignments = {}
            store_assignments = {}

            batch_size = 25
            total = len(other_df)
            batch_start = st.number_input(
                f"Showing rows (of {total} total)",
                min_value=1,
                max_value=max(1, total - batch_size + 1),
                value=1,
                step=batch_size
            )
            batch_df = other_df.iloc[batch_start - 1: batch_start - 1 + batch_size]

            h1, h2, h3, h4, h5 = st.columns([4, 1, 1, 3, 3])
            h1.markdown("**Query**")
            h2.markdown("**Clicks**")
            h3.markdown("**Impr.**")
            h4.markdown("**Assign Segment**")
            h5.markdown("**Store (optional)**")

            for _, row in batch_df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 3, 3])
                c1.markdown(f"`{row['query']}`")
                c2.markdown(str(int(row["Clicks"])))
                c3.markdown(str(int(row["Impressions"])))
                seg = c4.selectbox(
                    "", segment_options,
                    key=f"seg_{row['query']}",
                    label_visibility="collapsed"
                )
                store = c5.selectbox(
                    "", store_options,
                    key=f"store_{row['query']}",
                    label_visibility="collapsed"
                )
                if seg != "— Skip —":
                    assignments[row["query"]] = seg
                    store_assignments[row["query"]] = store

            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{len(assignments)} queries** ready to save")
            with col2:
                if st.button("💾 Save All", key="save_all_unclassified", type="primary"):
                    if assignments:
                        saved = 0
                        for q, seg in assignments.items():
                            store_val = store_assignments.get(q)
                            store_val = store_val if store_val != "None" else None
                            if save_classification(q, seg, store_val):
                                saved += 1
                        st.success(f"✓ Saved {saved} classifications")
                        st.rerun()
                    else:
                        st.warning("No segments assigned yet — use the dropdowns above.")

    # ── TAB 2: RECLASSIFY ANY KEYWORD ───────────────────────
    with tab2:
        st.markdown('<div class="section-header">Reclassify Any Keyword</div>', unsafe_allow_html=True)
        st.caption("Find any keyword and update its classification inline.")

        search_term = st.text_input("Filter by keyword", placeholder="Leave blank to show all...")

        all_q = df.groupby("query").agg(
            Clicks=("clicks", "sum"),
            Impressions=("impressions", "sum"),
            Position=("position", "mean"),
            Current_Segment=("segment", "first")
        ).reset_index().sort_values("Impressions", ascending=False)
        all_q["Position"] = all_q["Position"].round(1)
        all_q["Manual"] = all_q["query"].apply(
            lambda q: "✓" if q in manual_classifications else ""
        )

        if search_term:
            all_q = all_q[all_q["query"].str.contains(search_term, case=False)]

        st.markdown(f"**{len(all_q):,} queries**")

        segment_options_rc = ["— No change —"] + ALL_SEGMENTS
        store_options_rc = ["None"] + list(STORE_LOCATIONS.keys())

        rc_batch_start = st.number_input(
            f"Showing rows (of {len(all_q)} total)",
            min_value=1,
            max_value=max(1, len(all_q) - 24),
            value=1,
            step=25,
            key="rc_batch"
        )
        rc_batch = all_q.iloc[rc_batch_start - 1: rc_batch_start + 24]

        h1, h2, h3, h4, h5, h6 = st.columns([4, 1, 1, 2, 3, 2])
        h1.markdown("**Query**")
        h2.markdown("**Clicks**")
        h3.markdown("**Impr.**")
        h4.markdown("**Current**")
        h5.markdown("**New Segment**")
        h6.markdown("**Store**")

        rc_assignments = {}
        rc_stores = {}

        for _, row in rc_batch.iterrows():
            c1, c2, c3, c4, c5, c6 = st.columns([4, 1, 1, 2, 3, 2])
            c1.markdown(f"`{row['query']}`")
            c2.markdown(str(int(row["Clicks"])))
            c3.markdown(str(int(row["Impressions"])))
            c4.markdown(row["Current_Segment"])
            new_seg = c5.selectbox(
                "", segment_options_rc,
                key=f"rc_seg_{row['query']}",
                label_visibility="collapsed"
            )
            new_store = c6.selectbox(
                "", store_options_rc,
                key=f"rc_store_{row['query']}",
                label_visibility="collapsed"
            )
            if new_seg != "— No change —":
                rc_assignments[row["query"]] = new_seg
                rc_stores[row["query"]] = new_store

        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{len(rc_assignments)} queries** ready to save")
        with col2:
            if st.button("💾 Save All", key="save_all_reclassify", type="primary"):
                if rc_assignments:
                    saved = 0
                    for q, seg in rc_assignments.items():
                        store_val = rc_stores.get(q)
                        store_val = store_val if store_val != "None" else None
                        if save_classification(q, seg, store_val):
                            saved += 1
                    st.success(f"✓ Saved {saved} reclassifications")
                    st.rerun()
                else:
                    st.warning("No changes made yet.")

    # ── TAB 3: ALL MANUAL CLASSIFICATIONS ───────────────────
    with tab3:
        st.markdown('<div class="section-header">All Manual Classifications</div>', unsafe_allow_html=True)

        if not manual_classifications:
            st.info("No manual classifications saved yet.")
        else:
            manual_df = pd.DataFrame([
                {"Query": q, "Segment": v[0], "Store": v[1] or "—"}
                for q, v in manual_classifications.items()
            ]).sort_values("Segment")

            st.markdown(f"**{len(manual_df):,} manual classifications**")
            st.dataframe(manual_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("**Remove a classification** (reverts to auto-classification):")
            col1, col2 = st.columns([4, 1])
            with col1:
                query_to_delete = st.selectbox(
                    "Select query to remove",
                    options=manual_df["Query"].tolist(),
                    key="delete_query"
                )
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", key="delete_classification"):
                    if delete_classification(query_to_delete):
                        st.success(f"✓ Removed '{query_to_delete}'")
                        st.rerun()

            csv = manual_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv,
                file_name="query_classifications.csv",
                mime="text/csv"
            )
