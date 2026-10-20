# Bounded Autonomy in Scientific Replication

NewSpace at Berkeley research project, Fall 2026. Sponsor: Major Sean P. Allen.

We run Lemonade Stand at one frozen version, four architecture variants inside it, and a reference scaffold on about 20 ReplicationBench tasks from five papers. Sessions vary by autonomy condition, harness, and model. Every result is scored outside the system against a published value with a tolerance fixed in advance.

## Layout

| Folder | Contents | Prospectus | Owner |
|---|---|---|---|
| `docs/` | Schedule, protocols, decision log | §7, §8 | Timothy |
| `tasks/` | Task subset, published values, tolerances, paraphrases | §2, §4.2 | Timothy, Person A |
| `harness/` | Frozen Lemonade Stand tag, architecture variants, reference scaffold | §4.1 | Person C, Person B|
| `driver/` | Scripted run driver and session configs | §3, §4.1 | Person D |
| `faults/` | Fault injection set | §4.3 | Person A |
| `reviewer/` | AI Scientist Automated Reviewer setup and adapted form | §3 | Person B |
| `scoring/` | Logging schema and metric pipeline | §4.4, Table 2 | Person E |
| `experiments/` | Pilot and session block definitions, human condition assignments | §3, §4.4, Table 1 | Timothy |
| `runs/` | Session exports (not committed) | §3 | Person D |
| `analysis/` | Traceability sample, failure taxonomy, variance split | §4.3, Table 2 | Person E |
| `paper/` | Draft paper, figures, AI use disclosure | §8 | Everyone |
| `presentation/` | Final presentation | §8 | Everyone |
| `evidence/` | Evidence package linking each result to its sources | §8 | Timothy |
| `tests/` | Tests for driver, scoring, and faults | §8 | Everyone |

## Rules

1. Every session uses the frozen Lemonade Stand tag in `harness/lemonade-stand/FROZEN_TAG.md`.
2. `tasks/tasks.csv` is unlocked for pull requests until the Oct 26 pilot, then relocked (see `tasks/README.md`).
3. Any change to scope, sequence, or method is recorded in `docs/decisions/decision-log.md` (§7).
4. Scoring reads only from retained session exports. Nothing in `scoring/` runs inside a session.
5. Session exports and API keys are never committed.

## Milestones

| Date | Milestone |
|---|---|
| Oct 9 | Scope and metric definitions signed off |
| Oct 18 | Papers, task subset, and tolerances fixed; Lemonade Stand frozen |
| Nov 3 | Pilot reviewed; session time, budget, and models confirmed |
| Nov 24 | Planned sessions complete |
| Dec 11 | Draft paper complete and sent for release review |
| Jan 4, 2027 | Preprint posted |
