"""Runs inside the task container (stdlib only). Drives one Lemonade Stand chat
for one Harbor trial and writes, under --log-dir:

  stream.jsonl     every server-sent event frame from POST /api/chat
  final_reply.md   the assistant's reply text (the trial's report)
  usage.json       token and cost totals (contract with Person E, see README)

API facts below were checked on lemonade-stand 1.0.0-rc.57 (commit 92ae62f)
and tested end to end in fake-model mode on Oct 27.

  GET  /api/health                  public liveness probe
  POST /api/chat                    {"text", "conversation_id": null, "model", "effort"}
                                    -> SSE frames: meta, delta, retract, tool_start,
                                       tool, budget, downgrade, escalate, done, error
  POST /api/halt                    {"on": true} blocks every new paid call
  auth: header  X-Stand: <home>/secrets/api-token   (and no Origin header)
  usage: <home>/stand.db, table spend_events (kind='settle' rows)
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


def model_label(server_dir: Path, model: str) -> str:
    """Map a Harbor model id (e.g. 'anthropic/claude-sonnet-5') to Lemonade
    Stand's roster label (e.g. 'Sonnet 5')."""
    if not model:
        raise SystemExit("No model given (-m). Lemonade Stand would pick its own; refusing.")
    bare = model.split("/", 1)[-1]
    sys.path.insert(0, str(server_dir))
    try:
        import providers  # stdlib-only module in the server folder

        for candidate in (model, bare):
            if candidate in providers.ROSTER:
                return candidate
            if candidate in providers.BY_MODEL:
                return providers.BY_MODEL[candidate][0]
    except Exception as exc:  # noqa: BLE001
        print(f"model lookup failed: {exc}", file=sys.stderr)
    finally:
        sys.path.pop(0)
    # Never fall back to "auto": Lemonade Stand would route to a model of its
    # choosing and the trial would no longer be matched to the other agents.
    # An explicit label also stops rc.57 from switching to a cheaper model
    # when a call is refused for cost (chat.py: fixed_model).
    raise SystemExit(
        f"{model} is not in Lemonade Stand's model roster (app/config/ceilings.json "
        "models.roster); pass a roster label such as 'Sonnet 5'."
    )


def wait_healthy(base: str, deadline: float) -> dict:
    last = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(base + "/api/health", timeout=3) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1)
    raise SystemExit(f"Lemonade Stand server never became healthy: {last}")


def post_json(base, token, path, body, timeout=10):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode(),
        headers={"X-Stand": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def ledger_tokens(db_path: Path) -> int:
    """Settled tokens so far: uncached input + cache reads + cache writes +
    output. rc.57 stores tokens_in without the cached part (providers.py,
    provider_responses.py), so the cache columns are added back."""
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        try:
            (n,) = con.execute(
                "SELECT COALESCE(SUM(COALESCE(tokens_in,0)+COALESCE(cache_read,0)"
                "+COALESCE(cache_write,0)+COALESCE(tokens_out,0)),0) "
                "FROM spend_events WHERE kind='settle'"
            ).fetchone()
        finally:
            con.close()
        return int(n)
    except sqlite3.Error:
        return 0


class TokenCap(threading.Thread):
    """Polls the ledger; once settled tokens reach the cap, halts all new paid
    calls. The call in flight finishes and the turn closes out, so the trial
    ends with whatever the bots have written."""

    def __init__(self, base, token, db_path, cap, every=5.0):
        super().__init__(daemon=True)
        self.base, self.token, self.db, self.cap, self.every = base, token, db_path, cap, every
        self.hit = threading.Event()
        self.stopping = threading.Event()
        self.at_tokens = None

    def run(self):
        while not self.stopping.wait(self.every):
            used = ledger_tokens(self.db)
            if used >= self.cap:
                self.at_tokens = used
                try:
                    post_json(self.base, self.token, "/api/halt", {"on": True})
                except Exception as exc:  # noqa: BLE001
                    print(f"halt failed: {exc}", file=sys.stderr)
                self.hit.set()
                return


def stream_chat(base, token, body, timeout, out_path):
    req = urllib.request.Request(
        base + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"X-Stand": token, "Content-Type": "application/json"},
        method="POST",
    )
    text, frames, status = "", [], "running"
    deadline = time.time() + timeout
    with urllib.request.urlopen(req, timeout=timeout) as resp, out_path.open("w") as out:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            try:
                frame = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                continue
            out.write(json.dumps(frame) + "\n")
            out.flush()
            frames.append(frame)
            kind = frame.get("type")
            if kind == "delta":
                text += frame.get("text") or ""
            elif kind == "retract":
                # server takes back an unfinished tail before rewriting it
                tail = frame.get("text") or ""
                if tail and text.endswith(tail):
                    text = text[: -len(tail)]
            elif kind == "done":
                # rc.57 reports a failed model call inside the done frame
                # (chat.py: meta["error"] = {"code", "message"}), not as a
                # separate error frame.
                if frame.get("error"):
                    status = "provider_error"
                elif status not in ("error", "provider_error"):
                    status = "done"  # group chats send one per speaker; keep reading
            elif kind == "error":
                status = "error"
            if time.time() > deadline:
                status = "timeout"
                break  # leaving the with-block closes the socket, which cancels the turn
    if status == "running":
        status = "done"  # stream closed normally without an explicit frame
    return text, frames, status


def usage_from_ledger(db_path: Path) -> dict:
    """Sum settled spend. The home is fresh per trial, so every row is ours."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT model, agent_id, COALESCE(tokens_in,0), COALESCE(cache_read,0), "
        "COALESCE(cache_write,0), COALESCE(tokens_out,0), COALESCE(usd,0) "
        "FROM spend_events WHERE kind='settle'"
    ).fetchall()
    con.close()
    per_model, bots = {}, {}
    for model, agent, tin, cread, cwrite, tout, usd in rows:
        u = per_model.setdefault(
            model, {"n_input_tokens": 0, "n_output_tokens": 0, "n_cache_tokens": 0, "cost_usd": 0.0}
        )
        # rc.57's tokens_in excludes cached input for both providers
        # (Anthropic reports it separately; the OpenAI path subtracts it).
        # Harbor's n_input_tokens includes cache, so add reads and writes back.
        u["n_input_tokens"] += int(tin) + int(cread) + int(cwrite)
        u["n_cache_tokens"] += int(cread)
        u["n_output_tokens"] += int(tout)
        u["cost_usd"] += float(usd)
        key = agent or "default"
        bots[key] = round(bots.get(key, 0.0) + float(usd), 6)
    total = {k: sum(u[k] for u in per_model.values()) for k in
             ("n_input_tokens", "n_output_tokens", "n_cache_tokens", "cost_usd")}
    return {**total, "per_model": per_model, "bots": bots, "n_calls": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--home", required=True, help="LEMONADE_STAND_HOME")
    ap.add_argument("--server-dir", required=True)
    ap.add_argument("--instruction-file", required=True)
    ap.add_argument("--timeout", type=int, default=3300)
    ap.add_argument("--log-dir", default="/logs/agent")
    ap.add_argument("--model", default="")
    ap.add_argument("--effort", default="auto")
    ap.add_argument("--max-tokens", type=int, default=5_000_000, help="0 = no cap")
    ap.add_argument("--fake", action="store_true", help="server runs in fake-model mode")
    a = ap.parse_args()

    log, home = Path(a.log_dir), Path(a.home)
    log.mkdir(parents=True, exist_ok=True)
    start = time.time()
    health = wait_healthy(a.base_url, start + 60)
    token = (home / "secrets" / "api-token").read_text().strip()
    label = model_label(Path(a.server_dir), a.model)

    cap = None
    if a.max_tokens > 0:
        cap = TokenCap(a.base_url, token, home / "stand.db", a.max_tokens)
        cap.start()

    body = {
        "text": Path(a.instruction_file).read_text(),
        "conversation_id": None,
        "model": label,
        "effort": a.effort,
    }
    try:
        reply, frames, status = stream_chat(
            a.base_url, token, body, a.timeout - (time.time() - start), log / "stream.jsonl"
        )
    except urllib.error.HTTPError as exc:
        reply, frames, status = "", [], f"http_{exc.code}: {exc.read()[:300]!r}"
    except TimeoutError:
        reply, frames, status = "", [], "timeout"
    finally:
        if cap:
            cap.stopping.set()
    capped = bool(cap and cap.hit.is_set())
    if capped:
        status = "token_cap"
    refused = [f for f in frames if f.get("type") == "budget" and f.get("phase") == "refused"]
    if refused and status == "done":
        status = "spend_limit"  # the app's daily USD limit refused a call
    (log / "final_reply.md").write_text(reply)

    try:
        usage = usage_from_ledger(home / "stand.db")
    except sqlite3.Error as exc:
        usage = {"error": f"ledger read failed: {exc}"}
    meta = next((f for f in frames if f.get("type") == "meta"), {})
    models_seen = sorted({f["model"] for f in frames
                          if f.get("type") in ("meta", "done") and f.get("model")})
    usage.update(
        final_status=status,
        capped=capped,
        capped_at_tokens=cap.at_tokens if capped else None,
        max_tokens=a.max_tokens,
        wall_sec=round(time.time() - start, 1),
        conversation_id=meta.get("conversation_id"),
        model_label=label,
        model_used=meta.get("model"),
        models_seen=models_seen,
        n_downgrades=sum(1 for f in frames if f.get("type") == "downgrade"),
        n_escalations=sum(1 for f in frames if f.get("type") == "escalate"),
        n_spend_refusals=len(refused),
        server_version=health.get("version"),
        n_tool_calls=sum(1 for f in frames if f.get("type") == "tool_start"),
        fake=a.fake,
        provider_errors=[f["error"] for f in frames
                         if f.get("type") in ("done", "error") and f.get("error")],
    )
    (log / "usage.json").write_text(json.dumps(usage, indent=2))
    print(json.dumps({"status": status, "cost_usd": usage.get("cost_usd"),
                      "version": health.get("version")}))
    # A trial whose model was never reached is a setup failure, not a score of
    # 0: exit non-zero so Harbor records an exception.
    failed = status in ("error", "provider_error") or status.startswith("http_")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
