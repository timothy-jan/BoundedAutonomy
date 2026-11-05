# Trial table schema

One row per Harbor trial. Produced by `scoring/src/build_trial_table.py`. This is the
input to every Table 2 measure, so the columns are fixed here before the pilot and
changed only through a pull request.

Owner: Person E. Agreed with Persons B, C and D at the Sunday check-in.

## Grain

One row per trial directory, that is per `(job, task, repeat)`. Reruns of the same task
are separate rows; `trial_name` carries Harbor's random suffix and is unique within a job.
Rows are never aggregated in this file. Consistency and variance measures group these rows.

## Columns

| Column | Type | Source | Notes |
|---|---|---|---|
| `job_id` | str | `result.json` `config.job_id` | One Harbor `harbor run` invocation |
| `job_dir` | str | directory name | Batch timestamp, e.g. `2026-10-27__02-09-45` |
| `trial_name` | str | `result.json` `trial_name` | `<paper>__<task>__<suffix>`, unique in job |
| `paper_id` | str | `result.json` `task_name` | Parsed from `replicationbench__<paper>__<task>` |
| `task_id` | str | `result.json` `task_name` | Joins to the ReplicationBench task file |
| `task_checksum` | str | `result.json` `task_checksum` | Detects a task edited between runs |
| `agent` | str | `agent_info.name` | `oracle`, `terminus-2`, `claude-code`, ... |
| `agent_version` | str | `agent_info.version` | |
| `model` | str | `agent_info.model_info`, else `config.agent.model_name` | Null for the oracle |
| `status` | str | derived | `ok`, `exception`, or `no_verifier` |
| `reward` | float | `verifier_result.rewards.reward` | Mirrors `verifier/reward.txt` |
| `passed` | bool | `reward == 1` | Harbor's own pass or fail |
| `reported_value` | json | see **Reported value** below | Scalar, list or dict |
| `expected_value` | json | ReplicationBench task file `expected_output` | Scalar, list or dict |
| `tolerance` | json | ReplicationBench task file `tolerance` | Mirrors the answer's shape; `0` means exact match |
| `value_kind` | str | derived | `scalar`, `list` or `dict` |
| `n_elements` | int | derived | Numeric leaves in the answer, 1 to 19 |
| `normalized_error` | float | derived | Max over leaves; `inf` possible, see below |
| `normalized_error_vector` | json | derived | One entry per leaf |
| `wall_time_sec` | float | `finished_at - started_at` | Whole trial, including container build |
| `agent_exec_sec` | float | `agent_execution` span | Compare across agents, not `wall_time_sec` |
| `verifier_sec` | float | `verifier` span | |
| `n_input_tokens` | int | `agent_result.n_input_tokens` | Null for the oracle |
| `n_cache_tokens` | int | `agent_result.n_cache_tokens` | |
| `n_output_tokens` | int | `agent_result.n_output_tokens` | |
| `n_total_tokens` | int | `n_input_tokens + n_output_tokens` | Harbor's input count already includes cache, so cache is not added again. Null if both are null |
| `cost_usd` | float | `agent_result.cost_usd` | Null for the oracle |
| `confidence` | float | trial report | Not yet emitted, see **Open items** |
| `notes` | str | derived | Parse problems, one short phrase each |

## Reported value

Harbor's reward is 0 or 1, so normalized error needs the number the agent actually
reported. It is read in this order, first hit wins, and `notes` records which:

1. `artifacts/**/result.json` -- the container's `/app/result.json`, if it was copied out.
   This is the correct source and the only one that works for a real agent.
2. `agent/<agent>.txt` -- the agent's stdout, if it contains a JSON object with a
   `value` key. The oracle echoes its answer here; no other agent is expected to.

`verifier/test-stdout.txt` is **not** a source. The adapter runs pytest without `-v` or
`-s`, so it prints only `PASSED`/`FAILED` and never the value or the tolerance.

## Normalized error

Absolute difference over tolerance, at each numeric leaf of the answer:

```
e_i = |reported_i - expected_i| / tolerance_i
```

`normalized_error_vector` holds every `e_i`; `normalized_error` holds the **maximum**. The
maximum is the summary so that `normalized_error <= 1` means the same thing as `passed`:
every leaf within tolerance, which is what the verifier tests.

Answers are not all flat. In the first oracle job, of 92 trials:

| `value_kind` | Trials | Shape | Example |
|---|---|---|---|
| `scalar` | 40 | one number | `gw_cosmo__dark_energy` -> `0.05` |
| `list` | 48 | flat list, or a list of `[value, uncertainty]` pairs | `eht_resolve__eht_ring_size` -> `[[44.1, 1.2], ...]` |
| `dict` | 4 | keyed by quantity name, values scalar or list | `MUSE_outflows__electron_density` -> `{"ne_narrow": [300, 100], ...}` |

The tolerance mirrors the answer's shape exactly, so reported, expected and tolerance are
walked together and flattened to one vector of leaves. `n_elements` is the leaf count,
from 1 to 19. A scalar tolerance against a list applies to every element.

**Zero tolerance means exact match.** Four tasks set a tolerance of `0` on at least one
leaf, always an integer count (`ver_waves__gaia_rv_sample_size` expects `864268` with
tolerance `0`; `galaxy_soptics__shi_catalog_acquisition` mixes `0` in with real
tolerances). `|diff| / 0` is undefined, so such a leaf scores `0.0` on an exact match and
`inf` otherwise. `inf` is written literally in the CSV.

`normalized_error` is null, and `notes` says why, when the reported value is missing, is
not numeric, or has a shape or length that disagrees with `expected_value`. A missing
value is never scored as 0.

**Boundary note.** `passed` comes from the verifier and is authoritative. A leaf landing
exactly on its tolerance can compute to `1.0000000000000002` in floating point, so do not
rederive pass or fail from `normalized_error`; use `passed`. `normalized_error` describes
how far off an answer was, it does not decide the outcome.

## Published values and tolerances

Joined from `replicationbench-release/src/dataset/tasks/<paper_id>/<task_id>.json`, on
`paper_id` and `task_id`. All 87 distinct tasks in the first oracle job join, and all are
`kind: numeric`.

`tasks/tasks.csv` is **not** the join source yet. It holds 30 rows from the five paper
scope and matches only 22 of the 87 tasks run. When the 72 row file in pull request #1
merges, this schema changes to join on `tasks.csv` and to check it against the
ReplicationBench files, since rule 4 in `tasks/README.md` requires the two to agree.

## Known shapes in the data

- Person B ran on Windows. Paths inside `result.json` use backslashes
  (`datasets\batch_04\gw_cosmo__dark_energy`) and `trial_uri` is a `file:///C:/...` URL.
  Do not split on `/`.
- A crashed trial has `exception.txt` and no `verifier/` directory. 7 of 92 trials in the
  first oracle job crashed on Docker compose startup, all `hubble_trails`.
- The first oracle job is 92 trial directories over 87 distinct tasks, so 5 are reruns.

## Validation of the first run

`scoring/out/oracle-job-2026-10-27.csv` is this schema applied to Person B's first oracle
job. The oracle writes the published answer, so it is a check on the whole path from
export to metric:

- 92 rows: 85 `status = ok`, all with `reward = 1`; 7 `status = exception`.
- All 85 scored rows have `normalized_error` exactly `0.0`, as the oracle must.
- `passed` agrees with `normalized_error <= 1` on all 85 rows.
- Every one of the 87 distinct tasks joined to a ReplicationBench task file.
- `n_input_tokens`, `cost_usd` and `confidence` are empty on every row, which is correct
  for the oracle and is open items 1 to 3 below, not a parse failure.

`tests/test_trial_table.py` covers the error walk, the zero tolerance rule, the shape
mismatches and the token fallbacks: 37 tests.

## Open items

1. **Reported value for real agents.** Nothing copies `/app/result.json` out of the
   container; `artifacts/manifest.json` collects only `/logs/artifacts`. Until Person B
   adds it to the job config, or the verifier prints the parsed value, correctness and
   normalized error cannot be computed for any non oracle trial. Blocks Person C's handoff.
2. **Confidence.** No trial writes a report, because the shared instruction does not ask
   for one. Person C owns adding the request; this schema needs the file path and the
   field name before `confidence` can be filled.
3. **Tokens and cost.** Every `agent_result` field is null in the oracle job, so the
   parser's per agent branches are written against the Harbor schema but untested. First
   real check is Person C's Terminus-2 and Claude Code runs.
4. **Trajectory.** No trajectory is written by the oracle. Column set above does not yet
   cover tool call counts, which Table 2 needs for resource consistency.
5. **Task count.** 90 tasks generated where the prospectus says 72. Person B's item, but
   it sets the denominator for every rate in Table 2.
