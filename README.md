# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an AI-powered personal shopping and styling assistant for secondhand and vintage fashion. A user asks for an aesthetic, garment type, size, or price limit in natural language (e.g., "vintage graphic tee under $30"). The agent parses their request, searches a thrift catalog for matching pieces, recommends personalized outfit combinations utilizing pieces from the user's existing wardrobe, and generates a social-ready fit card caption highlighting the find.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches thrift store listings and filters them by keywords, optional size, and maximum price ceiling.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None).
- **Returns:** A list of listing dicts (at most 3), best match first, each containing `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), and `platform` (str).
- **When it has nothing:** An empty list (`[]`), never `None` or an exception.

### `suggest_outfit`

- **What it does:** Calls the Gemini model to suggest 1–2 outfit combinations pairing a selected thrift item with items from the user's wardrobe.
- **Inputs:** `new_item` (dict with listing fields: `id`, `title`, `category`, `style_tags`, `colors`, `price`), `wardrobe` (dict with an `'items'` key holding a list of wardrobe item dicts).
- **Returns:** A non-empty string containing 1–2 outfit pairing descriptions specifically naming owned wardrobe items.
- **When it has nothing:** When `wardrobe['items']` is empty, returns a string containing general styling suggestions and silhouette advice for the item rather than raising an error or returning `""`.

### `create_fit_card`

- **What it does:** Calls the Gemini model to write a 2–4 sentence social-ready caption highlighting the thrift find, styling vibe, price, and platform.
- **Inputs:** `outfit` (str), `new_item` (dict with listing fields: `title`, `price`, `platform`, `description`, `style_tags`).
- **Returns:** A 2–4 sentence caption string mentioning the item, its price, platform, and styling aesthetic.
- **When it has nothing:** When `outfit` is empty or whitespace-only, returns a descriptive caption focusing solely on the item, its price, and platform without crashing or raising an exception.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, set `session["error"]` with an informative message suggesting what the user could change and stop. Otherwise, take the first listing from `session["search_results"]`, store it in `session["selected_item"]`, and proceed to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex pattern extraction for price (e.g., `r'(?:under|<|\$)\s*(\d+(?:\.\d{2})?)'`) and size (e.g., `r'\bsize\s+([A-Za-z0-9/]+)\b'`), using remaining terms as the `description` string.

**What moves through the session:** `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` (list of listings) → `selected_item` (listing dict) → `outfit_suggestion` (str) → `fit_card` (str) [or `error` (str) if search results are empty].

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop

  Outfit:   **The Ultimate 90s Grunge Look**
Pair the graphic tee with your baggy dark-wash straight-leg jeans, and anchor the outfit with your black combat boots for an effortless, authentic streetwear vibe. Layer the vintage black denim jacket on top to play with textures and add an extra layer of vintage edge. 

**High-Low Contrast Streetwear**
Tuck the slightly boxy graphic tee into your wide-leg khaki trousers, and define the waist with your brown leather belt for a cool mix of earthy tones and grungy edge. Finish the fit with your chunky white sneakers and the black crossbody bag for a casual, balanced day-to-day look.

  Fit card: I can’t believe I scored this buttery-soft 2003 tour bootleg tee for just $24.0 on depop! The faded graphic and boxy fit give it that ultimate 90s grunge look when paired with baggy denim and beat-up combat boots. I’m so obsessed with how effortlessly authentic this streetwear vibe is!
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30)[:1])"
[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two ways to style your new Vintage Levi's 501s using pieces already in your wardrobe:

**1. Casual Streetwear Look**
Pair the Levi's with your **white ribbed tank top** tucked in, layered under your **vintage black denim jacket**, and finish with your **chunky white sneakers** and **black crossbody bag**. The fitted tank balances the relaxed 501 fit while the black outerwear creates a sharp, effortless contrast against the medium wash.

**2. Cozy Off-Duty Look**
Wear the jeans with your **oversized grey crewneck sweatshirt** half-tucked at the waist, cinched with your **brown leather belt**, and style it with your **black combat boots**. The heavy boots anchor the slouchy, vintage silhouette of the sweatshirt and denim for an easy, textured outfit.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('styled with a white tank and combat boots', load_listings()[0]))"
I am still not over finding these dream vintage Levi's 501 jeans with that perfectly faded medium wash! I just dropped them on my depop for $38.0, and they are begging to be styled with a crisp white tank and heavy combat boots. Grab them before I change my mind and keep them for myself!
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Size matching logic for `search_listings` to filter listings by sizes like "S", "M", "L", "US 9", and "W30".
- *What came back:* A simple case-insensitive substring search implementation (`query_size.lower() in item_size.lower()`).
- *What I changed:* Replaced the naive substring search with regex tokenization and token sets. The substring check produced false positives like `"s"` matching `"US 9"` or `"l"` matching `"xl"`, returning shoes when asking for small tops. The updated tokenized comparison accurately handles split sizes (e.g., `"M"` matches `"S/M"`), shoe sizes, and waist measurements (`"W30"` vs `"30"`) without cross-category false positives.

**Moment 2**

- *What I asked for:* Handling the branch condition in `run_agent()` when `search_listings` returns no matching items.
- *What came back:* A static generic message: `"No results found for your query."`
- *What I changed:* Replaced the generic string with dynamic, actionable feedback that inspects which filters were active (`max_price`, `size`, `description`) and specifies what the user could change (e.g. raising the price limit above $5.0, checking adjacent sizes instead of 'XXS', or broadening keywords) while keeping `session["fit_card"]` as `None` and halting before calling `suggest_outfit`.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. state preservation across tools | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card format and variety | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. empty wardrobe | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
File & Function: agent.py::run_agent (Scenario 1, Try 1)
Query: 'vintage graphic tee under $30'
Wardrobe: example

Selected Item:
  id: lst_006
  title: Graphic Tee — 2003 Tour Bootleg Style
  price: $24.0
  platform: depop

Outfit Suggestion:
**Look 1: 90s Streetwear Grunge**
Pair the graphic tee with your **baggy dark wash straight-leg jeans** and **chunky white sneakers** for an effortless, throwback silhouette. Throw your **vintage black denim jacket** over the top and finish with the **black crossbody bag** for a cohesive, everyday streetwear vibe.

**Look 2: Edgy Contrast**
Tuck the tee into your **wide-leg khaki trousers** using the **brown leather belt** to add a touch of structure and earthy contrast. Complete the outfit with your **black combat boots** to lean into the vintage, grunge edge of the shirt.

Fit Card:
I cannot get over this 2003 tour bootleg graphic tee I just scored on Depop for only $24.00! The faded print and boxy, worn-in cotton give it the ultimate 90s grunge edge, whether I'm pairing it with baggy denim and sneakers or dressing it down with khaki trousers and combat boots. Honestly, finding a piece with this much authentic vintage character for under 25 bucks is a total win.
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | In all 5 tries, the agent executed search_listings, suggest_outfit, and create_fit_card, returning a completed fit card. |
| 2 | Impossible query stops before second tool | 5 of 5 | MET (5/5) | In all 5 tries, search_listings returned [], the loop halted without calling suggest_outfit, and an actionable error was returned. |
| 3 | State preservation across tools | 5 of 5 | MET (5/5) | In all 5 tries, session["selected_item"]["id"] ('lst_004') matched session["search_results"][0]["id"] and was passed intact to downstream tools. |
| 4 | Fit card format and variety | 4 of 5 | MET (5/5) | All 5 fit cards contained price ($30.0) and platform (Depop), were 2-4 sentences long, and opened with distinct phrasing across tries. |
| 5 | Empty wardrobe graceful styling | 4 of 5 | MET (5/5) | In all 5 tries with an empty wardrobe, the agent completed all three tools, returning general styling advice with zero non-existent 'w_...' IDs. |

**Diagnoses**

All five criteria met their targets on the initial run. However, two minor UX issues were identified during inspection:
1. **Unformatted Float Stringification in Fit Card:** When `new_item["price"]` was passed as a raw float (e.g. `30.0` or `24.0`), the model prompt reflected `$30.0` or `$24.00`, leading to slightly robotic social captions (e.g., "for only $24.00" instead of the natural "for only $24").
2. **Platform Capitalization Inconsistency:** Raw platform values in `data/listings.json` are lowercase (`depop`, `thredUp`, `poshmark`). Captions occasionally mirrored the lowercase or inconsistent capitalization instead of proper brand casing (`Depop`, `ThredUp`, `Poshmark`).




---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey, Vintage Graphic Hoodie — Faded Black … +7 more
[2] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: **The Ultimate 90s Grunge Look** Pair the graphic tee with your baggy dark-wash straight-leg jeans, and anchor…
[3] create_fit_card
      in:  dict with keys: item, price
      out: I can’t believe I scored this buttery-soft 2003 tour bootleg tee for just $24 on Depop! The faded graphic an…
```

**Empty search**

```
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty search, stopping early
```

**On the MCP move:**
I decoupled `search_listings` from direct module execution by registering it with FastMCP in `mcp_server.py`, complete with typed parameters and docstrings. In `agent.py::run_agent`, the search call was rewired to call `mcp_client.call_tool("search_listings", search_args)`. The protocol serialization preserved the exact `list[dict]` return shape, so no downstream session or tool logic had to be altered. The trace now visibly displays `[1] search_listings (via MCP)`.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
1. In `tools.py::create_fit_card`, added clean price formatting (`f"${int(raw_price)}"` for whole-dollar amounts like `$30` instead of `$30.0`) and normalized platform casing using `.capitalize()` (`Depop`, `Poshmark`, `ThredUp`).
2. In `agent.py::parse_query`, expanded the price regex parser to recognize natural language variations such as `less than $X`, `below $X`, and `cheaper than $X` in addition to `under $X`.

**Which failure it was meant to fix:**
Addresses caption realism in Criterion 4 (preventing robotic float price strings like `$30.0` and lowercase platform tags) and improves query parsing robustness for conversational budget constraints.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. state preservation across tools | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card format and variety | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. empty wardrobe | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**
Yes. Across all 5 tries in `results/run_2026-10-01_0205_after.md`, every generated fit card caption cleanly featured natural integer prices (`$30`, `$42`, `$45`) and capitalized platform names (`Depop`, `Poshmark`), eliminating awkward decimal representations like `$30.0` while maintaining full criterion compliance (5/5).

---

## What's Still Broken

All five primary acceptance criteria targets are currently MET. However, in future iterations, two minor areas can be further enhanced:
1. **Semantic Search / Synonym Matching:** The search tool currently relies on keyword token overlap and style tags. A query asking for "sneakers" will not find listings tagged only as "kicks" or "trainers" unless those terms are explicitly present in the title or description. Adding vector embeddings or TF-IDF / BM25 would broaden synonym recall.
2. **Persistent Multi-Turn Dialogue:** The session state currently executes a single-turn query lifecycle (search → outfit → fit card). Supporting iterative follow-ups (e.g., "show me the next option" or "try a different color") would require keeping the session alive across user turns.




<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
