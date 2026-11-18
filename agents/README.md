# Agents

Four harnesses, each documented in its own folder. All four are built into Harbor 0.25.0, so none needs custom agent code. Owners: Person C (Terminus-2, mini-SWE-agent, Claude Code, Codex), Person D (OpenHands).

| Harness | Folder | Models | Architecture |
|---|---|---|---|
| Terminus-2 | `terminus-2/` | A and B | Harbor's reference single agent loop in a terminal |
| mini-SWE-agent | `mini-swe-agent/` | A and B | Minimal loop, bash only |
| Claude Code | `claude-code/` | A | Production coding agent with planning and subagents |
| Codex | `codex/` | B | Production coding agent |
| OpenHands | `openhands/` | A and B | Open-source agent platform (OpenHands Software Agent SDK): terminal, file editor and task tracker tools |

Each folder's README records: pinned version, exact model strings, tools available, settings changed from default, and the architecture in one paragraph.
