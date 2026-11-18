# Timeline

Revised Nov 17. The original plan had runs from Nov 4 to Nov 24, but no paid trial can start until the sponsor's API credits arrive. Everything from the pilot onward now counts from the day the keys arrive. The dates below assume keys by Nov 24, and they slide day for day if the keys come later. The Oct 20 plan is kept in `timeline_2026-10-20.pdf`.

| Phase | Dates | Status |
|---|---|---|
| Scope and first task set | Oct 6 to Oct 20 | Done |
| Benchmark setup | Oct 21 to Oct 27 | Done. The oracle job ran on Oct 27 |
| Integration | Oct 26 to Nov 5 | Done. Agents, scorer and token cap merged on Nov 5 |
| Work that needs no keys | Nov 6 to keys | In progress. Faults, reviewer, model choice, compute |
| Pilot | Keys to keys + 7 days (Nov 24 to Dec 1) | Waiting on keys |
| Human sessions | Dec 2 to Dec 11 | Waiting on the pilot |
| Runs | Dec 2 to Dec 22 (reserve Dec 23 to Jan 3) | Waiting on the pilot |
| Analysis | Dec 14 to Jan 10 | |
| Writing | Jan 4 to Jan 22 | |
| Release review | Jan 22 to Feb 12 | |

## Milestones

| Date | Milestone |
|---|---|
| Oct 27 | Harbor oracle run complete; task file locked |
| Nov 5 | Harbor design, four harnesses and scorer merged into `main` |
| Keys + 0 (target Nov 24) | API credits and keys received; spending limits set |
| Keys + 7 (target Dec 1) | Pilot reviewed; models, cost per trial and the OpenHands agent confirmed |
| Dec 11 | All 24 human sessions complete |
| Dec 22 | All 2,096 trials complete |
| Jan 22, 2027 | Draft paper complete and sent for release review |
| Feb 12, 2027 | Preprint posted and benchmark released |

## Work that needs no keys (until the keys arrive)

- 15 faults defined in `faults/faults.csv`, with working injectors (Person A)
- Automated Reviewer pinned, review form adapted (Person B)
- Machine for 8 parallel trials confirmed (Person B)
- Candidate versions for Model A and Model B, priced per trial against the $3,000 budget (Person C, Timothy)
- OpenHands config loads in Harbor and is ready for its first run (Person D)
- Variance split and failure taxonomy scripts run on the oracle fixture (Person E)
