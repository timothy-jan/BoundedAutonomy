# mini-SWE-agent

| Field | Value |
|---|---|
| Harbor agent name | `mini-swe-agent` |
| Version | 2.4.6 (`kwargs: {version: "2.4.6"}`), installed with `uv tool install mini-swe-agent==2.4.6` on Python 3.12 inside the container |
| Models | A and B |
| Tools | Bash only, through mini-swe-agent's built-in `mini.yaml` config |
| Settings changed from default | Version pinned. Everything else is Harbor's default: `--yolo` (no confirmation), `--exit-immediately`, `--cost-limit 0`, `max_tokens` unset |

## Architecture

mini-SWE-agent is the simplest autonomous agent in the study, in the sense of Anthropic's "Building effective agents": one augmented LLM in a loop whose only tool is a bash shell. Harbor starts it non-interactively with the task as `--task`. The model proposes a command, the command runs in the container, and the output comes back as the next observation. This repeats until the agent exits or the 3,600 s limit is reached. There is no planner, no subagent and no context summarisation.

## Notes from the first run

Pending first run.
