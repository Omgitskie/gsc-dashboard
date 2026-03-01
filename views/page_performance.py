import streamlit as st
import plotly.graph_objects as go
import re

# ── PAGE TYPE CLASSIFIER ─────────────────────────────────────

CATEGORY_SLUGS = {
    "womens-wellness", "wired-stimulators-bullets", "wigs", "whips-spankers-ticklers",
    "whips-crops-canes", "wearable-vibes-for-him", "wearable-vibes-for-her",
    "water-based-lube", "all-vibrators", "vibrators", "vibrators-for-her",
    "vibrator-kits", "vibrating-strap-ons", "vibrating-nipple-toys",
    "vibrating-dildos", "vibrating-cock-rings-sleeves", "vibrating-cock-rings",
    "valentines-gift-sets", "valentines-top-picks-for-him", "valentines-top-pick-for-her",
    "valentines-top-pick-for-couples", "valentines-top-gift-picks", "valentines-luxury-gifts",
    "valentines-lingerie", "sexy-valentines-lingerie", "valentines-gifts-under-60",
    "valentines-gifts-under-60-2", "valentines-day-gifts-for-him",
    "valentines-day-gifts-for-her", "valentines-day-gifts-for-couples", "valentines-day",
    "up-to-60-off-sale", "rabbits-and-eggs", "uncategorised", "toys-under-20",
    "toys-for-him", "toys-for-her", "toys-for-both", "top-sellers", "tights",
    "thrusting-sex-toys", "thigh-high-boots", "suspender-stockings", "suspender-belts",
    "surgical-items", "suction-toys", "suction-cup-dildos", "strap-ons-all", "strap-ons",
    "strap-on", "strap-on-sets", "strap-on-harnesses", "strap-on-dildos", "stockings",
    "stimulators-bullets", "stimulators-bullets-sex-toys-for-couples-top-sellers",
    "stimulation-tickler-sleeves-sex-toys-for-men", "stimulation-tickler-sleeves",
    "standard-vibrators", "standard-size-rabbits", "stag-parties", "spreader-bars",
    "special-offers", "special-offer-bundles", "sparkling-christmas", "spanking-paddles",
    "solo-toys", "solid-ball-gags", "slim-vibrators", "slides", "size-8-erotic-shoes",
    "silicone-butt-plugs", "silicone-oil-based-lube", "shoes-boots",
    "shibari-ropes-bondage-accessories", "sexy-stocking-thrillers", "sexy-stocking-fillers",
    "sexy-shoes", "sexy-plus-size-lingerie", "sexy-lingerie-sets", "sexy-gowns",
    "sexy-christmas-lingerie", "sexy-christmas", "sexy-boots", "female-sex-toys",
    "sex-toys-for-women", "male-sex-toys", "sex-toys-for-men", "couples-sex-toys",
    "sex-toys-for-couples", "sex-toys-for-couples-top-sellers",
    "sex-toys-and-adult-gifts-for-him", "mega-deals-sex-toys", "adult-sex-toys",
    "sex-toys", "sex-toy-gift-sets", "sex-machines-for-women", "sex-machines",
    "sex-machine-for-men", "sex-machine-accessories", "sex-kits-for-women",
    "sex-kits-for-men", "sex-kits-for-couples-2", "sex-kits-for-couples",
    "sex-kits-gift-sets", "sex-games", "sensation-lubes", "secret-santa-gifts",
    "sandals", "remote-control-toys", "remote-control-stimulators-bullets",
    "realistic-vibrators", "realistic-vaginas-and-sex-dolls", "realistic-vaginas",
    "realistic-sex-dolls", "realistic-masturbators", "realistic-male-toys",
    "realistic-dildos", "rabbits", "rabbit-vibrators-vibrators", "rabbit-vibrators",
    "pvc-wet-look", "fetish-pvc-wet-look", "pumps", "prostate-stimulators",
    "prostate-massagers-for-him", "prostate-massagers", "poweract-by-skins", "power-toys",
    "portable-masturbators", "pocket-pussy", "plus-size-sexy-dresses", "plus-size-knickers",
    "plus-size-hosiery", "plus-size-corsets-basques", "plus-size-body-stockings",
    "plus-baby-dollsbodies-teddies", "pleasure-enhancers-sex-toys-for-couples-top-sellers",
    "pleasure-enhancers", "pinwheels", "picks-under-40", "penis-pumps",
    "penis-pumps-for-him", "penis-plugs-urethral-sounds", "penis-extension-sleeves",
    "penis-extenders", "peek-a-boo-lingerie", "organic-essentials", "open-mouth-gags",
    "open-crotch-peephole", "open-crotch", "non-vibrating-dildos-dildos",
    "non-vibrating-strap-ons", "non-vibrating-cock-rings", "nipple-toys",
    "nipple-toys-for-her", "nipple-tassels-jewellery", "nipple-tassels",
    "nipple-clamps-tassels-teasers", "nipple-clamps", "nipple-clamps-nipple-toys",
    "nipple-breast-pumps-suckers", "nipple-breast-pumps", "new-sex-toys",
    "new-lingerie-sexy-wear", "new-arrivals", "naughty-valentines-day-gifts",
    "naughty-novelties", "mouth-gags", "monster-arrivals", "mix-match-deals-sex-toys",
    "mix-match-deals", "mini-dresses", "metal-cock-rings",
    "metal-cock-rings-cock-rings-sleeves", "metal-butt-plugs", "mens-underwear",
    "mens-body-stockings", "mens-best-sellers-buy-one-get-one-half-price",
    "mens-best-sellers-deal", "massagers", "massage-wands", "massage-oils-candles-2",
    "massage-oils-candles", "massage-oil-lubricants", "masks-gloves", "male-sex-toys-deal",
    "male-orgasm-libido-enhancers", "masturbators", "male-masturbators",
    "male-orgasm-stamina-enhancers", "male-delay-stamina-products", "male-delays",
    "male-chastity-devices", "luxury-vibrators", "luxury-toys-women",
    "luxury-toys-for-couples", "luxury-sex-toys-for-women", "luxury-sex-toys-for-men",
    "luxury-sex-toys-for-her", "luxury-sex-toys-for-couples-sex-toys-for-couples-top-sellers",
    "luxury-sex-toys-for-couples", "luxury-sex-toys-buy-one-get-one-half-price",
    "luxury-rabbits", "luxury-mens-toys", "lubricants-oils-for-him", "lubricants-oils",
    "lubricants-oils-sex-toys-for-couples-top-sellers", "lubricants-3-for-2", "lubricants",
    "lubricant-bundles", "lubes-extras", "lube-bundles", "love-lubes", "love-eggs-jiggle-balls",
    "love-eggs", "long-dresses", "liquid-vibrators-from-intt", "lingerie-sexy-wear",
    "lingerie-outfits", "lingerie-buy-one-get-one-half-price", "mega-deals-lingerie",
    "lingerie-sexy-wear-for-her", "leather-leatherette", "fetish-leather-leatherette",
    "fetish-latex-rubber", "latex-rubber", "knickers-thongs", "knickers-thongs-knickers-thongs",
    "knee-high-boots", "kinky-valentines-gifts", "kinky-christmas-gifts", "kegel-exercisers",
    "jiggle-balls", "jewelled-butt-plugs", "intt-imate-sexual-enhancers-3",
    "intt-imate-sexual-enhancers", "inflatable-dildos", "hygiene-care", "hot-bondage-4for3",
    "hosiery", "hollow-strap-ons", "hold-up-stockings", "high-performance-sex-machines",
    "hen-parties", "hen-stag-parties", "help-me-find-a-toy", "harness-gags",
    "handjob-day-essentials", "handcuffs-restraints-ties", "handcuffs-ankle-cuffs",
    "gowns-sexy-dresses", "glow-in-the-dark", "gloves-masks", "glass-sex-toys",
    "glass-love-balls-eggs", "glass-double-ended-dildos", "glass-dildos-massagers",
    "glass-dildos", "glass-butt-plugs", "glass-anal-toys", "glass-anal-toys-glass-sex-toys",
    "gimp-masks", "gifts-20-under", "gifts-10-under", "gifts-games",
    "gay-and-lesbian-sex-toys", "g-spot-vibrators", "foreplay-fun", "for-him", "for-her",
    "floggers", "flesh-light", "flavoured-lube", "finger-vibrator", "fetish-wear-accessories",
    "fetish-wear-latex-leather-pvc", "fetish-bondage-gear", "fetish-latex-leather-pvc",
    "festival-wear-accessories", "party-outfits-accessories", "female-orgasm-libido-enhancers",
    "female-orgasm-libido-enhancers-prev", "female-orgasm-libido-enhancers-for-her",
    "female-chastity-devices", "feather-ticklers", "fantasy-dildos", "fancy-dress-role-play",
    "extreme-dildos", "extreme-butt-plugs", "extreme-anal-toys", "extreme-anal",
    "mega-deals-essentials", "erotic-lingerie", "electro-sex-toys-sex-toys-for-couples-top-sellers",
    "electro-sex-toys", "electro-toys", "electrastim", "easter-range",
    "dresses-with-stockings", "double-penetrators", "double-ended-strap-on", "double-dildos",
    "double-dildos-couples", "discreet-vibrators", "discreet-travel-essentials",
    "discreet-masturbators", "dinky-rabbits", "dildo-for-women", "dildos", "dildo-vibrators",
    "dildo-sex-machines", "dildo-kits", "crotchless-knickers", "cross-sell",
    "corsets-basques", "condoms", "colourful-sex-toys", "collars-leads", "cock-rings-sleeves",
    "cock-rings-restraints", "cock-rings-penis-sleeves", "cock-rings", "cock-cages",
    "clitoral-stimulator", "clitoral-stimulators-for-her", "clitoral-stimulators",
    "christmas-picks", "christmas-gifts-for-him", "christmas-gifts-for-her",
    "christmas-gifts-for-couples", "christmas-gift-sets", "christmas", "chastity-devices",
    "chastity-devices-sex-toys-for-men", "cbd-collection", "buy-one-get-one-free-sex-toys",
    "butt-plugs", "bullets", "bullet-vibrators", "breathable-ball-gags", "bra-sets",
    "books", "bondage-rope-tape", "bondage-kits-sex-toys-for-couples-top-sellers",
    "bondage-kits", "bondage-hoods", "bondage-furniture-sex-swings", "mega-deals-bondage",
    "body-stockings", "body-paint-edibles", "body-jewellery", "blindfolds-masks-hoods",
    "blindfolds-masks", "mega-deals", "bit-gags", "big-savings", "better-sex",
    "better-sex-prev", "better-sex-better-oral-sex", "better-anal-sex",
    "better-sex-better-anal-sex", "bestselling-masturbators", "best-selling-vibrators",
    "luxury-sex-toys", "best-sellers", "beginners-anal-toys", "beginner-vibrators",
    "beginner-butt-plugs", "bed-restraints-ties", "batteries", "bank-holiday-picks",
    "bank-holiday-bangers", "baby-dolls-slips", "at-least-31-halloween-special",
    "armslegs-body-restraints", "aphrodisiacs", "ankle-boots", "anal-vibrators",
    "anal-toys", "anal-sex-toy-kits", "anal-sex-machines", "anal-lubes",
    "douches-and-enema-kits", "anal-dildos", "anal-beads", "alien-monster-dildos",
    "adult-games", "2-for-50-toys", "2-for-50-bondage", "2-for-30-toys-more",
    "2-for-30-bondage", "50-toys",
}

UK_LOCATIONS = {
    "london", "manchester", "birmingham", "leeds", "glasgow", "sheffield", "bradford",
    "liverpool", "edinburgh", "bristol", "cardiff", "leicester", "coventry", "nottingham",
    "newcastle", "brighton", "hull", "wolverhampton", "plymouth", "stoke", "derby",
    "swansea", "southampton", "portsmouth", "reading", "oxford", "cambridge", "norwich",
    "exeter", "bath", "york", "chester", "lincoln", "peterborough", "luton", "swindon",
    "bournemouth", "middlesbrough", "bolton", "sunderland", "ipswich", "milton-keynes",
    "belfast", "aberdeen", "dundee", "inverness", "stirling", "perth",
}


def classify_page(url):
    if not isinstance(url, str):
        return "Unclassified"
    path = url.lower()
    # Remove domain if present
    path = re.sub(r"https?://[^/]+", "", path)
    # Remove trailing slash and query params
    path = path.split("?")[0].rstrip("/")
    slug = path.strip("/").split("/")[-1] if "/" in path else path.strip("/")

    if path in ("", "/"):
        return "Homepage"
    if "sex-shops-near-me" in path:
        return "Store Page"
    for loc in UK_LOCATIONS:
        if loc in path:
            return "Store Page"
    if slug in CATEGORY_SLUGS:
        return "Category Page"
    for cat_slug in CATEGORY_SLUGS:
        if cat_slug in path:
            return "Category Page"
    # Products — if URL has multiple path segments and doesn't match above
    segments = [s for s in path.strip("/").split("/") if s]
    if len(segments) >= 2:
        return "Product Page"
    if len(segments) == 1:
        return "Product Page"

    return "Unclassified"


def get_period_data(df, granularity):
    df = df.copy()
    if granularity == "Day":
        df["period"] = df["date"]
    elif granularity == "Week":
        df["period"] = df["date"].dt.to_period("W").dt.start_time
    else:
        df["period"] = df["date"].dt.to_period("M").dt.start_time
    return df.groupby("period").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
    ).reset_index()


def calc_change(curr, prev):
    if prev == 0:
        return 100.0
    return round(((curr - prev) / prev) * 100, 1)


def chart_layout(height=300):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,18,40,0.95)",
            bordercolor="rgba(255,45,120,0.3)",
            font=dict(color="#E2E4EC", size=12, family="Plus Jakarta Sans")
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.03)",
            color="rgba(226,228,236,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            color="rgba(226,228,236,0.3)",
            tickfont=dict(size=10, family="Plus Jakarta Sans"),
            zeroline=False
        ),
        legend=dict(
            orientation="h", y=1.1, x=0,
            font=dict(color="rgba(226,228,236,0.5)", size=11, family="Plus Jakarta Sans"),
            bgcolor="rgba(0,0,0,0)"
        )
    )


def render(df_filtered, df_prev_filtered, start_str, end_str, period_days):
    st.markdown("""
    <div class="page-title">Page <span class="pink">Performance</span></div>
    <div class="page-subtitle">URL-level search performance across your site</div>
    """, unsafe_allow_html=True)

    # ── CLASSIFY PAGES ───────────────────────────────────────
    if "page" not in df_filtered.columns:
        st.warning("No page/URL data available from GSC. Check your data fetch includes the 'page' dimension.")
        return

    df = df_filtered.copy()
    df_prev = df_prev_filtered.copy()
    df["page_type"] = df["page"].apply(classify_page)
    df_prev["page_type"] = df_prev["page"].apply(classify_page)

    # Extract slug for display
    def to_slug(url):
        if not isinstance(url, str):
            return url
        path = re.sub(r"https?://[^/]+", "", url).split("?")[0].rstrip("/")
        return path if path else "/"

    df["slug"] = df["page"].apply(to_slug)
    df_prev["slug"] = df_prev["page"].apply(to_slug)

    # ── PAGE TYPE FILTER BUTTONS ──────────────────────────────
    PAGE_TYPES = ["All", "Category Page", "Store Page", "Product Page", "Homepage", "Unclassified"]

    if "selected_page_type" not in st.session_state:
        st.session_state.selected_page_type = "All"

    cols = st.columns(len(PAGE_TYPES))
    for i, pt in enumerate(PAGE_TYPES):
        with cols[i]:
            is_active = st.session_state.selected_page_type == pt
            if is_active:
                st.markdown(f"""
                <div style="border:1px solid #FF2D78; border-radius:10px; padding:9px 12px;
                    text-align:center; color:#FF2D78; font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:0.78rem; font-weight:700; background:rgba(255,45,120,0.1);">{pt}</div>
                """, unsafe_allow_html=True)
            else:
                if st.button(pt, key=f"pt_{pt}", use_container_width=True):
                    st.session_state.selected_page_type = pt
                    st.rerun()

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── FILTER BY TYPE ────────────────────────────────────────
    selected_type = st.session_state.selected_page_type
    if selected_type != "All":
        df_view = df[df["page_type"] == selected_type]
        df_prev_view = df_prev[df_prev["page_type"] == selected_type]
    else:
        df_view = df
        df_prev_view = df_prev

    # ── SUMMARY CARDS ─────────────────────────────────────────
    curr_clicks = df_view["clicks"].sum()
    curr_imp = df_view["impressions"].sum()
    curr_pages = df_view["page"].nunique()
    curr_pos = round(df_view["position"].mean(), 1)
    prev_clicks = df_prev_view["clicks"].sum()
    prev_imp = df_prev_view["impressions"].sum()
    prev_pages = df_prev_view["page"].nunique()
    prev_pos = round(df_prev_view["position"].mean(), 1)

    def scorecard(label, value, prev_value, format_fn=lambda x: f"{x:,}"):
        change = calc_change(value, prev_value)
        delta_class = "delta-up" if change >= 0 else "delta-down"
        arrow = "▲" if change >= 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{format_fn(value)}</div>
            <div class="metric-delta {delta_class}">{arrow} {abs(change)}% vs prev</div>
            <div class="metric-prev">prev: {format_fn(prev_value)}</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: scorecard("Clicks", curr_clicks, prev_clicks)
    with c2: scorecard("Impressions", curr_imp, prev_imp)
    with c3: scorecard("Pages with Clicks", curr_pages, prev_pages)
    with c4: scorecard("Avg Position", curr_pos, prev_pos, lambda x: f"{x}")

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── TOP PAGES TABLE ───────────────────────────────────────
    st.markdown('<div class="section-header">Top Pages</div>', unsafe_allow_html=True)

    pages_curr = df_view.groupby(["slug", "page_type"]).agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        CTR=("ctr", "mean"),
        Position=("position", "mean")
    ).reset_index()
    pages_prev = df_prev_view.groupby("slug").agg(
        Clicks_prev=("clicks", "sum")
    ).reset_index()
    pages = pages_curr.merge(pages_prev, on="slug", how="left").fillna(0)
    pages["Change %"] = pages.apply(lambda r: calc_change(r["Clicks"], r["Clicks_prev"]), axis=1)
    pages["CTR"] = pages["CTR"].round(2)
    pages["Position"] = pages["Position"].round(1)
    pages = pages.sort_values("Clicks", ascending=False)
    pages.columns = ["URL", "Type", "Clicks", "Impressions", "CTR %", "Position", "Clicks (Prev)", "Change %"]

    st.dataframe(pages, use_container_width=True, hide_index=True)

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── TOP 10 BAR CHART ─────────────────────────────────────
    st.markdown('<div class="section-header">Top 10 Pages by Clicks</div>', unsafe_allow_html=True)

    top10 = pages.head(10)
    fig = go.Figure(go.Bar(
        x=top10["Clicks"],
        y=top10["URL"],
        orientation="h",
        marker=dict(
            color=top10["Clicks"],
            colorscale=[[0, "rgba(255,45,120,0.3)"], [1, "#FF2D78"]],
            showscale=False
        ),
        hovertemplate="<b>%{y}</b><br>%{x:,} clicks<extra></extra>"
    ))
    layout = chart_layout(380)
    layout["yaxis"]["autorange"] = "reversed"
    layout["margin"] = dict(l=0, r=0, t=8, b=0)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── SINGLE PAGE TREND ─────────────────────────────────────
    st.markdown('<div class="section-header">Page Trend</div>', unsafe_allow_html=True)

    url_options = pages["URL"].tolist()
    selected_url = st.selectbox("Select a page to view trend", url_options, key="page_trend_url")
    granularity = st.selectbox("Granularity", ["Day", "Week", "Month"], index=1, key="page_trend_gran")

    df_url = df_view[df_view["slug"] == selected_url]
    if not df_url.empty:
        agg = get_period_data(df_url, granularity)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=agg["period"], y=agg["Clicks"],
            name="Clicks",
            line=dict(color="#FF2D78", width=2),
            fill="tozeroy", fillcolor="rgba(255,45,120,0.06)",
            hovertemplate="<b>%{y:,}</b> clicks<extra></extra>"
        ))
        fig2.add_trace(go.Scatter(
            x=agg["period"], y=agg["Impressions"],
            name="Impressions",
            line=dict(color="rgba(160,120,255,0.8)", width=1.5),
            yaxis="y2",
            hovertemplate="<b>%{y:,}</b> impressions<extra></extra>"
        ))
        layout2 = chart_layout(280)
        layout2["yaxis2"] = dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                                  color="rgba(226,228,236,0.3)", tickfont=dict(size=10),
                                  zeroline=False, showgrid=False)
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<hr class="dot-divider">', unsafe_allow_html=True)

    # ── TOP QUERIES FOR SELECTED PAGE ────────────────────────
    st.markdown(f'<div class="section-header">Queries driving {selected_url}</div>', unsafe_allow_html=True)

    page_queries = df_view[df_view["slug"] == selected_url].groupby("query").agg(
        Clicks=("clicks", "sum"),
        Impressions=("impressions", "sum"),
        CTR=("ctr", "mean"),
        Position=("position", "mean")
    ).reset_index().sort_values("Clicks", ascending=False).head(25)
    page_queries["CTR"] = page_queries["CTR"].round(2)
    page_queries["Position"] = page_queries["Position"].round(1)
    st.dataframe(page_queries, use_container_width=True, hide_index=True)
