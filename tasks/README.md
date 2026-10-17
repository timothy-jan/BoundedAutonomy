# tasks

`tasks.csv` is the single source of truth for the task subset (§3, §4.2). The driver and scorer both read it.

1. Fill one row per task from the five selected ReplicationBench papers.
2. Verify each published value against its source in the paper and set its tolerance before any session (§2).
3. When every row is verified, set `locked` to `yes` and tag the commit `tasks-locked-YYYY-MM-DD`.
4. After locking, changes go through a pull request with the reason, and are logged in `docs/decisions/decision-log.md`.

`papers.csv` lists the five papers. `instruction_p1` and `instruction_p2` hold the two paraphrases (Table 1, Robustness).
