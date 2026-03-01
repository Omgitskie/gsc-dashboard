ALL_SEGMENTS = [
    "Brand (Pure)",
    "Brand + Location",
    "Store & Local",
    "Store Intent (Near Me)",
    "Online / National",
    "Generic Sex Shop",
    "Product",
    "Category",
    "Other",
    "Not Relevant"
]

BRAND_PURE_TERMS = [
    "pulse and cocktail", "pulse & cocktail", "pulseandcocktail",
    "pulses and cocktail", "cocktails and pulse", "cocktail and pulse",
    "pulse n cocktail", "pulse snd cocktail", "pulse amd cocktail",
    "pulse and coctail", "pulse and cocktsil", "pulse and coxktail",
    "pulse and cicktail", "pulse and coktail", "pulse and.cocktail",
    "pulse and cocktsils", "pulse and covktail", "pulse and cocktaiks",
    "pulse and cocktials", "pulse andcocktail", "pulseandcocktails",
    "pulse snd", "pulse and cock"
]

NOISE_TERMS = [
    "pulse gym", "pulse radio", "pulse rate", "pulse yoga", "pulse pilates",
    "pulse clinic", "pulse coaching", "pulse leisure", "pulse fitness",
    "pulse hotel", "pulse agency", "pulse care", "pulse sanctuary",
    "pulse bar", "pulse theatre", "pulse outlet", "pulse warehouse",
    "pulse rx", "mediterranean", "pulse centre", "pulse high heels",
    "pulse trainers", "pulse solo", "pulse ring", "electric pulse",
    "air pulse", "pulse pantees", "pulse butt", "pulse dick",
    "pulse stroker", "pulse vagina", "clitoris pulse", "butt pulse",
    "pulse bookin", "pulse mark", "pulse closing", "pulse open now",
    "pulse77", "pulse sanctuary care", "pulse pulsefitness"
]

STORE_LOCATIONS = {
    "A1 North (Pontefract/Wentbridge)": ["pontefract", "wentbridge", "a1 north", "a1 northbound"],
    "A1 South (Grantham)": ["grantham", "sandy", "a1m", "a1 south"],
    "A1 (General)": ["a1 sex shop", "sex shop a1", "sex shop on a1", "sex shops on a1", "a1 sex shops"],
    "A12 / Essex (Rivenhall)": ["a12", "rivenhall", "witham", "essex", "colchester", "chelmsford"],
    "A38 / Lichfield": ["a38", "lichfield"],
    "A63 / Hull Brough": ["a63", "brough"],
    "Bradford": ["bradford"],
    "Cheltenham": ["cheltenham", "gloucester"],
    "Gateshead / Newcastle": ["gateshead", "newcastle", "blaydon", "north east"],
    "Hull": ["hull"],
    "Ipswich": ["ipswich"],
    "Kettering": ["kettering"],
    "Leeds": ["leeds"],
    "Lincoln / Saxilby": ["lincoln", "saxilby"],
    "Rotherham": ["rotherham"],
    "Scunthorpe": ["scunthorpe"],
    "Sheffield": ["sheffield"],
    "Wolverhampton": ["wolverhampton", "west midlands"],
    "Solihull (Closed)": ["solihull"],
}

NEAR_ME_TERMS = [
    "near me", "nearby", "nearest", "closest", "close to me",
    "local", "near by", "nwar me", "nesr me", "nere me", "mear me",
    "next to me", "around me", "near.me", "nearme", "near mr",
    "near ms", "near mw", "nea rme"
]

ONLINE_TERMS = [
    "online", " uk", "delivery", "next day", "same day",
    "website", "on line", "on-line", "internet"
]


def classify_query(query, manual_classifications=None):
    """Classify a query, checking manual overrides first."""
    q = query.lower().strip()

    if manual_classifications and query in manual_classifications:
        seg, store = manual_classifications[query]
        return seg, store

    if any(n in q for n in NOISE_TERMS):
        if not any(b in q for b in BRAND_PURE_TERMS):
            return "Noise", None

    is_brand = any(b in q for b in BRAND_PURE_TERMS)

    for store, terms in STORE_LOCATIONS.items():
        for term in terms:
            if term in q:
                if store == "A63 / Hull Brough" and "middlesbrough" in q:
                    continue
                if store == "Hull" and "solihull" in q:
                    continue
                if is_brand:
                    return "Brand + Location", store
                else:
                    return "Store & Local", store

    if is_brand:
        return "Brand (Pure)", None

    if any(t in q for t in NEAR_ME_TERMS):
        return "Store Intent (Near Me)", None

    if any(t in q for t in ONLINE_TERMS):
        return "Online / National", None

    if "sex shop" in q or "sex shops" in q or "adult shop" in q or "adult store" in q:
        return "Generic Sex Shop", None

    return "Other", None
