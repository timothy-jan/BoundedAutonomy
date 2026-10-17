# Run driver (§3, §4.1)

Starts any session without the desktop interface. Owner: Person D.

## Session config fields
`paper_id`, `model`, `harness` (lemonade-stand or reference-scaffold), `variant`, `instruction_version` (original, p1, p2), `fault_id` (none or from `faults/faults.csv`), `repeat`, `seed`, `condition` (autonomous, checkpoint, human-assisted).

## Requirements
1. Clean identical initial state per session.
2. Caps of 6 hours and 5M tokens; capped sessions marked capped.
3. Four sessions in parallel, no shared state.
4. Manifest per session with config, frozen tag commit, provider model version string, start and end times.
5. Full export to `runs/<session_id>/`.
6. Report step from `docs/protocols/report-template.md` at the end of every session.
7. Pause hook at the two checkpoint gates.
