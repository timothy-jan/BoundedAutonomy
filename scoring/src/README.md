# scoring/src

Scorers. These read retained job exports only; nothing here runs inside a session (rule 4).

## build_trial_table.py

Turns a Harbor job export into the trial table defined in `../schema/trial-table.md`,
one row per trial.

```
python scoring/src/build_trial_table.py JOBS_DIR TASKS_DIR -o scoring/out/trial-table.csv
```

- `JOBS_DIR` a single Harbor job directory, or a parent holding several of them.
- `TASKS_DIR` the ReplicationBench task definitions, `replicationbench-release/src/dataset/tasks`.
  Published values and tolerances are joined from here, not from `tasks/tasks.csv`; see
  "Published values and tolerances" in the schema for why, and when that changes.

Job exports are not committed (`jobs/` is in `.gitignore`), so point it at wherever
Person B's handover was unpacked. Standard library only, no dependencies.

Tests: `python -m pytest tests/test_trial_table.py`
