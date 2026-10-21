# Trial table

One row per Harbor trial. Agree on these columns at the Oct 21 check-in.

| Column | Source |
|---|---|
| `trial_id` | Harbor trial folder name |
| `block` | core, paraphrase, fault, pilot |
| `harness` | Harbor agent name |
| `model` | Exact model version string |
| `paper_id`, `task_id` | Task folder name `<paper_id>__<task_id>` |
| `repeat` | Attempt number |
| `instruction_version` | original, p1, p2 |
| `fault_id` | none or from `faults/faults.csv` |
| `reward` | `reward.txt` (0 or 1) |
| `reported_value` | Test output |
| `normalized_error` | Computed |
| `confidence` | From the trial's report |
| `seconds`, `tokens_in`, `tokens_out`, `cost_usd` | Agent logs and trajectory |
| `capped` | True if the 3,600 s limit was hit |
