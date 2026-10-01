"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re
import config
from generate import generate
from utils.data_loader import load_listings


_STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "for", "with", "and", "or", "of",
    "to", "under", "size", "is", "it", "me", "my", "some", "any", "that", "this"
}


def _matches_size(item_size: str, query_size: str) -> bool:
    """Case-insensitive size comparison avoiding false substring positives."""
    item_str = item_size.strip().lower()
    q_str = query_size.strip().lower()
    if item_str == q_str:
        return True
    if "one size" in q_str and "one size" in item_str:
        return True

    item_tokens = set(re.split(r"[^a-z0-9.]+", item_str)) - {"", "fits", "oversized", "adjustable"}
    q_tokens = set(re.split(r"[^a-z0-9.]+", q_str)) - {"", "fits", "oversized", "adjustable", "size"}

    if "us" in q_tokens and len(q_tokens) > 1:
        q_tokens.remove("us")
    item_tokens_without_us = item_tokens - {"us"}

    if q_tokens & item_tokens_without_us:
        return True

    for it in item_tokens:
        if it.startswith("w") and it[1:] in q_tokens:
            return True
    for qt in q_tokens:
        if qt.startswith("w") and qt[1:] in item_tokens:
            return True

    return False


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.
    """
    listings = load_listings()
    words = [w for w in re.findall(r"[a-z0-9]+", description.lower()) if w not in _STOPWORDS]
    desc_lower = description.lower()

    scored_results = []
    for item in listings:
        if max_price is not None and item.get("price", 0.0) > max_price:
            continue
        if size is not None and not _matches_size(item.get("size", ""), size):
            continue

        score = 0
        item_title = item.get("title", "").lower()
        item_desc = item.get("description", "").lower()
        item_cat = item.get("category", "").lower()
        item_tags = [t.lower() for t in item.get("style_tags", [])]
        item_colors = [c.lower() for c in item.get("colors", [])]
        item_brand = (item.get("brand") or "").lower()

        if desc_lower and desc_lower in item_title:
            score += 10
        if desc_lower and desc_lower in item_desc:
            score += 5

        for w in words:
            if w in item_title:
                score += 4
            if any(w == t or w in t for t in item_tags):
                score += 3
            if w == item_cat or w in item_cat:
                score += 3
            if any(w == c for c in item_colors):
                score += 2
            if item_brand and w in item_brand:
                score += 2
            if w in item_desc:
                score += 1

        if score > 0:
            scored_results.append((score, item))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    limit = getattr(config, "SEARCH_RESULT_LIMIT", 10)
    return [item for _, item in scored_results[:limit]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.
    """
    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    if not items:
        prompt = (
            "You are a personal stylist. The user is considering purchasing this thrifted item:\n"
            f"- Title: {new_item.get('title')}\n"
            f"- Category: {new_item.get('category')}\n"
            f"- Price: ${new_item.get('price')}\n"
            f"- Style Tags: {', '.join(new_item.get('style_tags', []))}\n"
            f"- Colors: {', '.join(new_item.get('colors', []))}\n"
            f"- Description: {new_item.get('description')}\n\n"
            "The user's closet is currently empty. Provide general styling advice and suggest 1-2 versatile outfit "
            "combinations using common wardrobe staples that pair well with this piece. Do not reference non-existent "
            "item IDs or claim the user already owns specific items. Keep your response concise (2 to 4 sentences)."
        )
    else:
        wardrobe_lines = []
        for it in items:
            name = it.get("name", "")
            cat = it.get("category", "")
            colors = ", ".join(it.get("colors", []))
            tags = ", ".join(it.get("style_tags", []))
            notes = f" ({it['notes']})" if it.get("notes") else ""
            wardrobe_lines.append(f"- {name} [{cat}, colors: {colors}, style: {tags}]{notes}")
        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = (
            "You are a personal stylist. The user is considering purchasing this thrifted item:\n"
            f"- Title: {new_item.get('title')}\n"
            f"- Category: {new_item.get('category')}\n"
            f"- Price: ${new_item.get('price')}\n"
            f"- Style Tags: {', '.join(new_item.get('style_tags', []))}\n"
            f"- Colors: {', '.join(new_item.get('colors', []))}\n"
            f"- Description: {new_item.get('description')}\n\n"
            "The user already owns these items in their wardrobe:\n"
            f"{wardrobe_text}\n\n"
            "Suggest 1 or 2 specific outfit combinations pairing this new item with pieces they already own. "
            "Explicitly name the pieces from their wardrobe that make the look work. Keep it concise and direct (2 to 4 sentences)."
        )

    system_inst = "You are a fashion stylist providing outfit pairing advice for secondhand fashion finds."
    response = generate(prompt, system=system_inst)
    return response.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.
    """
    outfit_text = outfit.strip() if outfit else ""
    price_val = new_item.get("price", 0.0)
    platform_val = new_item.get("platform", "online thrift")
    title_val = new_item.get("title", "thrift find")

    if not outfit_text:
        prompt = (
            "Write a short, engaging 2 to 4 sentence social media caption celebrating this thrift find:\n"
            f"- Item: {title_val}\n"
            f"- Price: ${price_val}\n"
            f"- Platform: {platform_val}\n"
            f"- Description: {new_item.get('description', '')}\n\n"
            "Requirements:\n"
            f"- Mention the item name, price (${price_val}), and platform ({platform_val}) each at least once.\n"
            "- Sound like a real social media post celebrating the find.\n"
            "- Keep the length between 2 and 4 sentences."
        )
    else:
        prompt = (
            "Write a short, engaging 2 to 4 sentence social media caption celebrating this thrift find:\n"
            f"- Item: {title_val}\n"
            f"- Price: ${price_val}\n"
            f"- Platform: {platform_val}\n"
            f"- Description: {new_item.get('description', '')}\n"
            f"- Outfit Idea: {outfit_text}\n\n"
            "Requirements:\n"
            f"- Mention the item, price (${price_val}), and platform ({platform_val}) each at least once.\n"
            "- Incorporate the styling vibe based on the outfit idea.\n"
            "- Sound like a genuine, exciting personal post rather than a product ad.\n"
            "- Keep the length between 2 and 4 sentences."
        )

    system_inst = "You write authentic social media captions for vintage and thrift enthusiasts."
    response = generate(prompt, system=system_inst, temperature=config.TEMPERATURE)
    return response.strip()

