"""
Web app: builds data/listings_extra.json, a larger catalog on top of the
original 40 listings in data/listings.json (which stay untouched, because the
capstone tests ran against them).

    python data/make_extra_listings.py

Each entry in ITEMS below is one kind of item. The script makes a few versions
of each in different colors, so search has real choices (black AND white
sneakers, a grey beanie, and so on). A fixed random seed means running it again
gives the same file.
"""

import json
import random
from pathlib import Path

random.seed(201)

# kind, category, sizes it comes in, price range, style tags, materials,
# and the description sentences it can use.
ITEMS = [
    # tops
    ("Graphic Tee", "tops", "letter", (12, 30), ["graphic tee", "streetwear", "vintage"], ["cotton"],
     "Soft, worn-in tee with a cracked vintage print."),
    ("Ringer Tee", "tops", "letter", (14, 28), ["70s", "retro", "casual"], ["cotton"],
     "Contrast-trim ringer tee, slightly boxy fit."),
    ("Baby Tee", "tops", "letter", (12, 26), ["y2k", "fitted", "cute"], ["cotton", "stretch cotton"],
     "Cropped, fitted baby tee with a tiny chest graphic."),
    ("Tank Top", "tops", "letter", (8, 20), ["basics", "minimal", "summer"], ["ribbed cotton"],
     "Ribbed tank that layers under everything."),
    ("Button-Down Shirt", "tops", "letter", (16, 38), ["classic", "preppy", "office"], ["oxford cotton", "linen"],
     "Crisp button-down, relaxed through the body."),
    ("Flannel Shirt", "tops", "letter", (16, 34), ["grunge", "90s", "cozy"], ["brushed flannel"],
     "Soft brushed flannel, great open over a tee."),
    ("Silk Blouse", "tops", "letter", (22, 48), ["elegant", "feminine", "office"], ["silk", "satin"],
     "Fluid blouse with a subtle sheen."),
    ("Crochet Top", "tops", "letter", (18, 40), ["boho", "festival", "handmade"], ["cotton crochet"],
     "Handmade crochet top, lined at the bust."),
    ("Corset Top", "tops", "letter", (24, 52), ["y2k", "going out", "feminine"], ["satin", "brocade"],
     "Boned corset top with a lace-up back."),
    ("Turtleneck", "tops", "letter", (14, 32), ["minimal", "90s", "layering"], ["merino", "ribbed knit"],
     "Fitted turtleneck that works on its own or layered."),
    ("Chunky Sweater", "tops", "letter", (24, 55), ["cozy", "fall", "vintage"], ["wool", "cable knit"],
     "Oversized cable-knit sweater, warm and heavy."),
    ("Cardigan", "tops", "letter", (18, 44), ["grandpa", "cozy", "vintage"], ["wool blend", "mohair"],
     "Button-front cardigan with deep pockets."),
    ("Hoodie", "tops", "letter", (20, 48), ["streetwear", "cozy", "athletic"], ["fleece-lined cotton"],
     "Heavyweight pullover hoodie, fleece inside."),
    ("Crewneck Sweatshirt", "tops", "letter", (18, 42), ["college", "vintage", "cozy"], ["fleece cotton"],
     "Faded crewneck with a ribbed hem and cuffs."),
    ("Sweater Vest", "tops", "letter", (16, 36), ["preppy", "dark academia", "vintage"], ["wool", "argyle knit"],
     "Knit vest, perfect over a collared shirt."),
    ("Polo Shirt", "tops", "letter", (14, 30), ["preppy", "90s", "sporty"], ["pique cotton"],
     "Classic polo with a three-button placket."),
    ("Mesh Top", "tops", "letter", (14, 30), ["y2k", "going out", "layering"], ["stretch mesh"],
     "Sheer stretch mesh top, made for layering."),

    # bottoms
    ("Straight Leg Jeans", "bottoms", "waist", (24, 58), ["denim", "classic", "vintage"], ["rigid denim"],
     "Mid-rise straight leg jeans with a vintage wash."),
    ("Baggy Jeans", "bottoms", "waist", (26, 60), ["denim", "streetwear", "y2k"], ["denim"],
     "Loose, low-slung jeans with a long inseam."),
    ("Flare Jeans", "bottoms", "waist", (24, 52), ["70s", "denim", "retro"], ["stretch denim"],
     "High-rise flares that sit at the natural waist."),
    ("Mom Jeans", "bottoms", "waist", (22, 48), ["90s", "denim", "vintage"], ["rigid denim"],
     "Tapered high-waisted mom jeans."),
    ("Cargo Pants", "bottoms", "waist", (22, 50), ["utility", "y2k", "streetwear"], ["cotton twill", "ripstop"],
     "Relaxed cargo pants with six pockets."),
    ("Wide-Leg Trousers", "bottoms", "waist", (24, 54), ["tailored", "minimal", "office"], ["wool blend", "linen"],
     "Pleated wide-leg trousers with a sharp crease."),
    ("Corduroy Pants", "bottoms", "waist", (20, 44), ["70s", "cozy", "vintage"], ["wide-wale corduroy"],
     "Soft corduroy pants, straight through the leg."),
    ("Pleated Mini Skirt", "bottoms", "letter", (14, 34), ["preppy", "y2k", "schoolgirl"], ["poly blend", "wool"],
     "Pleated mini skirt with a side zip."),
    ("Midi Skirt", "bottoms", "letter", (18, 42), ["feminine", "boho", "elegant"], ["satin", "cotton"],
     "Bias-cut midi skirt that moves when you walk."),
    ("Denim Skirt", "bottoms", "waist", (16, 38), ["denim", "y2k", "casual"], ["denim"],
     "Classic five-pocket denim skirt."),
    ("Denim Shorts", "bottoms", "waist", (14, 32), ["denim", "summer", "vintage"], ["denim"],
     "Cutoff denim shorts with a frayed hem."),
    ("Leggings", "bottoms", "letter", (10, 26), ["athletic", "basics", "y2k"], ["stretch nylon"],
     "High-waisted leggings with a flat waistband."),
    ("Sweatpants", "bottoms", "letter", (14, 34), ["cozy", "athletic", "streetwear"], ["fleece cotton"],
     "Cuffed sweatpants with a drawstring waist."),

    # dresses (the catalog files them under tops, like the original slip dress)
    ("Slip Dress", "tops", "letter", (22, 48), ["90s", "feminine", "going out"], ["satin", "silk"],
     "Bias-cut slip dress with adjustable straps."),
    ("Sundress", "tops", "letter", (18, 42), ["summer", "boho", "cottagecore"], ["cotton", "linen"],
     "Breezy sundress with a smocked back."),
    ("Mini Dress", "tops", "letter", (18, 44), ["y2k", "going out", "party"], ["stretch knit", "velvet"],
     "Fitted mini dress for a night out."),
    ("Maxi Dress", "tops", "letter", (24, 56), ["boho", "summer", "flowy"], ["rayon", "chiffon"],
     "Floor-length maxi dress with flutter sleeves."),
    ("Sweater Dress", "tops", "letter", (22, 50), ["cozy", "fall", "minimal"], ["ribbed knit"],
     "Ribbed knit sweater dress, hits below the knee."),

    # outerwear
    ("Denim Jacket", "outerwear", "letter", (26, 60), ["denim", "classic", "vintage"], ["denim"],
     "Broken-in denim trucker jacket."),
    ("Leather Jacket", "outerwear", "letter", (55, 140), ["edgy", "moto", "vintage"], ["genuine leather"],
     "Moto-style leather jacket, soft from years of wear."),
    ("Bomber Jacket", "outerwear", "letter", (30, 70), ["streetwear", "90s", "utility"], ["nylon", "satin"],
     "Classic bomber with ribbed cuffs."),
    ("Puffer Jacket", "outerwear", "letter", (35, 90), ["winter", "streetwear", "cozy"], ["nylon"],
     "Warm, boxy puffer that packs down small."),
    ("Trench Coat", "outerwear", "letter", (45, 110), ["classic", "elegant", "rainy day"], ["cotton gabardine"],
     "Double-breasted trench with a waist belt."),
    ("Wool Coat", "outerwear", "letter", (50, 120), ["winter", "classic", "minimal"], ["wool"],
     "Long wool overcoat, fully lined."),
    ("Blazer", "outerwear", "letter", (28, 70), ["tailored", "office", "vintage"], ["wool", "linen", "tweed"],
     "Single-breasted blazer with structured shoulders."),
    ("Varsity Jacket", "outerwear", "letter", (40, 95), ["college", "sporty", "vintage"], ["wool", "leather sleeves"],
     "Varsity jacket with chenille patches."),
    ("Windbreaker", "outerwear", "letter", (20, 46), ["90s", "sporty", "retro"], ["nylon"],
     "Lightweight windbreaker with a half zip."),
    ("Fleece Jacket", "outerwear", "letter", (22, 48), ["outdoorsy", "cozy", "gorpcore"], ["polar fleece"],
     "Zip-up fleece, warm without the bulk."),

    # shoes
    ("Low-Top Sneakers", "shoes", "shoe", (25, 70), ["streetwear", "classic", "casual"], ["canvas", "leather"],
     "Everyday low-top sneakers, clean soles."),
    ("High-Top Sneakers", "shoes", "shoe", (30, 80), ["streetwear", "90s", "skater"], ["canvas", "leather"],
     "High-top sneakers with ankle padding."),
    ("Platform Sneakers", "shoes", "shoe", (30, 70), ["y2k", "chunky", "streetwear"], ["leather", "canvas"],
     "Chunky platform sneakers with a thick sole."),
    ("Running Shoes", "shoes", "shoe", (30, 75), ["athletic", "gorpcore", "dad shoe"], ["mesh"],
     "Retro running shoes, light and cushioned."),
    ("Combat Boots", "shoes", "shoe", (40, 95), ["grunge", "edgy", "90s"], ["leather"],
     "Lace-up combat boots with a lug sole."),
    ("Chelsea Boots", "shoes", "shoe", (40, 90), ["classic", "minimal", "fall"], ["leather", "suede"],
     "Pull-on Chelsea boots with elastic sides."),
    ("Cowboy Boots", "shoes", "shoe", (55, 130), ["western", "vintage", "boho"], ["tooled leather"],
     "Pointed-toe cowboy boots with stitched shafts."),
    ("Knee-High Boots", "shoes", "shoe", (45, 110), ["70s", "elegant", "fall"], ["leather", "suede"],
     "Sleek knee-high boots with a block heel."),
    ("Loafers", "shoes", "shoe", (28, 70), ["preppy", "dark academia", "classic"], ["leather"],
     "Penny loafers, broken in and comfortable."),
    ("Mary Janes", "shoes", "shoe", (25, 60), ["y2k", "feminine", "schoolgirl"], ["patent leather"],
     "Strappy Mary Janes with a small heel."),
    ("Heels", "shoes", "shoe", (25, 70), ["going out", "elegant", "party"], ["satin", "leather"],
     "Classic pointed-toe heels."),
    ("Sandals", "shoes", "shoe", (15, 45), ["summer", "minimal", "boho"], ["leather"],
     "Flat strappy sandals for warm days."),

    # accessories
    ("Beanie", "accessories", "one", (8, 22), ["cozy", "winter", "streetwear"], ["ribbed knit", "wool"],
     "Ribbed cuffed beanie, stretchy and warm."),
    ("Baseball Cap", "accessories", "one", (10, 26), ["sporty", "streetwear", "casual"], ["cotton twill"],
     "Faded six-panel cap with an adjustable strap."),
    ("Bucket Hat", "accessories", "one", (10, 24), ["90s", "streetwear", "summer"], ["cotton", "corduroy"],
     "Soft bucket hat, packable."),
    ("Beret", "accessories", "one", (10, 24), ["french", "dark academia", "elegant"], ["wool felt"],
     "Classic wool beret."),
    ("Scarf", "accessories", "one", (10, 30), ["cozy", "winter", "classic"], ["wool", "cashmere blend"],
     "Long, soft scarf with fringed ends."),
    ("Silk Scarf", "accessories", "one", (12, 34), ["elegant", "vintage", "french"], ["silk"],
     "Printed silk square, wear it in your hair or at your neck."),
    ("Ascot", "accessories", "one", (14, 32), ["dapper", "vintage", "elegant"], ["silk"],
     "Vintage silk ascot, a statement for the bold."),
    ("Tie", "accessories", "one", (8, 22), ["office", "vintage", "dapper"], ["silk"],
     "Skinny vintage tie."),
    ("Tote Bag", "accessories", "one", (12, 40), ["casual", "minimal", "everyday"], ["canvas", "leather"],
     "Roomy tote that fits a laptop."),
    ("Crossbody Bag", "accessories", "one", (16, 48), ["everyday", "minimal", "y2k"], ["leather", "nylon"],
     "Small crossbody bag with an adjustable strap."),
    ("Shoulder Bag", "accessories", "one", (18, 55), ["y2k", "90s", "going out"], ["leather", "suede"],
     "Baguette-style shoulder bag."),
    ("Backpack", "accessories", "one", (18, 50), ["everyday", "school", "utility"], ["nylon", "canvas"],
     "Sturdy backpack with a padded laptop sleeve."),
    ("Belt", "accessories", "one", (10, 30), ["western", "classic", "vintage"], ["leather"],
     "Leather belt with a vintage buckle."),
    ("Sunglasses", "accessories", "one", (10, 30), ["y2k", "90s", "summer"], ["acetate"],
     "Retro sunglasses with tinted lenses."),
    ("Gloves", "accessories", "one", (10, 28), ["winter", "elegant", "classic"], ["leather", "wool"],
     "Lined gloves for cold days."),
]

COLORS = ["black", "white", "grey", "navy", "brown", "tan", "cream", "red", "burgundy",
          "pink", "green", "olive", "blue", "light blue", "purple", "orange", "yellow"]

# Shoes and coats come in fewer colors in real life.
CATEGORY_COLORS = {
    "shoes": ["white", "brown", "tan", "grey", "cream", "burgundy", "navy"],
    "outerwear": ["brown", "tan", "navy", "olive", "grey", "cream", "burgundy", "blue"],
}

# Brands that actually make each category (None = unbranded/vintage).
CATEGORY_BRANDS = {
    "tops": [None, None, "Gap", "Champion", "Zara", "Urban Outfitters", "Free People", "J.Crew", "Ralph Lauren", "Madewell"],
    "bottoms": [None, None, "Levi's", "Gap", "Carhartt", "Zara", "Madewell", "Urban Outfitters"],
    "outerwear": [None, None, "Levi's", "Carhartt", "Patagonia", "The North Face", "Zara", "J.Crew"],
    "shoes": [None, "Nike", "Adidas", "Converse", "Vans", "Dr. Martens", "Steve Madden", "Frye"],
    "accessories": [None, None, None, "Coach", "Urban Outfitters", "Carhartt", "Zara"],
}

SIZES = {
    "letter": ["XS", "S", "M", "L", "XL", "XXL"],
    "waist": ["W26", "W27", "W28", "W29", "W30", "W31", "W32", "W34", "W36"],
    "shoe": ["US 6", "US 6.5", "US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 11"],
    "one": ["One Size"],
}

BRANDS_UNUSED = None  # brands now come from CATEGORY_BRANDS above

CONDITIONS = ["excellent", "good", "good", "fair"]
CONDITION_NOTES = {
    "excellent": "Barely worn, no flaws.",
    "good": "Light wear consistent with age, no major flaws.",
    "fair": "Visible wear (small mark noted in photos), priced to match.",
}
PLATFORMS = ["depop", "poshmark", "thredUp"]
VERSIONS_PER_ITEM = 3


def make_listing(number: int, item: tuple, color: str) -> dict:
    kind, category, size_type, (low, high), tags, materials, blurb = item
    material = random.choice(materials)
    condition = random.choice(CONDITIONS)
    brand = random.choice(CATEGORY_BRANDS[category])
    title = f"{kind} — {color.title()}"
    if brand:
        title = f"{brand} {title}"
    return {
        "id": f"lst_{number:03d}",
        "title": title,
        "description": f"{blurb} {color.capitalize()} {material}. {CONDITION_NOTES[condition]}",
        "category": category,
        "style_tags": tags,
        "size": random.choice(SIZES[size_type]),
        "condition": condition,
        "price": float(random.randint(low, high)),
        "colors": [color],
        "brand": brand,
        "platform": random.choice(PLATFORMS),
    }


def main():
    listings = []
    number = 101  # the original catalog uses lst_001 to lst_040
    for item in ITEMS:
        category = item[1]
        # Every item comes in black, plus two other colors that suit it.
        palette = [c for c in CATEGORY_COLORS.get(category, COLORS) if c != "black"]
        colors = ["black"] + random.sample(palette, VERSIONS_PER_ITEM - 1)
        for color in colors:
            listings.append(make_listing(number, item, color))
            number += 1

    out = Path(__file__).parent / "listings_extra.json"
    out.write_text(json.dumps(listings, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(listings)} listings to {out}")


if __name__ == "__main__":
    main()
