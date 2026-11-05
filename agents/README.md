# Agents

Four harnesses, each documented in its own folder. Owners: Person C (built-in agents), Person D (Lemonade Stand).

| Harness | Folder | Models | Architecture |
|---|---|---|---|
| Terminus-2 | `terminus-2/` | A and B | Harbor's reference single agent loop in a terminal |
| mini-SWE-agent | `mini-swe-agent/` | A and B | Minimal loop, bash only |
| Claude Code | `claude-code/` | A | Production coding agent with planning and subagents |
| Codex | `codex/` | B | Production coding agent |
| Lemonade Stand | `lemonade-stand/` | A and B | Multi-bot team with a shared cost ledger; custom Harbor agent |

Each folder's README records: pinned version, exact model strings, tools available, settings changed from default, and the architecture in one paragraph.
