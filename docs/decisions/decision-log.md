# Decision log (§7)

| Date | Decision | Type (scope, sequence, method) | Reason | Decided by |
|---|---|---|---|---|
| 2026-10-06 | Prospectus issued | scope | Baseline | Sponsor |
| 2026-10-20 | Unlocked `tasks.csv` for pull requests; Oct 18 version kept at commit `4a1bf2c`; relock before the Oct 26 pilot | sequence | Paraphrases need rewriting and mars_clouds IDs need renaming | Timothy |
| 2026-10-20 | Task set is 30 tasks across 5 papers, not ~20 | scope | All tasks of each selected paper kept; sessions run per paper, so session count is unchanged | Timothy |
| 2026-10-20 | Lemonade Stand frozen at 1.0.0-rc.57, commit `92ae62f` | method | Last release before the Oct 18 milestone; recorded two days late | Timothy |
| 2026-10-20 | Human-condition papers: gw_nsbh, gw_cosmo, fable_mps, mars_clouds | method | astm3 needs GPU training and has the highest difficulty (5.4) | Timothy |
| 2026-10-20 | Human-condition assignments randomized with seed 20261020 (`experiments/human-conditions/randomize.py`) | method | 3 sessions per paper per condition; each student runs every paper once, 2 per condition | Timothy |
| 2026-10-20 | Reference scaffold is ReplicationBench's Inspect AI agent; agent mode fixed by Oct 22 | method | Matches the scaffold behind the benchmark's published results | Timothy |
| 2026-10-20 | Automated Reviewer model is GPT-4o; neither study model may be GPT-4o | method | AI Scientist README: reviews are best done with GPT-4o | Timothy |
| 2026-10-20 | Normalized error = abs(reported - published) / tolerance, per value | method | Scale-free across tasks; 1.0 marks the tolerance edge | Timothy |
| 2026-10-20 | Paraphrases drafted with Claude; human equivalence check pending | method | Speeds the robustness block; source noted in limitations if a Claude model is a study model | Timothy |
| 2026-10-20 | Pivot to a reliability benchmark built on Harbor and ReplicationBench; revised prospectus sent for sponsor approval | scope | Lemonade Stand is under continuous release and cannot anchor every comparison | Timothy |
| 2026-10-20 | Lemonade Stand kept as one of four evaluated harnesses (rc.57), alongside Terminus-2, mini-SWE-agent, and Claude Code or Codex | method | Keeps the sponsor's system in the study without making it the baseline | Timothy |
| 2026-10-20 | Task set is 72 tasks from 14 papers: Harbor's ReplicationBench set minus abacus, astm3, hubble_trails | scope | Breadth for a benchmark; no GPU needed. fable_mps dropped because Harbor excludes it for data size | Timothy |
| 2026-10-20 | Unit of execution is one trial on one task with Harbor's limits (3,600 s, 1 CPU, 4 GB) | method | Matches Harbor and the benchmark's grading unit; replaces 6 h paper sessions | Timothy |
| 2026-10-20 | Human conditions use Claude Code on Model A; papers gw_nsbh, gw_cosmo, mars_clouds, galaxy_manifold; re-randomized with seed 20261020 | method | fable_mps is no longer in the task set | Timothy |
| 2026-10-20 | Reviewer scores a stratified sample of 300 trial reports plus all 24 human sessions | method | Scoring all 2,096 reports with a 5-review ensemble is not needed for the agreement test | Timothy |
| 2026-10-20 | Superseded: custom driver, four Lemonade Stand variants, ReplicationBench Inspect scaffold as reference | method | Replaced by Harbor and its built-in agents | Timothy |
