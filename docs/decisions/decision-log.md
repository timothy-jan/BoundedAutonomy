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
| 2026-10-28 | Every task instruction is extended with the report request via Harbor's extra_instruction_paths, and /app/result.json and /app/report.md are collected as artifacts | method | Scoring needs the reported value and the confidence; all agents must get identical text | Timothy (approved 2026-11-05) |
| 2026-11-05 | Revised Harbor design merged into `main` (pull request #1) ahead of sponsor approval | sequence | Runs window opened Nov 4; the team works from one branch | Timothy |
| 2026-11-05 | Token cap of 5,000,000 per trial (input including cache, plus output) for every agent, applied in scoring; Lemonade Stand's live stop is off by default | method | Harbor has no token limit common to all agents (Claude Code and mini-SWE-agent cap dollars, Terminus-2 and Codex nothing), so one rule after the run is the only identical treatment | Timothy |
| 2026-11-10 | Lemonade Stand dropped from the study; OpenHands (Harbor's built-in `openhands-sdk` agent, OpenHands SDK 1.58.2) takes its place as the fourth harness, on Models A and B. `agents/lemonade-stand/` and its driver test removed (last present at commit `3391f40`) | scope | rc.57's bots cannot run code, so its trials would measure the missing code tool rather than replication (go/no-go of Oct 27). OpenHands is built into Harbor 0.25.0, runs both Anthropic and OpenAI models, and reports tokens and cost like the other agents | Team (Timothy to confirm) |
| 2026-11-15 | API token budget is $3,000 | scope | Sponsor raised the budget | Sponsor |
| 2026-11-15 | Dec 11 draft is a target, not a hard deadline; team works through winter break | sequence | API credits not yet received, so runs could not start Nov 4 | Sponsor, Timothy |
| 2026-11-17 | Schedule re-based on the day API keys arrive: pilot keys to keys + 7, runs Dec 2 to 22, draft Jan 22, release Feb 12 (assuming keys by Nov 24) | sequence | No paid trial can run before the keys arrive | Timothy |
| 2026-11-22 | Lemonade Stand stays out of the study regardless of the credits outcome; the Nov 10 removal stands | scope | Confirms pull request #10 | Timothy |
