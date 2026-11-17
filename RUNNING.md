# Running FitFindr

FitFindr is a thrift-shopping agent. You describe what you want, it finds a
listing, suggests an outfit from your wardrobe, and writes a fit card caption.
It runs locally from the command line (capstone Path B: local with logs).

---

## Quick start (Windows PowerShell)

```powershell
# Clone the project
git clone https://github.com/ponzek/ai201-project2-fitfindr-starter-v2026.git

# Enter the project folder
cd ai201-project2-fitfindr-starter-v2026

# Create and activate the environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env from the example, then open .env and paste in your own GEMINI_API_KEY
copy .env.example .env

# Verify setup
python test.py

# Run FitFindr
python app.py ask 'vintage graphic tee under $30'
```

**macOS / Linux:** use `python3 -m venv .venv`, `source .venv/bin/activate`, and
`cp .env.example .env` for those three lines. Everything else is the same.

You're ready when `python test.py` passes. Activate the environment again each
time you open a new terminal; you should see `(.venv)` at the start of the prompt.

> **Use single quotes around queries.** In PowerShell, `"... under $30"` in
> double quotes silently drops `$30` (it's read as a variable), so the price
> limit disappears with no error.

---

## What the environment needs

| Thing | Value |
|---|---|
| Python | **Use 3.11, 3.12, or 3.13** (what `requirements.txt` supports). The capstone runs were done on 3.10.10, which worked, but `test.py` flags it as unsupported, so don't rely on it. |
| Packages | `pip install -r requirements.txt`. Pinned with upper and lower bounds: `python-dotenv>=1.0,<1.2`, `google-genai>=1.0,<2.0`, `mcp>=1.0,<2.0`, `flask>=3.0,<4.0`, `gunicorn>=21.2,<24.0` |
| API key | A free Gemini key from aistudio.google.com, saved as `GEMINI_API_KEY` in `.env`. Never commit `.env`; it's in `.gitignore`. |
| Model files | None. FitFindr calls the Gemini API (`gemini-3.5-flash-lite`); nothing is downloaded. |
| Network | Needed for the model calls. |

---

## Commands

| Command | What it does |
|---|---|
| `python test.py` | Checks the environment, packages, key, and one model call |
| `python app.py ask '...'` | Runs the agent on one query |
| `python app.py ask '...' --trace` | Same, printing each step |
| `python app.py ask '...' --empty-wardrobe` | Runs as a user with nothing in their wardrobe |
| `python app.py examples` | Queries worth trying, including one that matches nothing |
| `python app.py listings --full -n 6` | Shows six listings in full |
| `python run_log.py` | Prints the last 10 records from the run log |
| `python capstone_eval.py --label before` | Runs the five capstone criteria for 3 trials (about 5 minutes) and writes `results/capstone_<label>.md` and `.json` |

### Try these

```powershell
python app.py ask 'vintage graphic tee under $30'          # normal run
python app.py ask 'designer ballgown size XXS under $5'    # nothing matches: stops early, no model calls
```

To see the failure fallback, break the model name for one run:

```powershell
$env:AI201_MODEL='no-such-model'; python app.py ask 'denim jacket under $50'; Remove-Item Env:AI201_MODEL
```

You should still see the listing (`Found: Denim Jacket ...`) plus a `Note:`
saying the outfit step failed.

---

## The run log

Every run, including failed ones, adds one JSON line to `logs/runs.jsonl` with
the timestamp, query, outcome, time per step, model calls, and tokens. The code
is in `run_log.py`. The README's **Instrumentation** section explains each field.

---

## Settings for testing

Set these as environment variables in PowerShell, for example `$env:AI201_CACHE='0'`.

| Variable | What it does |
|---|---|
| `AI201_CACHE=0` | Turns off the response cache, so every run makes real model calls. Use it for any measured run. |
| `AI201_MODEL_TIMEOUT=20` | Seconds before a model call is abandoned. Minimum 10 (Gemini rejects less). |
| `AI201_MODEL=no-such-model` | Forces a model failure, to test the fallback. |

---

## Where everything lives

| File | What it does |
|---|---|
| `app.py` | The command line |
| `agent.py` | The planning loop, the fallback when a model step fails, and the call to the run log |
| `tools.py` | The three tools: `search_listings`, `suggest_outfit`, `create_fit_card` |
| `generate.py` | The only code that calls Gemini: pacing, retries, time limit, token counts |
| `run_log.py` | Writes and reads `logs/runs.jsonl` |
| `capstone_eval.py` | Runs the capstone criteria and builds the results table |
| `config.py` | Settings: model, temperature, cache, time limit, rate limit |
| `mcp_server.py` / `mcp_client.py` | Search runs through an MCP server |
| `criteria.md` | Acceptance criteria (Unit 9 capstone at the bottom) |
| `results/` | Saved test results |
| `data/` | 40 listings and the example wardrobe |

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `No GEMINI_API_KEY found` | No `.env`, or the key wasn't pasted in. On Windows, check it didn't save as `.env.txt`. |
| `Note: Couldn't suggest an outfit: The model rejected your API key` | Bad key in `.env`. The listing still shows; that's the fallback working. |
| `[rate limit] ... Waiting 34s` | The free tier allows 15 requests a minute. It's pacing itself; leave it. |
| A price limit you typed is ignored | You used double quotes in PowerShell. Use single quotes. |
| `IncompleteFieldDefinitionWarning: Field 'lifespan'` | Harmless noise from the MCP library. Ignore it. |
| Every run gives word-for-word the same text | The cache is on. Set `AI201_CACHE=0`. |
| The first run is slower | Normal: a run takes about 4–6 seconds, about 2 of which is starting the MCP server for search. |
