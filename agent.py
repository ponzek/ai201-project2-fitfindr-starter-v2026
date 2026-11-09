"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import time

import config
import generate
import run_log
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── query parsing ─────────────────────────────────────────────────────────────

def parse_query(query: str) -> dict:
    """
    Extract search keywords, size, and price ceiling from a natural language query.
    """
    parsed = {"description": query.strip(), "size": None, "max_price": None}
    working = query

    # 1. Price pattern: "under $30", "under 30", "< $30", "$30", "less than $40", "below $30"
    price_match = re.search(
        r"(?:under|<|\bmax\b|below|less than|cheaper than)\s*\$?(\d+(?:\.\d+)?)|(?:\$(\d+(?:\.\d+)?))",
        working,
        re.I,
    )
    if price_match:
        price_str = price_match.group(1) or price_match.group(2)
        parsed["max_price"] = float(price_str)
        working = working[:price_match.start()] + " " + working[price_match.end():]

    # 2. Size pattern: "in size M", "size XXS", "size 8", "size US 9", "size W30"
    size_match = re.search(
        r"\b(?:in\s+)?size\s+([A-Za-z0-9/]+(?:\s+[A-Za-z0-9.]+)?)\b",
        working,
        re.I,
    )
    if size_match:
        parsed["size"] = size_match.group(1).strip()
        working = working[:size_match.start()] + " " + working[size_match.end():]

    # 3. Clean up description
    desc = re.sub(
        r"\b(looking for|find me|i want|search for|a|an)\b",
        " ",
        working,
        flags=re.I,
    )
    desc = re.sub(r"\s+", " ", desc).strip()
    parsed["description"] = desc if desc else query.strip()
    return parsed


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
        "warning": None,             # capstone: a model step failed, but we still have a listing
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. Check session["error"] first — if it isn't None,
        the run ended early and the later fields will still be None.

    Capstone: every run, including one that crashes, writes a record to
    logs/runs.jsonl with its timing and token use (see run_log.py).
    """
    session = new_session(query, wardrobe)
    timer = run_log.StepTimer()
    tokens_before = generate.token_counts()
    calls_before = generate.call_count()
    started = time.perf_counter()
    crash = None

    try:
        _run_steps(session, timer)
    except Exception as exc:
        crash = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        tokens_after = generate.token_counts()
        run_log.write_record(
            session,
            duration=time.perf_counter() - started,
            steps=timer.steps,
            tokens={
                "prompt": tokens_after["prompt"] - tokens_before["prompt"],
                "output": tokens_after["output"] - tokens_before["output"],
            },
            model_calls=generate.call_count() - calls_before,
            crash=crash,
        )
    return session


def _run_steps(session: dict, timer) -> None:
    """The planning loop itself. Fills in the session as it goes."""
    query = session["query"]
    iteration = 0

    # Step 1: Parse the user's query into structured parameters
    iteration += 1
    trace.check_iterations(iteration)
    session["parsed"] = parse_query(session["query"])

    # Step 2: Search catalog listings using parsed inputs from session via MCP
    iteration += 1
    trace.check_iterations(iteration)
    parsed_input = session["parsed"]
    search_args = {
        "description": parsed_input.get("description", query),
        "size": parsed_input.get("size"),
        "max_price": parsed_input.get("max_price"),
    }

    timer.start()
    try:
        from mcp_client import call_tool
        session["search_results"] = call_tool("search_listings", search_args)
        step_name = "search_listings (via MCP)"
    except Exception:
        session["search_results"] = search_listings(
            description=search_args["description"],
            size=search_args["size"],
            max_price=search_args["max_price"],
        )
        step_name = "search_listings"
    timer.stop("search")

    # ⚠️ BRANCH: If search returned nothing, stop early and explain what to change
    if not session["search_results"]:
        trace.step(step_name, inputs=search_args, returned=[], note="branch: empty search, stopping early")
        filters = []
        if parsed_input.get("max_price") is not None:
            filters.append(f"raising your price limit above ${parsed_input['max_price']}")
        if parsed_input.get("size") is not None:
            filters.append(f"searching for sizes other than '{parsed_input['size']}'")
        filters.append(f"broadening your search terms (tried '{parsed_input.get('description', query)}')")
        session["error"] = f"No matching listings found. Try {' or '.join(filters)}."
        return session

    trace.step(step_name, inputs=search_args, returned=session["search_results"])

    # Step 3: Select top candidate item and store in session
    iteration += 1
    trace.check_iterations(iteration)
    session["selected_item"] = session["search_results"][0]

    # Step 4: Suggest outfits by reading selected item and wardrobe from session
    iteration += 1
    trace.check_iterations(iteration)
    item_to_pair = session["selected_item"]
    user_closet = session["wardrobe"]
    timer.start()
    try:
        session["outfit_suggestion"] = suggest_outfit(item_to_pair, user_closet)
    except ModelUnavailable as exc:
        timer.stop("outfit")
        # Capstone fallback: search already found a listing, so keep it and
        # tell the user which step failed instead of throwing it all away.
        session["warning"] = f"Couldn't suggest an outfit: {exc}"
        trace.step("suggest_outfit", inputs={"item": item_to_pair.get("title")},
                   returned=None, note="model failed, returning the listing only")
        return session
    timer.stop("outfit")
    trace.step(
        "suggest_outfit",
        inputs={"item": item_to_pair.get("title"), "wardrobe_items": len(user_closet.get("items", []))},
        returned=session["outfit_suggestion"],
    )

    # Step 5: Generate social fit card by reading outfit and selected item from session
    iteration += 1
    trace.check_iterations(iteration)
    outfit_text = session["outfit_suggestion"]
    item_for_card = session["selected_item"]
    timer.start()
    try:
        session["fit_card"] = create_fit_card(outfit_text, item_for_card)
    except ModelUnavailable as exc:
        timer.stop("fit_card")
        # Capstone fallback: keep the listing and the outfit we already have.
        session["warning"] = f"Couldn't write a fit card: {exc}"
        trace.step("create_fit_card", inputs={"item": item_for_card.get("title")},
                   returned=None, note="model failed, returning listing and outfit")
        return session
    timer.stop("fit_card")
    trace.step(
        "create_fit_card",
        inputs={"item": item_for_card.get("title"), "price": item_for_card.get("price")},
        returned=session["fit_card"],
    )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
