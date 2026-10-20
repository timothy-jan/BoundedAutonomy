# tasks

`tasks.csv` is the single source of truth for the task subset (§3, §4.2). The driver and scorer both read it.

1. Fill one row per task from the five selected ReplicationBench papers.
2. Verify each published value against its source in the paper and set its tolerance before any session (§2).
3. The file is unlocked (`locked` = `no`) while the team adds paraphrases and fixes IDs. Anyone may change it through a pull request.
4. Published values and tolerances must still match the official ReplicationBench task files. Say in the pull request if a change touches either.
5. Before the pilot on Oct 26, set every row's `locked` to `yes` and tag the commit `tasks-locked-YYYY-MM-DD`. After that, changes need a reason in the pull request and an entry in `docs/decisions/decision-log.md`.

The Oct 18 snapshot is preserved as the git tag `tasks-locked-2026-10-18`.

`papers.csv` lists the five papers. `instruction_p1` and `instruction_p2` hold the two paraphrases (Table 1, Robustness).
