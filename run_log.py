"""
Capstone: structured run log.

Every agent run adds one line to logs/runs.jsonl. Each line is a JSON record
with named fields, so a run can be looked up later without adding new code.

    python run_log.py        prints the last 10 records
"""

import json
import time
from datetime import datetime, timezone

import config

LOG_FILE = config.ROOT / "logs" / "runs.jsonl"


class StepTimer:
    """Records how long each step of one run takes, in seconds."""

    def __init__(self):
        self.steps = {}
        self._start = None

    def start(self):
        self._start = time.perf_counter()

    def stop(self, name: str):
        self.steps[name] = round(time.perf_counter() - self._start, 3)


def write_record(session: dict, duration: float, steps: dict,
                 tokens: dict, model_calls: int, crash: str | None = None) -> dict:
    """Build one log record from a finished session and append it to the file."""
    item = session.get("selected_item") or {}

    if crash:
        outcome = "crashed"
    elif session.get("error"):
        outcome = "stopped_early"
    elif session.get("warning"):
        outcome = "partial"
    else:
        outcome = "complete"

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": session.get("query"),
        "wardrobe_items": len((session.get("wardrobe") or {}).get("items", [])),
        "outcome": outcome,
        "selected_item": item.get("id"),
        "has_outfit": bool(session.get("outfit_suggestion")),
        "has_fit_card": bool(session.get("fit_card")),
        "error": session.get("error") or crash,
        "warning": session.get("warning"),
        "duration_s": round(duration, 3),
        "step_s": steps,
        "model_calls": model_calls,
        "prompt_tokens": tokens["prompt"],
        "output_tokens": tokens["output"],
        "model": config.MODEL,
        "timeout_s": config.MODEL_TIMEOUT_SECONDS,
    }

    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_records(last: int = 10) -> list[dict]:
    """Return the most recent records, oldest first."""
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-last:] if line.strip()]


if __name__ == "__main__":
    for record in read_records():
        print(json.dumps(record, ensure_ascii=False))

