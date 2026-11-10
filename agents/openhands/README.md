# OpenHands

Replaces Lemonade Stand as the fourth harness (decision log, 2026-11-10).

| Field | Value |
|---|---|
| Harbor agent name | `openhands-sdk` |
| Version | OpenHands Software Agent SDK 1.58.2 (`kwargs: {version: "1.58.2"}`), installed with `uv pip install openhands-sdk==1.58.2 openhands-tools==1.58.2 fastapi` into a Python 3.12 venv inside the container. 1.58.2 was the newest release when Harbor 0.25.0 came out (both Oct 25) |
| Models | A and B, through LiteLLM (`anthropic/...` and `openai/...` model strings; keys from `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`) |
| Tools | Terminal, file editor and task tracker. No browser or web search tool; the terminal still has network access |
| Settings changed from default | Version pinned. Everything else is Harbor's default: 500 iterations per run (the SDK default, `max_iterations` unset), temperature and reasoning effort unset, no history condenser, no MCP servers, skills loaded only if the task container ships any |

## Why this agent

- It is built into Harbor 0.25.0, so it is two entries in each job config and no custom agent code.
- It runs both study models, so it fills both Lemonade Stand slots and the design stays at 8 configurations.
- Harbor copies its tokens (input, cache, output) and cost into `agent_result` and writes an ATIF trajectory, so `scoring/src/build_trial_table.py` reads it like the other built-in agents.
- It is a widely used open-source agent platform, which sits between the minimal loops (Terminus-2, mini-SWE-agent) and the vendor products (Claude Code, Codex).

Harbor also has an `openhands` agent, which runs the older `openhands-ai` package through `python -m openhands.core.main`. That entry point was removed after `openhands-ai` 1.6.0 (March 2026), so it only works pinned to an old release. `openhands-sdk` is the maintained path.

## Architecture

OpenHands is an autonomous agent in the sense of Anthropic's "Building effective agents": one augmented LLM in a loop that chooses its own actions from tool results. Harbor installs the SDK in the task container and runs a small runner script that builds an SDK `Agent` with three tools (a persistent terminal, a structured file editor and a task tracker for its own plan) and starts one conversation with the task instruction in the container's working directory. Unlike Terminus-2 it uses native tool calls and not keystrokes, and unlike mini-SWE-agent it has dedicated edit and planning tools beside the shell. The run ends when the agent finishes, reaches 500 iterations, or the 3,600 s limit is reached.

## Notes from the first run

Pending first run. To check then: the install fits in the trial (it downloads Python 3.12 and the SDK in every fresh container), both model strings resolve, and `agent_result` carries tokens and cost.
