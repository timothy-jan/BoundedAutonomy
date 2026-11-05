#!/usr/bin/env bash
# Go/no-go probe for a Lemonade Stand checkout (run it on rc.57 / 92ae62f).
#
#   ./probe_headless.sh /path/to/lemonade-stand
#
# Answers the two questions that decide the integration:
#   1. Does the backend start headless on Linux? (1 CPU, 4 GB, no display,
#      fake-model mode, so no API keys or spend)
#   2. Can its bots run code? rc.29 says in its own tool list that it has
#      "no code runner, terminal or sandbox".
# Uses Docker if available, otherwise runs on this machine.
set -uo pipefail

SRC=$(cd "${1:?path to Lemonade Stand checkout}" && pwd)
PORT=${PORT:-8279}
LOG="$(cd "$(dirname "$0")" && pwd)/probe-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

echo "version: $(cat "$SRC/VERSION" 2>/dev/null)   (frozen: 1.0.0-rc.57)"
echo "commit:  $(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo 'no git metadata')   (frozen: 92ae62f)"

echo; echo "== 1. code execution tools =="
python3 - "$SRC/app/config/tools.json" <<'PY'
import json, re, sys
tools = json.load(open(sys.argv[1]))
tools = tools.get("tools", tools) if isinstance(tools, dict) else {t["name"]: t for t in tools}
pat = re.compile(r"\b(shell|bash|terminal|exec|execute|run_code|run_python|python|sandbox|code runner)\b", re.I)
# Match tool names, plus descriptions that offer execution (not ones that rule it out).
offers = re.compile(r"\b(runs?|executes?) (python|code|commands?|scripts?)\b|\bshell access\b", re.I)
hits = [n for n, t in tools.items() if pat.search(n) or offers.search(t.get("description", ""))]
denial = [n for n, t in tools.items() if "no code runner" in t.get("description", "")]
print(f"{len(tools)} tools")
print("possible code-execution tools:", hits or "none")
if denial: print("tool list states there is no code runner (in:", ", ".join(denial) + ")")
print("RESULT_TOOLS=" + ("HAS_EXEC_CANDIDATE" if hits else "NO_EXEC"))
PY

echo; echo "== 2. headless start =="
# args: <source dir> <scratch dir> <port>
run='src=$1 w=$2 port=$3
  cp -r "$src" "$w/ls" && cd "$w/ls/app/server" || exit 2
  export LEMONADE_STAND_HOME="$w/home" LEMONADE_STAND_FAKE=1; unset DISPLAY
  python3 stand.py --port "$port" > "$w/server.log" 2>&1 & pid=$!
  for i in $(seq 1 30); do
    if python3 -c "import urllib.request as u,sys; print(u.urlopen(\"http://127.0.0.1:$port/api/health\",timeout=2).read().decode())" 2>/dev/null; then
      echo "healthy after ~${i}s"; kill $pid; echo RESULT_HEADLESS=GO; exit 0; fi; sleep 1; done
  tail -40 "$w/server.log"; kill $pid 2>/dev/null; echo RESULT_HEADLESS=NO-GO; exit 3'
if docker info >/dev/null 2>&1; then
  docker run --rm --cpus 1 --memory 4g -v "$SRC":/src:ro python:3.11-slim \
    bash -c "$run" _ /src /tmp "$PORT"
else
  echo "(docker not available: running on this machine)"
  tmp=$(mktemp -d); bash -c "$run" _ "$SRC" "$tmp" "$PORT"; rm -rf "$tmp"
fi
echo "log: $LOG"
