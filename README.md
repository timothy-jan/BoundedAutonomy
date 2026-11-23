# Bounded Autonomy in Scientific Replication

NewSpace at Berkeley research project, Fall 2026. Sponsor: Major Sean P. Allen.

A reliability benchmark for science agents. 72 ReplicationBench tasks from 14 papers run through [Harbor](https://github.com/harbor-framework/harbor) on four harnesses (Terminus-2, mini-SWE-agent, Claude Code or Codex, and OpenHands) and two models. The benchmark adds repeated trials, reworded instructions, injected faults, autonomy conditions and traceability checks to ReplicationBench's single success score. Design: [revised prospectus](https://claude.ai/artifact/GYbHkatnN7xqNVVrATNQas).

## Layout

| Folder | Contents | Prospectus | Owner |
|---|---|---|---|
| `docs/` | Prospectus, schedule, protocols, decision log, compute, budget | §7, §8 | Timothy |
| `tasks/` | The 72 tasks, published values, tolerances, rewordings | §3 | Timothy, Person A |
| `harbor/` | Pinned Harbor version, excluded papers, job configs for each block | §4.1 | Person B |
| `agents/` | One folder per harness: version, settings, architecture | §3, §4.1 | Persons C, D |
| `faults/` | Fault injection set | §4.3 | Person A |
| `reviewer/` | AI Scientist Automated Reviewer setup and adapted form | §3 | Person B |
| `scoring/` | Trial table and reliability metrics from Harbor outputs | §4.4 | Person E |
| `experiments/` | Pilot plan, block definitions, human condition assignments | §3, §4.2 | Timothy |
| `runs/` | Harbor job outputs (not committed) | §3 | Person B |
| `analysis/` | Traceability sample, failure taxonomy, variance split | §4.3, §4.4 | Person E |
| `paper/` | Draft paper, figures, AI use disclosure | §8 | Everyone |
| `presentation/` | Final presentation | §8 | Everyone |
| `evidence/` | Evidence package linking each result to its sources | §8 | Timothy |
| `tests/` | Tests for scoring and fault injectors | §8 | Everyone |

## Rules

All changes go through pull requests; see `CONTRIBUTING.md`.

1. Tasks, published values and tolerances come unchanged from ReplicationBench.
2. Every agent runs the same instruction, container limits and time limit.
3. `tasks/tasks.csv` is locked once the oracle run passes. Changes after that need a reason in the pull request.
4. Any change to scope, sequence, or method is recorded in `docs/decisions/decision-log.md` (§7).
5. Scoring reads only retained Harbor outputs. Nothing in `scoring/` runs inside a trial.
6. Harbor job outputs and API keys are never committed.

## Status (Nov 17)

- **Done:** task set (72 tasks), Harbor oracle run, all four harnesses set up in Harbor, the scorer, and one token cap for every agent.
- **Blocked:** no paid trial can run until the sponsor's API credits arrive. The budget is $3,000.
- **Open:** model versions, and a first real run of OpenHands (`agents/openhands/README.md`).

## Milestones

Revised Nov 17. Dates from the pilot onward assume API keys by Nov 24 and slide day for day if the keys come later. Full schedule: [`docs/schedule/timeline.md`](docs/schedule/timeline.md).

| Date | Milestone |
|---|---|
| Oct 27 | Harbor oracle run complete; task file locked |
| Nov 5 | Harbor design, four harnesses and scorer merged into `main` |
| Keys (target Nov 24) | API credits and keys received; spending limits set |
| Keys + 7 (target Dec 1) | Pilot reviewed; models, cost per trial and the OpenHands agent confirmed |
| Dec 11 | All 24 human sessions complete |
| Dec 22 | All 2,096 trials complete |
| Jan 22, 2027 | Draft paper complete and sent for release review |
| Feb 12, 2027 | Preprint posted and benchmark released |
