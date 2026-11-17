"""
Web app: the clothing and color words FitFindr's search understands.

Search used to treat every word the same, so "silk ascot" matched a silk shirt.
Now, if a query names a type of clothing, search only returns listings of that
type, and says so plainly when the catalog has none.

Each group is one kind of item and the words people use for it. Plurals are
handled automatically ("boot" and "boots" both work).
"""

# ── clothing ─────────────────────────────────────────────────────────────────
# Group name -> words that mean it. The group name is what the user is told
# when nothing matches ("We don't have any ascots right now").

CLOTHING = {
    # tops
    "tee": ["tee", "t-shirt", "tshirt", "baby tee", "band tee", "graphic tee"],
    "shirt": ["shirt", "button-down", "button down", "button-up", "blouse", "flannel", "polo", "henley"],
    "tank top": ["tank", "tank top", "cami", "camisole"],
    "crop top": ["crop top", "cropped top", "halter", "halter top", "tube top", "bandeau"],
    "top": ["top", "long sleeve", "long-sleeve"],
    "sweater": ["sweater", "jumper", "pullover", "knit", "turtleneck", "cardigan"],
    "sweatshirt": ["sweatshirt", "crewneck", "hoodie", "hoody", "sweats"],
    "vest": ["vest", "waistcoat", "sweater vest", "gilet"],
    "bodysuit": ["bodysuit", "leotard"],
    "corset": ["corset", "bustier"],
    "jersey": ["jersey"],

    # bottoms
    "jeans": ["jeans", "jean", "denim", "levis", "levi's"],
    "pants": ["pants", "trousers", "slacks", "chinos", "khakis", "cargos", "cargo pants",
              "carpenter pants", "wide-leg", "wide leg", "flares", "bell bottoms"],
    "shorts": ["shorts", "cutoffs", "jorts", "biker shorts", "bermudas"],
    "skirt": ["skirt", "miniskirt", "mini skirt", "midi skirt", "maxi skirt", "skort"],
    "leggings": ["leggings", "tights", "yoga pants", "joggers", "sweatpants", "track pants"],
    "overalls": ["overalls", "dungarees", "jumpsuit", "romper", "boilersuit"],

    # dresses
    "dress": ["dress", "slip dress", "sundress", "gown", "ballgown", "maxi dress",
              "midi dress", "mini dress", "frock"],

    # outerwear
    "jacket": ["jacket", "bomber", "windbreaker", "track jacket", "denim jacket",
               "leather jacket", "puffer", "anorak", "varsity jacket", "shacket"],
    "coat": ["coat", "trench", "trench coat", "overcoat", "peacoat", "parka", "duster"],
    "blazer": ["blazer", "sport coat", "suit jacket"],
    "suit": ["suit", "tuxedo", "tux"],

    # shoes
    "sneakers": ["sneakers", "sneaker", "trainers", "kicks", "tennis shoes", "running shoes"],
    "boots": ["boots", "boot", "chelsea boots", "combat boots", "cowboy boots", "booties",
              "ankle boots", "knee-high boots", "doc martens", "docs"],
    "heels": ["heels", "pumps", "stilettos", "kitten heels", "wedges", "platform heels"],
    "flats": ["flats", "ballet flats", "mary janes", "mary jane", "loafers", "oxfords", "brogues"],
    "sandals": ["sandals", "slides", "flip-flops", "flip flops", "mules", "clogs", "crocs"],
    "slippers": ["slippers"],

    # accessories
    "hat": ["hat", "bucket hat", "cap", "baseball cap", "beret", "fedora", "visor", "cowboy hat"],
    "beanie": ["beanie", "toque", "knit cap", "watch cap"],
    "bag": ["bag", "purse", "handbag", "tote", "shoulder bag", "crossbody", "clutch",
            "backpack", "satchel", "messenger bag", "fanny pack", "belt bag"],
    "belt": ["belt"],
    "scarf": ["scarf", "bandana", "shawl", "pashmina", "kerchief"],
    "ascot": ["ascot", "cravat"],
    "tie": ["tie", "necktie", "bow tie", "bowtie"],
    "gloves": ["gloves", "mittens"],
    "sunglasses": ["sunglasses", "shades", "glasses"],
    "jewelry": ["jewelry", "jewellery", "necklace", "bracelet", "earrings", "ring", "chain", "watch"],
    "socks": ["socks", "stockings"],
    "swimsuit": ["swimsuit", "bikini", "swim trunks", "one-piece", "bathing suit"],
    "lingerie": ["lingerie", "bra", "bralette", "underwear", "boxers"],
}


# ── colors ───────────────────────────────────────────────────────────────────
# A query color also matches its close relatives in the catalog
# ("gray" finds "grey" and "charcoal"). Colors rank results higher; unlike
# clothing, they never remove a listing, because "white" vs "cream" is a matter
# of taste.

COLORS = {
    "black": ["black", "faded black", "charcoal"],
    "white": ["white", "off-white", "ivory", "cream", "ecru", "natural"],
    "cream": ["cream", "ivory", "ecru", "off-white", "natural", "white"],
    "gray": ["grey", "gray", "charcoal", "faded black"],
    "grey": ["grey", "gray", "charcoal", "faded black"],
    "brown": ["brown", "tan", "camel", "rust", "khaki"],
    "tan": ["tan", "camel", "khaki", "brown", "natural"],
    "beige": ["tan", "camel", "khaki", "natural", "ecru", "cream"],
    "red": ["red", "faded red", "burgundy", "wine", "rust"],
    "burgundy": ["burgundy", "wine", "red"],
    "pink": ["pink", "dusty pink"],
    "orange": ["orange", "rust"],
    "yellow": ["yellow", "mustard"],
    "green": ["green", "forest green", "olive", "sage", "mint", "emerald"],
    "olive": ["olive", "khaki", "green"],
    "blue": ["blue", "light blue", "medium blue", "dark blue", "navy", "indigo", "teal"],
    "navy": ["navy", "dark blue", "indigo"],
    "purple": ["purple", "lavender"],
    "lavender": ["lavender", "purple"],
    "teal": ["teal", "blue", "green"],
    "plaid": ["plaid"],

    # Common misspellings and nicknames people type.
    "burgandy": ["burgundy", "wine", "red"],
    "burgundi": ["burgundy", "wine", "red"],
    "maroon": ["burgundy", "wine", "red"],
    "wine": ["wine", "burgundy", "red"],
    "oxblood": ["burgundy", "wine", "red"],
    "crimson": ["red", "burgundy"],
    "scarlet": ["red"],
    "blush": ["pink", "dusty pink"],
    "rose": ["pink", "dusty pink"],
    "fuchsia": ["pink", "purple"],
    "fuschia": ["pink", "purple"],
    "magenta": ["pink", "purple"],
    "lilac": ["lavender", "purple"],
    "violet": ["purple", "lavender"],
    "camel": ["camel", "tan", "brown"],
    "chocolate": ["brown"],
    "khaki": ["khaki", "tan", "olive"],
    "ivory": ["ivory", "cream", "off-white", "white"],
    "offwhite": ["off-white", "cream", "ivory", "white"],
    "charcoal": ["charcoal", "grey", "gray"],
    "silver": ["grey", "gray"],
    "sky": ["light blue", "blue"],
    "forest": ["forest green", "green"],
    "sage": ["sage", "green", "mint"],
    "mint": ["mint", "green", "sage"],
    "emerald": ["emerald", "green"],
    "mustard": ["yellow", "mustard"],
    "rust": ["rust", "orange", "brown"],
}


# ── helpers ──────────────────────────────────────────────────────────────────

# Every single clothing word, plus plurals, for quick "is this a clothing word?" checks.
ALL_CLOTHING_WORDS = {
    form
    for words in CLOTHING.values()
    for phrase in words
    for word in phrase.split()
    for form in (word, word + "s", word + "es")
    if len(word) > 2
}

def _forms(word: str) -> set[str]:
    """A word plus its plural, so 'boot' and 'boots' both match."""
    return {word, word + "s", word + "es"}


def clothing_in(query: str) -> dict[str, list[str]]:
    """
    Which clothing groups a query names, longest phrase first so
    "slip dress" counts once, not as "slip dress" and "dress".
    """
    text = f" {query.lower()} "
    found = {}
    phrases = sorted(
        ((phrase, group) for group, words in CLOTHING.items() for phrase in words),
        key=lambda pair: -len(pair[0]),
    )
    for phrase, group in phrases:
        for form in _forms(phrase):
            if f" {form} " in text:
                found.setdefault(group, CLOTHING[group])
                text = text.replace(f" {form} ", " ")
    return found


def item_text(item: dict) -> str:
    """Everything a listing says about itself, in lowercase, for matching."""
    return " ".join([
        item.get("title", ""), item.get("description", ""), item.get("category", ""),
        " ".join(item.get("style_tags", [])),
    ]).lower()


def is_kind(item: dict, words: list[str]) -> bool:
    """Does this listing look like one of these kinds of clothing?"""
    text = f" {item_text(item).replace('—', ' ').replace(',', ' ')} "
    return any(f" {form} " in text for w in words for form in _forms(w))


def colors_in(query: str) -> list[str]:
    """Every catalog color a query's color words point to."""
    words = query.lower().split()
    matched = []
    for w in words:
        matched.extend(COLORS.get(w, []))
    return matched
