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

<!-- ═══════════════════════ UNIT 9 — THE CAPSTONE ═══════════════════════
     The capstone sections come first. The Unit 3 and Unit 4 sections below
     are left as they were submitted.
     ═════════════════════════════════════════════════════════════════════ -->

# Unit 9 — Capstone

## What This Extends

This extends **FitFindr**, my thrift-shopping agent from Units 3 and 4. It
searches listings, then makes two Gemini calls: one to suggest an outfit and
one to write a fit card.

**What's new:** when a model call fails, the run no longer ends with only an
error. The user still gets the listing that search found, plus a clear note
saying which step failed.

## The Shape

**Shape B — harden against failure.**

Right now, if either Gemini call fails, hangs, or returns nothing, the user
loses everything, including the listing search already found. I'm adding one
failure layer around the two model steps: a time limit on each call, and a
fallback so the user always gets the listing plus a note about what didn't
work.

**Out of scope:**

- I'm not changing search, synonyms, or the MCP server.
- I'm not adding multi-turn conversation or showing a second listing.
- I'm not hosting it. It runs locally with logs (Path B).

**Stretch I'm declaring before I build:** a latency breakdown — how long each
step of one run takes (search, outfit, fit card), measured from the logs.

## Running It

**Path B — local with logs.** No hosting. Everything a reader needs is in
[RUNNING.md](RUNNING.md): the start command, the Python version, the pinned
packages, and the settings used to test failures. There are no model files;
the model is called over the Gemini API.

```powershell
python app.py ask 'vintage graphic tee under $30'
```

The committed run record is `logs/runs.jsonl`.

## Instrumentation

Every run writes one JSON line to `logs/runs.jsonl`, even if it fails or
crashes. The code is in `run_log.py::write_record`, called from
`agent.py::run_agent`.

| Field | What it holds |
|---|---|
| `timestamp` | When the run finished (UTC) |
| `query`, `wardrobe_items` | What came in |
| `outcome` | `complete`, `partial` (a model step failed but the listing was kept), `stopped_early` (no listings), or `crashed` |
| `selected_item`, `has_outfit`, `has_fit_card` | What came out |
| `error`, `warning` | Why it stopped early, or which model step failed |
| `duration_s` | Whole run, in seconds |
| `step_s` | Seconds per step: `search`, `outfit`, `fit_card` |
| `model_calls`, `prompt_tokens`, `output_tokens` | What the run cost |
| `model`, `timeout_s` | Settings in use |

**12 entries from `logs/runs.jsonl`** (10 normal runs with the cache off, then
an impossible query, then a forced model failure with `AI201_MODEL=no-such-model`):

```
{"timestamp": "2026-11-09T03:11:58+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.34, "step_s": {"search": 2.314, "outfit": 2.186, "fit_card": 0.838}, "model_calls": 2, "prompt_tokens": 724, "output_tokens": 206, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:04+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.351, "step_s": {"search": 2.259, "outfit": 2.253, "fit_card": 0.838}, "model_calls": 2, "prompt_tokens": 741, "output_tokens": 210, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:11+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 6.439, "step_s": {"search": 2.801, "outfit": 2.648, "fit_card": 0.989}, "model_calls": 2, "prompt_tokens": 742, "output_tokens": 220, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:17+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.623, "step_s": {"search": 2.501, "outfit": 2.362, "fit_card": 0.759}, "model_calls": 2, "prompt_tokens": 735, "output_tokens": 203, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:23+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.828, "step_s": {"search": 2.418, "outfit": 2.468, "fit_card": 0.94}, "model_calls": 2, "prompt_tokens": 732, "output_tokens": 228, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:29+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.488, "step_s": {"search": 2.388, "outfit": 2.158, "fit_card": 0.94}, "model_calls": 2, "prompt_tokens": 739, "output_tokens": 235, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:36+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.967, "step_s": {"search": 2.403, "outfit": 2.51, "fit_card": 1.053}, "model_calls": 2, "prompt_tokens": 742, "output_tokens": 220, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:42+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.397, "step_s": {"search": 2.28, "outfit": 2.233, "fit_card": 0.883}, "model_calls": 2, "prompt_tokens": 746, "output_tokens": 222, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:48+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.803, "step_s": {"search": 2.777, "outfit": 2.181, "fit_card": 0.844}, "model_calls": 2, "prompt_tokens": 741, "output_tokens": 218, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:12:56+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 7.16, "step_s": {"search": 3.17, "outfit": 3.023, "fit_card": 0.966}, "model_calls": 2, "prompt_tokens": 735, "output_tokens": 212, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:14:09+00:00", "query": "designer ballgown size XXS under $5", "wardrobe_items": 10, "outcome": "stopped_early", "selected_item": null, "has_outfit": false, "has_fit_card": false, "error": "No matching listings found. Try raising your price limit above $5.0 or searching for sizes other than 'XXS' or broadening your search terms (tried 'designer ballgown').", "warning": null, "duration_s": 2.387, "step_s": {"search": 2.386}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
{"timestamp": "2026-11-09T03:14:12+00:00", "query": "denim jacket under $50", "wardrobe_items": 10, "outcome": "partial", "selected_item": "lst_007", "has_outfit": false, "has_fit_card": false, "error": null, "warning": "Couldn't suggest an outfit: The model name 'no-such-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.", "duration_s": 3.45, "step_s": {"search": 2.161, "outfit": 1.287}, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "model": "no-such-model", "timeout_s": 20.0}
```

## What It Costs

**Measured per-run cost: about \$0.00076 (738 prompt + 217 output tokens, 2 model calls).**

How I measured it: I ran `python app.py ask 'vintage graphic tee under $30'`
10 times with the cache off (`AI201_CACHE=0`). Each run logged the token
counts Gemini reported for its two calls. I averaged the 10 records (the first
10 entries above).

| | Average per run |
|---|---|
| Prompt tokens | 737.7 |
| Output tokens | 217.4 |
| Wall-clock time | 5.84 s |

Converting tokens to dollars at the paid price for `gemini-3.5-flash-lite`
(\$0.30 per 1M input tokens, \$2.50 per 1M output tokens):

```
input:  737.7 × $0.30 / 1,000,000 = $0.000221
output: 217.4 × $2.50 / 1,000,000 = $0.000544
one run                           = $0.000765
```

**A hundred people a day, one run each:**

```
100 × $0.000765 = $0.0765 per day   (about 8 cents)
$0.0765 × 30    = $2.30 per month
```

On the free tier I'm using, the real limit isn't money. It's 15 requests a
minute (`config.REQUESTS_PER_MINUTE`). At 2 calls per run, that's about 7 runs
a minute.

## Latency Breakdown (stretch)

Measured from `step_s` across the same 10 runs:

| Step | Average | Fastest | Slowest |
|---|---|---|---|
| `search` (via MCP) | 2.53 s | 2.26 s | 3.17 s |
| `suggest_outfit` (model) | 2.40 s | 2.16 s | 3.02 s |
| `create_fit_card` (model) | 0.91 s | 0.76 s | 1.05 s |

**Search is the slowest step, which surprised me.** Calling
`tools.py::search_listings` directly takes 0.0008 s (I timed it once on its
own). The other ~2.5 s is MCP overhead: `mcp_client.py::call_tool` launches
`mcp_server.py` as a brand-new process on every call (`stdio_client`) before
it can search. The outfit call is close behind; the fit card is fast because
its output is short.

## Run Log and Verdicts

Run with `python capstone_eval.py --label before`. Each run is a real
`python app.py ask ...` in its own process with the cache off. One trial is
15 runs: 5 forced failures (`AI201_MODEL=no-such-model`, query
`'denim jacket under $50'`), 5 normal runs (`'vintage graphic tee under $30'`),
and 5 empty searches (`'designer ballgown size XXS under $5'`). Nothing was
changed between trials; there is a 60 s pause between trials so the free-tier
per-minute limit resets. Raw output: `results/capstone_before.json`.

### Run Log — Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Failed model step still shows the listing | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 2. Every run is logged | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 3. Normal run under 7 s | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3b. Tightened (diagnosis): normal run under 5 s | 4 of 5 | 1/5 | 5/5 | 5/5 | MISSED |
| 4. Failure note has no raw error | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. No results means no model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Row 3b is not one of my five criteria. It is the tighter target from the
diagnosis below, scored from the same saved runs.

Normal-run times (`duration_s`), before:
Trial 1 [5.089, 5.475, 5.009, 5.0, 4.688], Trial 2 [4.402, 4.196, 4.399, 4.454, 4.564], Trial 3 [4.541, 4.561, 4.951, 4.844, 4.34].

### Real output (Trial 1, before)

**Criteria 1 and 4** — printed by `app.py::_ask_one`; the listing is kept and
the note is set by `agent.py::_run_steps` (the `except ModelUnavailable` around
`suggest_outfit`), and the note text comes from `generate.py::_explain`:

```
Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark
  Note:     Couldn't suggest an outfit: The model name 'no-such-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.
```

**Criterion 2** — the log line written by `run_log.py::write_record` for that
same forced failure:

```
{"timestamp": "2026-11-09T04:17:30+00:00", "query": "denim jacket under $50", "wardrobe_items": 10, "outcome": "partial", "selected_item": "lst_007", "has_outfit": false, "has_fit_card": false, "error": null, "warning": "Couldn't suggest an outfit: The model name 'no-such-model' did not resolve. If you changed AI201_MODEL in your .env, put it back. Otherwise post in the help channel — this is not something you caused.", "duration_s": 3.121, "step_s": {"search": 1.895, "outfit": 1.225}, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "model": "no-such-model", "timeout_s": 20.0}
```

**Criterion 3** — log line for a normal run (`run_log.py::write_record`), see
`duration_s`:

```
{"timestamp": "2026-11-09T04:17:50+00:00", "query": "vintage graphic tee under $30", "wardrobe_items": 10, "outcome": "complete", "selected_item": "lst_006", "has_outfit": true, "has_fit_card": true, "error": null, "warning": null, "duration_s": 5.089, "step_s": {"search": 1.955, "outfit": 2.247, "fit_card": 0.886}, "model_calls": 2, "prompt_tokens": 728, "output_tokens": 196, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
```

**Criterion 5** — log line for an empty search (`run_log.py::write_record`),
see `model_calls`; the stop is the branch in `agent.py::_run_steps`:

```
{"timestamp": "2026-11-09T04:18:15+00:00", "query": "designer ballgown size XXS under $5", "wardrobe_items": 10, "outcome": "stopped_early", "selected_item": null, "has_outfit": false, "has_fit_card": false, "error": "No matching listings found. Try raising your price limit above $5.0 or searching for sizes other than 'XXS' or broadening your search terms (tried 'designer ballgown').", "warning": null, "duration_s": 2.03, "step_s": {"search": 2.029}, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "model": "gemini-3.5-flash-lite", "timeout_s": 20.0}
```

### Verdicts and Diagnosis

All five criteria were MET in all three trials.

| # | Verdict | How I decided |
|---|---|---|
| 1 | MET | 3/3 in every trial: `Found:` line had title and price, and the `Note:` named the outfit step. |
| 2 | MET | 15/15 in every trial: exactly one new line per run, all fields present, and the outcome matched (`partial`, `complete`, `stopped_early`). |
| 3 | MET | 5/5 in every trial; slowest run 5.475 s, well under 7 s. |
| 4 | MET | 5/5 in every trial: no `Traceback`, `400`, `INVALID_ARGUMENT`, or `{'error'`. |
| 5 | MET | 5/5 in every trial: `model_calls` was 0. |

**Which target was set too low, and the tighter one:**
Criterion 3, a normal run under 7 s in 4 of 5, was too easy. I picked 7 s from
10 earlier runs that averaged 5.84 s. In these trials normal runs averaged
4.70 s and the slowest took 5.48 s, so it scored 5/5 every time with more than
1.5 s to spare. A run could have slowed by a full second without the criterion
noticing. I also wrote in `criteria.md` that a 5-second target "would fail every
run" because search took about 2.5 s then. Search averaged 1.82 s here, and most
runs came in under 5 s, so that was wrong.

The tighter target is **a normal run under 5 s in 4 of 5** (row 3b). Trial 1
misses it at 1/5.

**Diagnosis of the tightened target's miss (Trial 1, 1/5):**
The miss is latency in two tool steps: `tools.py::suggest_outfit` and the search
call through `mcp_client.py::call_tool`. No logic failed, and every run
completed. Those two steps take about 3.8 s of a normal run (outfit 2.00 s,
search 1.82 s). With the fit card at 0.88 s, the average run is 4.70 s, which
leaves only about 0.3 s under the target. Search is slow because `call_tool`
starts a new `mcp_server.py` process on every call. The outfit step is slow
because its prompt allowed two full looks with headings, the longest text in
the run. The whole run writes about 224 output tokens, outfit and fit card
combined.

| Before, normal runs | Run average | Search | Outfit | Output tokens | Empty searches (no model) |
|---|---|---|---|---|---|
| Trial 1 | 5.05 s | 1.97 s | 2.21 s | 216 | 2.07 s |
| Trial 2 | 4.40 s | 1.64 s | 1.85 s | 225 | 1.81 s |
| Trial 3 | 4.65 s | 1.86 s | 1.93 s | 230 | 1.89 s |

That small margin is why a slow trial went over: four of Trial 1's five runs
landed between 5.0 s and 5.48 s. Output length does not explain why Trial 1 was
the slow one, because it wrote the fewest tokens. Search and the outfit call
both ran slower in that trial, and so did empty searches, which make no model
calls. That points to general slowness during Trial 1, from the network or my
machine; the logs can't tell me which. The outfit text was still the right thing
to cut, because it is the largest step and search was out of scope.

## The Improvement

**What I changed:** in `tools.py::suggest_outfit`, the prompt now asks for ONE
outfit in 2 or 3 sentences with no headings (it asked for "1 or 2"), and the
call passes `max_output_tokens=150` through a new optional argument to
`generate.py::generate`. Commit `2a6f7c0`.

**Which failure it was meant to fix:** the tightened target 3b (under 5 s),
missed in Trial 1. The outfit call was the biggest model step, and it was
writing two full looks.

### Run Log — After

Run with `python capstone_eval.py --label after`, same setup. Raw output:
`results/capstone_after.json`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Failed model step still shows the listing | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 2. Every run is logged | 15 of 15 | 15/15 | 15/15 | 15/15 | MET |
| 3. Normal run under 7 s | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3b. Tightened (diagnosis): normal run under 5 s | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Failure note has no raw error | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. No results means no model calls | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Normal-run times (`duration_s`), after:
Trial 1 [4.222, 4.375, 3.964, 4.354, 4.494], Trial 2 [4.669, 4.428, 4.115, 4.219, 4.219], Trial 3 [4.583, 4.315, 4.23, 4.712, 4.138].

| 15 normal runs | Before | After |
|---|---|---|
| Average run | 4.70 s | 4.34 s |
| Slowest run | 5.48 s | 4.71 s |
| Outfit step (average) | 2.00 s | 1.71 s |
| Search step (average, not changed) | 1.82 s | 1.74 s |
| Output tokens per run | 224 | 140 |

**Did it help, and how do I know:** yes. The tightened target went from MISSED
(1/5, 5/5, 5/5) to MET (5/5 in all three trials), and every original criterion
stayed MET. The outfit step got 0.29 s faster on average. Part of the overall
gain is likely normal variation: search, which I didn't change, also got
0.08 s faster, and only Trial 1 was slow before.

**What it cost elsewhere:** users now get one outfit instead of two. The
Unit 3 Tool Inventory still says "1–2 outfit combinations". Output tokens fell
37%, so each run is also slightly cheaper. An "after" outfit:

```
Outfit:   Channel effortless 90s grunge by pairing the vintage graphic tee with your baggy dark wash jeans and black combat boots for that classic slouchy silhouette. Throw your slightly cropped vintage black denim jacket over the top and accessorize with your black crossbody bag to complete the ultimate streetwear-ready look.
```


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
- **Returns:** A list of listing dicts (at most 10, set by `config.SEARCH_RESULT_LIMIT`), best match first, each containing `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), and `platform` (str). The trace prints only the first 3 titles and counts the rest (`trace.py::_short`), and the agent uses only the first result.
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

**Moment 3 (Unit 4)**

- *What I asked for:* A fix for robotic float price representations (e.g., `"$30.0"` or `"$24.00"`) and unformatted lowercase platforms (`depop`) diagnosed during Criterion 4 testing.
- *What came back:* A suggestion to apply global regular expressions across the model's finished caption output after generation to replace float patterns.
- *What I changed:* Rejected post-generation regex substitution because post-processing generated text risks corrupting valid numbers in descriptions or sentences. Instead, implemented clean data preprocessing in `tools.py::create_fit_card` before prompt assembly, converting whole-dollar floats to integers (`f"${int(raw_price)}"`) and capitalizing platform names (`platform.capitalize()`). This solved the issue at the source without altering the LLM's natural sentence structure.

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

**Real output for each criterion (from Try 1)**, pasted as text, naming the file and function
that produced it:

```
Criterion 1 — matching query completes
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

```
Criterion 2 — impossible query stops early
File & Function: agent.py::run_agent (Scenario 2, Try 1)
Query: 'designer ballgown size XXS under $5'
Wardrobe: example

stopped early: yes
error: "No matching listings found. Try raising your price limit above $5.0 or searching for sizes other than 'XXS' or broadening your search terms (tried 'designer ballgown')."
selected_item: None
search_results: []
fit_card: None
```

```
Criterion 3 — state preservation across tools
File & Function: agent.py::run_agent (Scenario 4, Try 1)
Query: '90s track jacket in size M'
Wardrobe: example

stopped early: no
session["search_results"][0]["id"]: lst_004
session["selected_item"]["id"]: lst_004
title: 90s Track Jacket — Navy/White Stripe
price: $45.0
platform: poshmark

Outfit Suggestion:
**Look 1: 90s Streetwear Casual**
Pair the track jacket over your fitted **white ribbed tank top** and **baggy straight-leg jeans (dark wash)**. Finish the fit with your **chunky white sneakers** and the **black crossbody bag** for an effortless, vintage athletic vibe.

**Look 2: High-Low Contrast**
Create a cool menswear-inspired silhouette by layering the track jacket with your **wide-leg khaki trousers** and the **white ribbed tank top** tucked in. Add your **chunky white sneakers** and cinch the look with the **brown leather belt** to tie the navy and khaki tones together.

Fit Card:
Still obsessing over how good this authentic 90s navy and white striped track jacket looks with a baggy denim street fit or high-waisted khakis! I just listed this lightweight, full-zip vintage gem over on my Poshmark for $45, and it is the ultimate layering piece for nailing that effortless retro athletic vibe. Run, don't walk, to grab it before I change my mind and keep it for myself!
```

```
Criterion 4 — fit card format and variety
File & Function: agent.py::run_agent (Scenario 5, Try 1)
Query: 'silk slip dress in midi length under $40'
Wardrobe: example

stopped early: no
selected_item: 90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)

Fit Card:
Just scored the ultimate 90s floral midi slip dress for only $30.0 on depop, and I’m already obsessed! I'm totally planning to grunge it up with an oversized crewneck and combat boots, or keep it casual-cool layered over straight-leg jeans with chunky sneaks. Snag this dreamy vintage piece on my depop shop before someone else beats you to it!
```

```
Criterion 5 — empty wardrobe
File & Function: agent.py::run_agent (Scenario 3, Try 1)
Query: 'denim jacket under $50'
Wardrobe: empty

stopped early: no
selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)

Outfit Suggestion:
This light wash, cropped vintage denim jacket is a streetwear staple that adds instant structure and effortless cool to any frame. Build your capsule wardrobe around it by pairing it with a simple white cotton t-shirt, high-waisted black straight-leg trousers, and retro sneakers for an easy, classic-meets-streetwear look. Alternatively, throw it over a black ribbed midi dress with chunky black boots to balance the rugged denim texture with a sleek, feminine silhouette.

Fit Card:
I am still obsessing over this light wash, cropped denim jacket with the absolute best structured shoulders, and I scored it on Poshmark for just $42! It’s totally a blank canvas waiting to be customized, but right now I'm loving it thrown over a black midi dress with chunky boots for that effortless streetwear vibe. Grab it in my closet before I change my mind and keep it for my own capsule wardrobe!
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

All five criteria met their targets on the initial run (5/5 passes across all five scenarios). 

**Target Assessment & Honesty Check:**
Because all five targets were MET at 5/5, I evaluated whether the targets were set too leniently:
- **Criterion 1 (4 of 5):** The target was set conservatively at 4/5 assuming keyword search might miss phrasing variants. However, our token-matching and size-filtering logic was robust enough to hit 5/5 consistently.
- **Criterion 5 (4 of 5):** The target was set at 4/5 anticipating potential model hallucination on empty wardrobes. The dedicated prompt branch in `tools.py::suggest_outfit` handled this cleanly every time.
- **The criterion I would tighten:** **Criterion 4 (Fit card format and variety)**. The current target of 4/5 allows for generative slop. I would tighten it to **5 of 5** and make the acceptance condition stricter by explicitly requiring whole-dollar currency formatting (disallowing `$30.0` or `$24.00`) and canonical platform casing (requiring `Depop`, `Poshmark`, `ThredUp` instead of raw JSON lowercase like `depop`).

During qualitative inspection of the 5/5 run logs, two specific mechanisms produced minor UX flaws:
1. **Unformatted Float Stringification (Place: tool / model prompt in `create_fit_card`):** Passing `new_item["price"]` as a raw float caused the prompt to instruct the model with values like `30.0` or `24.0`, leading to awkward social captions (e.g., "for only $24.00" or "$30.0" instead of "$24" or "$30").
2. **Platform Capitalization Inconsistency (Place: tool / input data in `create_fit_card`):** The catalog JSON stores platform names in lowercase (`depop`, `thredUp`, `poshmark`). Without normalization before prompt injection, the model occasionally mirrored `depop` instead of the capitalized brand name `Depop`.




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
- *What changed in code:* In `mcp_server.py`, registered `search_listings` with FastMCP (`@mcp.tool()`) including full docstrings and typed schema parameters (`description: str`, `size: str | None = None`, `max_price: float | None = None`). In `agent.py::run_agent`, replaced the direct function call with `mcp_client.call_tool("search_listings", search_args)`.
- *Whether anything behaved differently after:* No functional behavior changed. MCP serializes requests and responses over stdio, but `mcp_client._unwrap()` converts the JSON payload back into the identical `list[dict]` structure. All downstream tools, state propagation in `session`, and loop branches continued operating without requiring any modification.

### Failure Modes Handled

All three failure modes were intentionally triggered and verified:

1. **Empty search:**
   - *Trigger command:* `python app.py ask 'authentic medieval chainmail armour under $5' --trace`
   - *Agent message:* `"No matching listings found. Try raising your price limit above $5.0 or broadening your search terms (tried 'authentic medieval chainmail armour')."`
   - *Handler behavior:* In `agent.py::run_agent`, checks `if not session["search_results"]`. Halts early before subsequent tool calls, sets `session["error"]` with actionable guidance indicating which constraints to loosen, and preserves `fit_card` as `None`.

2. **Empty wardrobe:**
   - *Trigger command:* `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace`
   - *Agent message:* Successfully generates styling suggestions based on universal silhouette and layering principles (e.g. pairing with high-waisted denim and leather jackets) rather than crashing or returning an empty string.
   - *Handler behavior:* In `tools.py::suggest_outfit`, detects when `len(wardrobe.get("items", [])) == 0` and pivots prompt instructions to recommend versatile wardrobe staples and styling advice without hallucinating non-existent wardrobe IDs.

3. **Model unavailable:**
   - *Trigger command:* Corrupted key in `.env`, ran `python app.py ask 'lime green neon windbreaker jacket under $55' --trace`
   - *Agent message:* `"Model unavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com."`
   - *Handler behavior:* In `agent.py::run_agent`, wraps calls to `suggest_outfit` and `create_fit_card` in `try...except ModelUnavailable`. Intercepts the exception, prevents raw traceback dumps or hanging, sets `session["error"]` with the human-readable explanation from `generate.py::_explain()`, and terminates cleanly.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
In `tools.py::create_fit_card`, added clean price formatting (`f"${int(raw_price)}"` for whole-dollar amounts like `$30` instead of `$30.0`) and normalized platform casing using `.capitalize()` (`Depop`, `Poshmark`, `ThredUp`). This is the one measured improvement.

*Separate change, not part of the measured improvement:* in the same round I also expanded the price regex in `agent.py::parse_query` to recognize `less than $X`, `below $X`, and `cheaper than $X`. None of my five criteria use those phrasings (every test query says `under $X`), so the after-run doesn't measure this change, and it can't explain any difference between the two tables.

**Which failure it was meant to fix:**
Addresses caption realism in Criterion 4 (preventing robotic float price strings like `$30.0` and lowercase platform tags).

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. state preservation across tools | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card format and variety | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. empty wardrobe | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**
Yes, the improvement helped: across all 5 re-run tries, every generated fit card caption in `results/run_2026-10-01_0205_after.md` cleanly featured natural integer prices (`$30`, `$42`, `$45`) and properly capitalized platform names (`Depop`, `Poshmark`), eliminating awkward decimal representations like `$30.0` while maintaining 100% criterion compliance (5/5).

---

## What's Still Broken

All five primary acceptance criteria targets were MET (5/5). However, pretending nothing is left to improve is not honest:

1. **Vocabulary / Synonym Misses in Keyword Search (Criterion 1 edge cases):**
   - *What's still broken:* Keyword search only matches literal tokens and style tags in the listings catalog. If a user asks for "kicks", it will miss items described strictly as "sneakers" or "trainers".
   - *What I'd do:* Integrate TF-IDF synonym expansions or vector embeddings with cosine similarity to perform semantic retrieval alongside keyword matching.
   - *Why I stopped there:* Unit 4 strictly enforces a "one change only" rule between evaluation runs. Adding vector embeddings would require external model calls, new dependencies, and changes to multiple components simultaneously.

2. **Persistent Multi-Turn Dialogue:**
   - *What's still broken:* The agent operates strictly as a single-turn pipeline (query → search → outfit → fit card). If the user wants to inspect alternative candidate matches from `session["search_results"][1:]` or ask for adjustments, there is no interactive conversational memory.
   - *What I'd do:* Maintain session history across turns and implement an intent branch to support follow-up requests like "show me the next option" or "try styling with different colors".
   - *Why I stopped there:* The evaluation criteria and unit requirements are designed around single-turn planning loop validation, so multi-turn persistence was out of scope.




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

       [x] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [x] Run Log — Before, five criteria, five tries each
       [x] Real output pasted underneath, naming file and function
       [x] A verdict on every criterion
       [x] A diagnosis for every miss, naming a place AND a mechanism
       [x] Loop Trace, with the MCP call visible in it
       [x] All three failure modes triggered and handled
       [x] One improvement, with Run Log — After in the same format
       [x] What's Still Broken
       [x] At least four new commits
       [x] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
