"""
Capstone: runs the five Unit 9 criteria (criteria.md) for 3 trials.

Each run is a real `python app.py ask ...` in its own process, so the test
sees exactly what a user would see. The cache is off for every run.

One trial = 15 runs:
    5 forced failures  (AI201_MODEL=no-such-model)  -> criteria 1, 2, 4
    5 normal runs                                   -> criteria 2, 3
    5 empty searches                                -> criteria 2, 5

    python capstone_eval.py --label before

Writes the table and the raw output to results/capstone_<label>.md and .json.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

import config
import run_log

FAIL_QUERY = "denim jacket under $50"
NORMAL_QUERY = "vintage graphic tee under $30"
EMPTY_QUERY = "designer ballgown size XXS under $5"

LOG_FIELDS = ["timestamp", "query", "outcome", "step_s", "prompt_tokens", "output_tokens"]
RAW_ERROR_SIGNS = ["Traceback", "400", "INVALID_ARGUMENT", "{'error'"]
TRIALS = 3
RUNS_PER_GROUP = 5
PAUSE_BETWEEN_TRIALS_S = 60  # lets the free-tier per-minute limit reset


def count_log_lines() -> int:
    if not run_log.LOG_FILE.exists():
        return 0
    return len(run_log.LOG_FILE.read_text(encoding="utf-8").splitlines())


def run_app(query: str, broken_model: bool = False) -> dict:
    """Run one query through app.py and return what it printed and logged."""
    env = dict(os.environ, AI201_CACHE="0", PYTHONIOENCODING="utf-8")
    env.pop("AI201_MODEL", None)
    if broken_model:
        env["AI201_MODEL"] = "no-such-model"

    lines_before = count_log_lines()
    proc = subprocess.run(
        [sys.executable, "app.py", "ask", query],
        capture_output=True, text=True, encoding="utf-8", env=env,
        cwd=config.ROOT,
    )
    lines_after = count_log_lines()

    new_records = run_log.read_records(lines_after - lines_before) if lines_after > lines_before else []
    return {
        "query": query,
        "broken_model": broken_model,
        "stdout": proc.stdout,
        "exit_code": proc.returncode,
        "new_log_lines": lines_after - lines_before,
        "record": new_records[-1] if new_records else None,
    }


# ── one check per criterion, per run ─────────────────────────────────────────

def note_line(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.strip().startswith("Note:"):
            return line.strip()
    return ""


def check_c1(run: dict) -> bool:
    """Listing title and price shown, plus a note naming the failed step."""
    out = run["stdout"]
    shows_listing = "Found:" in out and "$" in out.split("Found:", 1)[1].splitlines()[0]
    note = note_line(out)
    names_step = "outfit" in note or "fit card" in note
    return shows_listing and names_step


def check_c2(run: dict, expected_outcome: str) -> bool:
    """Exactly one new log line, with every field, and the right outcome."""
    record = run["record"]
    if run["new_log_lines"] != 1 or record is None:
        return False
    if any(field not in record for field in LOG_FIELDS):
        return False
    return record["outcome"] == expected_outcome


def check_c3(run: dict) -> bool:
    """Normal run finishes in under 7 seconds (duration_s)."""
    record = run["record"]
    return bool(record) and record["outcome"] == "complete" and record["duration_s"] < 7.0


def check_c4(run: dict) -> bool:
    """The note has no raw API error or stack trace."""
    note = note_line(run["stdout"])
    if not note:
        return False
    return not any(sign in note for sign in RAW_ERROR_SIGNS) and "Traceback" not in run["stdout"]


def check_c5(run: dict) -> bool:
    """Empty search makes 0 model calls."""
    record = run["record"]
    return bool(record) and record["model_calls"] == 0


# ── a trial ──────────────────────────────────────────────────────────────────

def run_trial(n: int) -> dict:
    print(f"\n=== Trial {n} ===", flush=True)
    failures = [run_app(FAIL_QUERY, broken_model=True) for _ in range(RUNS_PER_GROUP)]
    print("  forced failures done", flush=True)
    normals = [run_app(NORMAL_QUERY) for _ in range(RUNS_PER_GROUP)]
    print("  normal runs done", flush=True)
    empties = [run_app(EMPTY_QUERY) for _ in range(RUNS_PER_GROUP)]
    print("  empty searches done", flush=True)

    c2_runs = ([check_c2(r, "partial") for r in failures]
               + [check_c2(r, "complete") for r in normals]
               + [check_c2(r, "stopped_early") for r in empties])

    return {
        "trial": n,
        "scores": {
            1: (sum(check_c1(r) for r in failures[:3]), 3),
            2: (sum(c2_runs), len(c2_runs)),
            3: (sum(check_c3(r) for r in normals), RUNS_PER_GROUP),
            4: (sum(check_c4(r) for r in failures), RUNS_PER_GROUP),
            5: (sum(check_c5(r) for r in empties), RUNS_PER_GROUP),
        },
        "durations": [r["record"]["duration_s"] if r["record"] else None for r in normals],
        "runs": {"failures": failures, "normals": normals, "empties": empties},
    }


# The target for each criterion, as written in criteria.md.
CRITERIA = {
    1: ("Failed model step still shows the listing", 3, 3),
    2: ("Every run is logged", 15, 15),
    3: ("Normal run under 7 s", 4, 5),
    4: ("Failure note has no raw error", 5, 5),
    5: ("No results means no model calls", 5, 5),
}


def build_table(trials: list[dict]) -> str:
    rows = ["| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |",
            "|---|---|---|---|---|---|"]
    for c, (name, need, out_of) in CRITERIA.items():
        cells = []
        met = True
        for t in trials:
            got, total = t["scores"][c]
            cells.append(f"{got}/{total}")
            if got < need:
                met = False
        verdict = "MET" if met else "MISSED"
        rows.append(f"| {c}. {name} | {need} of {out_of} | " + " | ".join(cells) + f" | {verdict} |")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="before")
    args = parser.parse_args()

    trials = []
    for n in range(1, TRIALS + 1):
        if n > 1:
            print(f"  pausing {PAUSE_BETWEEN_TRIALS_S}s between trials", flush=True)
            time.sleep(PAUSE_BETWEEN_TRIALS_S)
        trials.append(run_trial(n))

    table = build_table(trials)
    print("\n" + table)

    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    base = config.RESULTS_DIR / f"capstone_{args.label}"
    base.with_suffix(".json").write_text(json.dumps(trials, indent=2, ensure_ascii=False), encoding="utf-8")
    base.with_suffix(".md").write_text(
        f"# Capstone run log — {args.label} ({stamp})\n\n{table}\n", encoding="utf-8")
    print(f"\nSaved {base}.md and {base}.json")


if __name__ == "__main__":
    main()

