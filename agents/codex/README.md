# Codex

| Field | Value |
|---|---|
| Harbor agent name | `codex` |
| Version | 0.165.0 (`kwargs: {version: "0.165.0"}`), installed with `npm install -g @openai/codex@0.165.0` on Node 22 via nvm |
| Models | B |
| Tools | Codex CLI's built-in tools, with `unified_exec` (shell) enabled. Native web search is left at Codex's own default, because Harbor's `disable_web_search` defaults to false |
| Settings changed from default | Version pinned. Everything else is Harbor's default: `codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check --json --enable unified_exec`, with reasoning effort and summary unset |

## Architecture

Codex is a production autonomous agent in the sense of Anthropic's "Building effective agents": an augmented LLM in a loop that chooses its own shell and file actions from what the environment returns. Harbor runs it non-interactively with `codex exec`. Approvals and Codex's own sandbox are switched off, so the Harbor container is the only boundary. The JSON event stream is kept as the trajectory. The run ends when the model stops or the 3,600 s limit is reached.

## Notes from the first run

Pending first run.
