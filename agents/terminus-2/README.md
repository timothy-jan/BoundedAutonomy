# Terminus-2

| Field | Value |
|---|---|
| Harbor agent name | `terminus-2` |
| Version | Built into Harbor 0.25.0; reports agent version `2.0.0` |
| Models | A and B |
| Tools | One tmux terminal (160 x 40). Each turn the model returns JSON with `analysis`, `plan`, a list of `commands` (`keystrokes` plus a wait `duration`) and an optional `task_complete` flag |
| Settings changed from default | None. Harbor defaults: `parser_name: json`, `max_turns` unset (no practical limit), `enable_summarize: true` at 8,000 free tokens, temperature unset |

## Architecture

Terminus-2 is an autonomous agent in the sense of Anthropic's "Building effective agents": one augmented LLM in a loop, with no fixed workflow. It has a single tool, a tmux terminal. Each turn the model reads the latest screen, writes its analysis and plan, and sends keystrokes. The terminal output it gets back is its ground truth from the environment. The loop ends when the model sets `task_complete` or the 3,600 s limit is reached. When free context drops below 8,000 tokens, Harbor summarises earlier turns, so long trials run on a compressed history.

## Notes from the first run

Pending first run.
