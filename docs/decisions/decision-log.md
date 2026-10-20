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
