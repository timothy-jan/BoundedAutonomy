# Driver interfaces

Proposal for the Wednesday Oct 21 check-in. Four teams plug into the driver, and each connection is fixed here so they can build in parallel. Change a field only by editing this file in a pull request.

## Session folder

Every session writes one folder, `runs/<session_id>/`. `session_id` is `<paper_id>-<model>-<harness>-<variant>-<instruction_version>-<fault_id>-r<repeat>`.

| File | Written by | Read by |
|---|---|---|
| `manifest.json` | Driver | Scoring, evidence package |
| `events.jsonl` | Driver (Lemonade Stand) or converter (Inspect log) | Scoring, traceability sample |
| `submission.json` | Agent | Scoring |
| `report.md` | Agent, final step | Reviewer, scoring (confidence) |
| `workspace/` | Agent | Traceability sample |

## 1. Log schema (driver to scoring)

`events.jsonl` holds one JSON object per line, in time order.

| Field | Type | Notes |
|---|---|---|
| `t` | ISO 8601 string | UTC |
| `type` | string | `plan`, `decision`, `tool_call`, `tool_result`, `artifact`, `failure`, `intervention`, `message` |
| `role` | string | Agent role in the variant, e.g. `planner`, `executor`, `verifier`, `subagent-2` |
| `tokens_in` | integer | Per model call, 0 otherwise |
| `tokens_out` | integer | Per model call, 0 otherwise |
| `cost_usd` | number | From the Lemonade Stand ledger or provider usage |
| `tool` | string | For `tool_call` and `tool_result` |
| `path` | string | For `artifact`: path inside `workspace/` |
| `detail` | string | Free text, truncated at 4 KB |
| `cause` | string | For `intervention`: the student's reason |

The reference scaffold's Inspect logs are converted into the same schema by the scoring code, so both harnesses are scored identically.

## 2. Variant settings (variants to driver)

The driver passes `variant` to Lemonade Stand as one of `single-loop`, `planner-executor`, `orchestrator`, `generator-verifier`. Each variant's README lists the exact Lemonade Stand settings it sets. All variants share:

| Setting | Value |
|---|---|
| Tokens per session | 5,000,000, summed over every role |
| Wall clock per session | 21,600 s |
| Tool call timeout | 7,200 s |
| Tools | Python, bash, file read and write |
| System prompt | ReplicationBench `src/evaluation/core/prompts.py` |

## 3. Report and submission (agent to reviewer and scoring)

`submission.json` uses the structure of each task's `expected_output` in ReplicationBench, keyed by `task_id`. A task the agent could not compute is `null`.

`report.md` follows `docs/protocols/report-template.md`. The reviewer reads the whole file as text. Scoring reads the results table, with one row per task: task ID, reported value, units, confidence from 0 to 1, supporting artifact path.

## 4. Fault hooks (faults to driver)

The driver reads `fault_id` from the session config and looks it up in `faults/faults.csv`.

| Field | Meaning |
|---|---|
| `fault_type` | `missing_file`, `corrupted_value`, `misleading_error` |
| `target` | File path or tool name |
| `injection_point` | `before_start` (file removed or altered before the agent starts), `on_write` (file altered after the agent first writes it), `tool_wrapper` (tool returns the injected error on call N) |
| `seed` | Integer, so the fault is identical across harnesses and repeats |

Injectors live in `faults/injectors/` and take the session `workspace/` path and the seed. They never touch the prompt.
