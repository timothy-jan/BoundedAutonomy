# Scoring fixtures

Real Harbor job exports kept as test inputs for `scoring/src/build_trial_table.py`. Session exports and new job outputs still go out of band (repo rule 5); a file lands here only when a test or a validation in `scoring/schema/` depends on it.

| File | What it is | Used by |
|---|---|---|
| `oracle-job-2026-10-27.zip` | Person B's first oracle job: 92 trial folders over 87 tasks, 85 passed and 7 crashed on Docker compose startup (all `hubble_trails`). Paths inside are Windows-style. | `tests/test_trial_table.py`; the validation in `scoring/schema/trial-table.md`, which regenerates `scoring/out/oracle-job-2026-10-27.csv` |

Regenerate the oracle table:

```
unzip -q scoring/fixtures/oracle-job-2026-10-27.zip -d /tmp/oracle
python scoring/src/build_trial_table.py /tmp/oracle/jobs \
    <replicationbench-release>/src/dataset/tasks -o scoring/out/oracle-job-2026-10-27.csv
```
