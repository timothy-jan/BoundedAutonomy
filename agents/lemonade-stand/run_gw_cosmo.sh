#!/usr/bin/env bash
# One gw_cosmo task on each model with Lemonade Stand rc.57 as a Harbor agent.
#
#   agents/lemonade-stand/run_gw_cosmo.sh <task dir> <lemonade-stand checkout> <model> [<model> ...]
#
# Example (from the repo root):
#   agents/lemonade-stand/run_gw_cosmo.sh \
#     datasets/batch_04/gw_cosmo__h0_scaling ~/lemonade-stand \
#     anthropic/claude-sonnet-5 openai/gpt-5
#
# Smoke test first, free (fake model, no keys):  FAKE=1 run_gw_cosmo.sh <task> <checkout> anthropic/claude-sonnet-5
# Provider keys come from your shell: ANTHROPIC_API_KEY, OPENAI_API_KEY,
# XAI_API_KEY, GOOGLE_AI_API_KEY (or GEMINI_API_KEY).
set -euo pipefail

TASK=${1:?task dir, e.g. datasets/batch_04/gw_cosmo__h0_scaling}
SRC=$(cd "${2:?Lemonade Stand checkout at 92ae62f}" && pwd)
shift 2
[ $# -ge 1 ] || { echo "give at least one model" >&2; exit 2; }
HERE=$(cd "$(dirname "$0")" && pwd)

version=$(cat "$SRC/VERSION" 2>/dev/null || echo missing)
commit=$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo "no git metadata")
echo "Lemonade Stand $version ($commit); frozen: 1.0.0-rc.57 (92ae62f)"
[ "$version" = "1.0.0-rc.57" ] || { echo "Not the frozen version; stopping." >&2; exit 1; }

extra=()
if [ "${FAKE:-0}" = 1 ]; then extra+=(--ak fake=true); echo "FAKE=1: fake model, no spend, results do not count"; fi

for model in "$@"; do
  echo "=== $model ==="
  PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}" harbor run \
    -p "$TASK" \
    -a lemonade_stand_agent:LemonadeStandAgent \
    -m "$model" \
    --artifact /app/result.json \
    --ae LS_SOURCE_DIR="$SRC" \
    --ak daily_usd_limit="${DAILY_USD_LIMIT:-100}" \
    --ak max_tokens="${MAX_TOKENS:-0}" \
    ${extra[@]+"${extra[@]}"} \
    -o "${JOBS_DIR:-jobs}"
done

echo
echo "Per trial, see <jobs dir>/<job>/<trial>/agent/usage.json and result.json."
