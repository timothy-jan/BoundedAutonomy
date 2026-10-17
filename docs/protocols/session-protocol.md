# Session protocol

1. One session is one bounded attempt on one paper (§2).
2. Caps: 6 hours and 5 million tokens per session (§3). A capped session is marked capped, not failed.
3. Every session starts from an identical clean state with the same data, tools, and budget.
4. Every session ends with the written report in `report-template.md`.
5. The full export is retained in `runs/<session_id>/` before any scoring.
