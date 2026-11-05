"""Turn a Harbor job directory into the trial table defined in scoring/schema/trial-table.md.

One row per trial. Reads only retained job exports; nothing here runs inside a session.

    python scoring/src/build_trial_table.py JOBS_DIR TASKS_DIR -o out.csv

JOBS_DIR   a single job directory, or a parent holding several of them
TASKS_DIR  replicationbench-release/src/dataset/tasks
"""

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path

ROW_FIELDS = [
    "job_id", "job_dir", "trial_name", "paper_id", "task_id", "task_checksum",
    "agent", "agent_version", "model", "status", "reward", "passed",
    "reported_value", "expected_value", "tolerance", "value_kind", "n_elements",
    "normalized_error", "normalized_error_vector",
    "wall_time_sec", "agent_exec_sec", "verifier_sec",
    "n_input_tokens", "n_cache_tokens", "n_output_tokens", "n_total_tokens",
    "cost_usd", "token_cap", "capped_tokens", "capped_time", "capped", "passed_within_cap",
    "confidence", "notes",
]

TOKEN_CAP = 5_000_000
TIMEOUT_EXCEPTIONS = {"AgentTimeoutError"}

TASK_NAME_RE = re.compile(r"replicationbench__(?P<paper>[^_].*?)__(?P<task>.+)$")


# --- task definitions -------------------------------------------------------

def load_task_defs(tasks_dir):
    """paper_id__task_id -> ReplicationBench task definition."""
    defs = {}
    for path in Path(tasks_dir).glob("*/*.json"):
        paper = path.parent.name
        with open(path) as fh:
            defs[f"{paper}__{path.stem}"] = json.load(fh)
    return defs


def split_task_name(task_name):
    """'replicationbench/replicationbench__gw_cosmo__dark_energy' -> ('gw_cosmo', 'dark_energy').

    Task ids themselves contain '__', so split on the first separator only.
    """
    match = TASK_NAME_RE.search(task_name or "")
    if not match:
        return None, None
    return match.group("paper"), match.group("task")


# --- reported value ---------------------------------------------------------

_DECODER = json.JSONDecoder()


def _value_from_json_text(text):
    """Last JSON object in text that carries a 'value' key."""
    for start in reversed([m.start() for m in re.finditer(r"\{", text)]):
        try:
            obj, _ = _DECODER.raw_decode(text, start)
        except ValueError:
            continue
        if isinstance(obj, dict) and "value" in obj:
            return obj["value"]
    return None


def read_reported_value(trial_dir):
    """(value, note). Artifact copy of /app/result.json first, agent stdout second.

    See 'Reported value' in the schema: the verifier stdout is not a source, the
    adapter runs pytest without -v/-s so it never prints the number.
    """
    for path in sorted(trial_dir.glob("artifacts/**/result.json")):
        try:
            with open(path) as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue
        if isinstance(obj, dict) and "value" in obj:
            return obj["value"], "value_from=artifact"

    for path in sorted((trial_dir / "agent").glob("*.txt")):
        try:
            value = _value_from_json_text(path.read_text(errors="replace"))
        except OSError:
            continue
        if value is not None:
            return value, f"value_from=agent/{path.name}"

    return None, "value_missing"


_NUMBER_RE = re.compile(r"(?<![\w.])(\d*\.?\d+)\s*(%?)")
_SCALE_RE = re.compile(r"\(?\s*(?:a number\s+)?(?:from\s+|between\s+)?0\s*(?:to|-|–|and)\s*1\s*\)?", re.I)


def _confidence_from_markdown(text):
    """Confidence from the report request's Markdown (harbor/report-request.md, item 3).

    Takes the first number on the line that names confidence, or on the next non-empty
    line when the heading stands alone. A percentage is divided by 100. Values outside
    0 to 1 are rejected rather than clipped.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "confidence" not in line.lower():
            continue
        after = line[line.lower().index("confidence") + len("confidence"):]
        candidates = [after] + [l for l in lines[i + 1:i + 3] if l.strip()][:1]
        for chunk in candidates:
            match = _NUMBER_RE.search(_SCALE_RE.sub(" ", chunk))
            if not match:
                continue
            value = float(match.group(1))
            if match.group(2) == "%":
                value /= 100
            return (value, None) if 0 <= value <= 1 else (None, "confidence_out_of_range")
        return None, "confidence_not_numeric"
    return None, "confidence_missing"


def read_confidence(trial_dir):
    """Stated confidence from the trial's end-of-run report.

    The report request asks every agent for /app/report.md, collected as an artifact.
    A report.json with a confidence key is also accepted.
    """
    for path in sorted(trial_dir.glob("artifacts/**/report.json")):
        try:
            with open(path) as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue
        for key in ("confidence", "stated_confidence"):
            if isinstance(obj, dict) and key in obj:
                return obj[key], None
    for path in sorted(trial_dir.glob("artifacts/**/report.md")):
        try:
            return _confidence_from_markdown(path.read_text(errors="replace"))
        except OSError:
            continue
    return None, "report_missing"


def apply_caps(usage, exception_type, passed, token_cap=TOKEN_CAP):
    """Study caps, applied identically to every agent after the run.

    A trial over the token cap is capped and cannot pass within the cap, whatever its
    reward. A trial stopped by Harbor's agent time limit is capped as well. Both stay
    rows in the table: capped is not the same as failed (trial protocol).
    """
    total = usage.get("n_total_tokens")
    capped_tokens = None if total is None else total > token_cap
    capped_time = exception_type in TIMEOUT_EXCEPTIONS
    capped = capped_time or bool(capped_tokens)
    if passed is None:
        within = None
    elif not passed or capped:
        within = False
    elif capped_tokens is None:
        within = None
    else:
        within = True
    return {
        "token_cap": token_cap,
        "capped_tokens": capped_tokens,
        "capped_time": capped_time,
        "capped": capped,
        "passed_within_cap": within,
    }


# --- normalized error -------------------------------------------------------

def _as_list(value):
    return list(value) if isinstance(value, (list, tuple)) else [value]


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _flatten_errors(reported, expected, tolerance, path=""):
    """Walk reported/expected/tolerance together, yielding one ratio per leaf.

    Answers are not always flat: some tasks return a dict keyed by quantity name, some a
    list of [value, uncertainty] pairs. The tolerance mirrors the answer's structure
    exactly, so the three are walked in step. Raises ValueError when the shapes disagree.
    """
    here = path or "root"

    if isinstance(expected, dict):
        if not isinstance(reported, dict):
            raise ValueError(f"shape_mismatch at {here}: expected dict")
        if not isinstance(tolerance, dict):
            raise ValueError(f"tolerance_shape_mismatch at {here}: expected dict")
        missing = set(expected) - set(reported)
        if missing:
            raise ValueError(f"missing_keys at {here}: {sorted(missing)[:3]}")
        for key in expected:
            if key not in tolerance:
                raise ValueError(f"tolerance_missing_key at {here}.{key}")
            yield from _flatten_errors(reported[key], expected[key], tolerance[key], f"{path}.{key}")
        return

    if isinstance(expected, (list, tuple)):
        if not isinstance(reported, (list, tuple)):
            raise ValueError(f"shape_mismatch at {here}: expected list")
        if len(reported) != len(expected):
            raise ValueError(f"length_mismatch at {here}: {len(reported)} vs {len(expected)}")
        # A scalar tolerance applies to every element of the list.
        if isinstance(tolerance, (list, tuple)):
            if len(tolerance) != len(expected):
                raise ValueError(f"tolerance_length_mismatch at {here}: {len(tolerance)} vs {len(expected)}")
            tolerances = tolerance
        else:
            tolerances = [tolerance] * len(expected)
        for i, (r, e, t) in enumerate(zip(reported, expected, tolerances)):
            yield from _flatten_errors(r, e, t, f"{path}[{i}]")
        return

    if not (_numeric(reported) and _numeric(expected) and _numeric(tolerance)):
        raise ValueError(f"non_numeric at {here}")

    difference = abs(reported - expected)
    if tolerance == 0:
        # Exact match required. 0 if it matches, infinite otherwise.
        yield 0.0 if difference == 0 else float("inf")
        return
    yield difference / tolerance


def normalized_error(reported, expected, tolerance):
    """(scalar, vector, note). Absolute difference over tolerance, per leaf; max summary.

    The maximum is the summary so that normalized_error <= 1 is the same statement as
    'every element within tolerance', which is what the verifier tests. A leaf whose
    tolerance is 0 requires an exact match and contributes inf when it misses.
    """
    if reported is None:
        return None, None, "value_missing"
    if expected is None or tolerance is None:
        return None, None, "no_expected_or_tolerance"

    try:
        vector = list(_flatten_errors(reported, expected, tolerance))
    except ValueError as exc:
        return None, None, str(exc)

    if not vector:
        return None, None, "no_leaves"
    return max(vector), vector, None


def count_leaves(value):
    """Number of numeric leaves in an expected answer."""
    if isinstance(value, dict):
        return sum(count_leaves(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return sum(count_leaves(v) for v in value)
    return 1


# --- timings and usage ------------------------------------------------------

def _parse_ts(text):
    if not text:
        return None
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _span(block):
    if not isinstance(block, dict):
        return None
    start, finish = _parse_ts(block.get("started_at")), _parse_ts(block.get("finished_at"))
    if start is None or finish is None:
        return None
    return round((finish - start).total_seconds(), 3)


def read_usage(agent_result):
    """Tokens and cost. Harbor normalizes installed agents into agent_result; fall back
    to model_usage for agents that only report per model totals.

    Harbor's n_input_tokens already includes cached tokens, so the total is input plus
    output; n_cache_tokens is the cached share of the input, not a third addend.
    """
    agent_result = agent_result or {}
    usage = {
        "n_input_tokens": agent_result.get("n_input_tokens"),
        "n_cache_tokens": agent_result.get("n_cache_tokens"),
        "n_output_tokens": agent_result.get("n_output_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
    }

    model_usage = agent_result.get("model_usage")
    if isinstance(model_usage, dict) and any(v is None for v in usage.values()):
        per_model = [v for v in model_usage.values() if isinstance(v, dict)]
        for key, aliases in (
            ("n_input_tokens", ("n_input_tokens", "input_tokens", "prompt_tokens")),
            ("n_cache_tokens", ("n_cache_tokens", "cache_read_input_tokens")),
            ("n_output_tokens", ("n_output_tokens", "output_tokens", "completion_tokens")),
            ("cost_usd", ("cost_usd", "cost")),
        ):
            if usage[key] is not None:
                continue
            found = [m[a] for m in per_model for a in aliases if m.get(a) is not None]
            if found:
                usage[key] = sum(found)

    counts = [usage[k] for k in ("n_input_tokens", "n_output_tokens")]
    present = [c for c in counts if c is not None]
    usage["n_total_tokens"] = sum(present) if present else None
    return usage


# --- rows -------------------------------------------------------------------

def _json_cell(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value)
    return value


def build_row(trial_dir, task_defs, token_cap=TOKEN_CAP):
    with open(trial_dir / "result.json") as fh:
        result = json.load(fh)

    notes = []
    config = result.get("config") or {}
    agent_info = result.get("agent_info") or {}
    paper_id, task_id = split_task_name(result.get("task_name"))

    verifier_result = result.get("verifier_result") or {}
    rewards = verifier_result.get("rewards") or {}
    reward = rewards.get("reward")

    exception_type = (result.get("exception_info") or {}).get("exception_type")
    if exception_type in TIMEOUT_EXCEPTIONS:
        status = "capped"
        notes.append("agent_time_limit")
    elif result.get("exception_info") or (trial_dir / "exception.txt").exists():
        status = "exception"
        notes.append("trial_raised_exception")
    elif reward is None:
        status = "no_verifier"
        notes.append("no_reward")
    else:
        status = "ok"

    reported, value_note = read_reported_value(trial_dir)
    if value_note:
        notes.append(value_note)

    task_def = task_defs.get(f"{paper_id}__{task_id}")
    if task_def is None:
        notes.append("no_task_definition")
        expected = tolerance = None
        error = vector = None
    else:
        expected, tolerance = task_def.get("expected_output"), task_def.get("tolerance")
        error, vector, error_note = normalized_error(reported, expected, tolerance)
        if error_note and error_note != value_note:
            notes.append(error_note)

    model_info = agent_info.get("model_info")
    agent_config = config.get("agent") or {}
    model = model_info if isinstance(model_info, str) else None
    if model is None and isinstance(model_info, dict):
        model = model_info.get("name") or model_info.get("model_name")
    model = model or agent_config.get("model_name")

    usage = read_usage(result.get("agent_result"))
    passed = None if reward is None else (reward == 1)
    caps = apply_caps(usage, exception_type, passed, token_cap)
    if caps["capped_tokens"]:
        notes.append("over_token_cap")
    confidence, confidence_note = read_confidence(trial_dir)
    if confidence_note and agent_info.get("name") != "oracle":
        notes.append(confidence_note)

    whole = {"started_at": result.get("started_at"), "finished_at": result.get("finished_at")}
    n_elements = count_leaves(expected) if expected is not None else None

    return {
        "job_id": config.get("job_id") or result.get("job_id"),
        "job_dir": trial_dir.parent.name,
        "trial_name": result.get("trial_name") or trial_dir.name,
        "paper_id": paper_id,
        "task_id": task_id,
        "task_checksum": result.get("task_checksum"),
        "agent": agent_info.get("name"),
        "agent_version": agent_info.get("version"),
        "model": model,
        "status": status,
        "reward": reward,
        "passed": passed,
        "reported_value": _json_cell(reported),
        "expected_value": _json_cell(expected),
        "tolerance": _json_cell(tolerance),
        "value_kind": None if expected is None else (
            "scalar" if not isinstance(expected, (list, tuple, dict))
            else "dict" if isinstance(expected, dict) else "list"),
        "n_elements": n_elements,
        "normalized_error": None if error is None else round(error, 6),
        "normalized_error_vector": _json_cell(None if vector is None else [round(v, 6) for v in vector]),
        "wall_time_sec": _span(whole),
        "agent_exec_sec": _span(result.get("agent_execution")),
        "verifier_sec": _span(result.get("verifier")),
        "confidence": confidence,
        "notes": "; ".join(notes),
        **usage,
        **caps,
    }


def find_trial_dirs(jobs_dir):
    """Trial directories under one job directory, or under a parent of several jobs.

    A job directory holds a result.json of its own next to the trial directories, so a
    directory counts as a trial only if its result.json carries a task_name.
    """
    jobs_dir = Path(jobs_dir)
    found = []
    for path in sorted(jobs_dir.glob("result.json")) + sorted(jobs_dir.glob("*/result.json")) \
            + sorted(jobs_dir.glob("*/*/result.json")):
        try:
            with open(path) as fh:
                if json.load(fh).get("task_name"):
                    found.append(path.parent)
        except (OSError, ValueError):
            continue
    return found


def build_table(jobs_dir, tasks_dir, token_cap=TOKEN_CAP):
    task_defs = load_task_defs(tasks_dir)
    if not task_defs:
        raise SystemExit(f"no task definitions under {tasks_dir}")
    rows = []
    for trial_dir in find_trial_dirs(jobs_dir):
        try:
            rows.append(build_row(trial_dir, task_defs, token_cap))
        except (OSError, ValueError) as exc:
            rows.append({
                "job_dir": trial_dir.parent.name,
                "trial_name": trial_dir.name,
                "status": "unreadable",
                "notes": f"{type(exc).__name__}: {exc}",
            })
    return rows


def write_csv(rows, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in ROW_FIELDS})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs_dir", help="a Harbor job directory, or a parent of several")
    parser.add_argument("tasks_dir", help="replicationbench-release/src/dataset/tasks")
    parser.add_argument("-o", "--out", default="scoring/out/trial-table.csv")
    parser.add_argument("--token-cap", type=int, default=TOKEN_CAP,
                        help="per-trial token cap applied to every agent (default 5,000,000)")
    args = parser.parse_args()

    rows = build_table(args.jobs_dir, args.tasks_dir, args.token_cap)
    write_csv(rows, args.out)

    ok = sum(1 for r in rows if r.get("status") == "ok")
    scored = sum(1 for r in rows if r.get("normalized_error") is not None)
    print(f"{len(rows)} trials -> {args.out}")
    print(f"  status ok           {ok}")
    print(f"  passed              {sum(1 for r in rows if r.get('passed'))}")
    print(f"  normalized_error    {scored}")
    print(f"  tokens or cost      {sum(1 for r in rows if r.get('n_total_tokens') or r.get('cost_usd'))}")
    print(f"  passed within cap   {sum(1 for r in rows if r.get('passed_within_cap'))}")
    print(f"  capped              {sum(1 for r in rows if r.get('capped'))}")
    print(f"  confidence          {sum(1 for r in rows if r.get('confidence') is not None)}")


if __name__ == "__main__":
    main()
