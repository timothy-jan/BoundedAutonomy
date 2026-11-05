import importlib.util
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

DRIVER = Path(__file__).resolve().parents[1] / "agents" / "lemonade-stand" / "ls_driver.py"
spec = importlib.util.spec_from_file_location("ls_driver", DRIVER)
ls_driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls_driver)


def sse(frame):
    return f"data: {json.dumps(frame)}\n\n".encode()


def serve(script):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            script(self)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def start_stream(handler):
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream")
    handler.end_headers()


@pytest.fixture
def run_chat(tmp_path):
    servers = []

    def run(script, timeout=5):
        server, base = serve(script)
        servers.append(server)
        return ls_driver.stream_chat(base, "tok", {"text": "hi"}, timeout, tmp_path / "s.jsonl")

    yield run
    for server in servers:
        server.shutdown()


def test_normal_stream_collects_text(run_chat):
    def script(h):
        start_stream(h)
        h.wfile.write(sse({"type": "meta", "model": "Sonnet 5"}))
        h.wfile.write(sse({"type": "delta", "text": "hello "}))
        h.wfile.write(sse({"type": "delta", "text": "world"}))
        h.wfile.write(sse({"type": "done"}))

    text, frames, status = run_chat(script)
    assert (text, status, len(frames)) == ("hello world", "done", 4)


def test_retract_removes_tail(run_chat):
    def script(h):
        start_stream(h)
        h.wfile.write(sse({"type": "delta", "text": "abc draft"}))
        h.wfile.write(sse({"type": "retract", "text": " draft"}))
        h.wfile.write(sse({"type": "delta", "text": " final"}))
        h.wfile.write(sse({"type": "done"}))

    assert run_chat(script)[0] == "abc final"


def test_error_in_done_frame_is_provider_error(run_chat):
    def script(h):
        start_stream(h)
        h.wfile.write(sse({"type": "done", "error": {"code": "x", "message": "y"}}))

    assert run_chat(script)[2] == "provider_error"


def test_deadline_holds_when_server_only_sends_keepalives(run_chat):
    def script(h):
        start_stream(h)
        h.wfile.write(sse({"type": "delta", "text": "partial"}))
        h.wfile.flush()
        for _ in range(40):
            h.wfile.write(b": keepalive\n\n")
            h.wfile.flush()
            time.sleep(0.1)

    began = time.time()
    text, _, status = run_chat(script, timeout=1)
    assert status == "timeout"
    assert text == "partial"
    assert time.time() - began < 3


def test_deadline_holds_when_server_goes_silent(run_chat):
    def script(h):
        start_stream(h)
        h.wfile.flush()
        time.sleep(4)

    began = time.time()
    status = run_chat(script, timeout=1)[2]
    assert status == "timeout"
    assert time.time() - began < 3


def test_http_error_status_is_reported(run_chat):
    def script(h):
        h.send_response(403)
        h.end_headers()
        h.wfile.write(b"forbidden")

    assert run_chat(script)[2].startswith("http_403")


def make_ledger(path, rows):
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE spend_events (kind TEXT, model TEXT, agent_id TEXT, tokens_in INT, "
        "cache_read INT, cache_write INT, tokens_out INT, usd REAL)"
    )
    con.executemany("INSERT INTO spend_events VALUES (?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()


def test_usage_adds_cache_back_into_input(tmp_path):
    db = tmp_path / "stand.db"
    make_ledger(db, [
        ("settle", "Sonnet 5", "bot-1", 100, 50, 10, 20, 0.5),
        ("settle", "Sonnet 5", "bot-2", 10, 0, 0, 5, 0.1),
        ("reserve", "Sonnet 5", "bot-1", 999, 999, 999, 999, 9.9),
    ])
    usage = ls_driver.usage_from_ledger(db)
    assert usage["n_input_tokens"] == 170
    assert usage["n_cache_tokens"] == 50
    assert usage["n_output_tokens"] == 25
    assert usage["cost_usd"] == pytest.approx(0.6)
    assert usage["n_calls"] == 2
    assert usage["bots"] == {"bot-1": 0.5, "bot-2": 0.1}


def test_usage_null_model_gets_a_string_key(tmp_path):
    db = tmp_path / "stand.db"
    make_ledger(db, [("settle", None, None, 1, 0, 0, 1, 0.0)])
    usage = ls_driver.usage_from_ledger(db)
    assert list(usage["per_model"]) == ["unknown"]
    assert usage["bots"] == {"default": 0.0}
