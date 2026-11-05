# Claude Code

| Field | Value |
|---|---|
| Harbor agent name | `claude-code` |
| Version | 2.1.312 (`kwargs: {version: "2.1.312"}`), installed in the container by Anthropic's bootstrap script (npm on Alpine) |
| Models | A |
| Tools | Claude Code's built-in tool set. Its native `WebSearch` and `WebFetch` stay enabled, because Harbor's `disable_web_search` defaults to false |
| Settings changed from default | Version pinned. Everything else is Harbor's default: `--permission-mode=bypassPermissions`, `--print --output-format=stream-json`, and no `--max-turns`, `--max-budget-usd`, `--effort` or fallback model |

## Architecture

Claude Code is a production autonomous agent in the sense of Anthropic's "Building effective agents". An augmented LLM with file, shell and web tools runs in a loop and decides its own steps from tool results. It can also hand subtasks to subagents, which is the orchestrator-workers pattern inside the agent. Harbor runs it headless: the instruction goes in on stdin with `--print`, permission prompts are bypassed, and the stream-json output is saved as the trajectory. The run ends when the model stops or the 3,600 s limit is reached.

## Notes from the first run

Pending first run.
