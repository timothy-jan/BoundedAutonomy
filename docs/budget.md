# API budget

| Block | Trials |
|---|---|
| Pilot | 48 |
| Reliability core | 1,728 |
| Paraphrase | 200 |
| Fault injection | 120 |
| Total | 2,096 |

Plus 24 human sessions with Claude Code on Model A, and Automated Reviewer calls on 324 reports (300 sampled trials and 24 human sessions).

Tokens are recorded, not capped. Estimated cost = trials × mean cost per trial for each configuration, measured in the pilot. Fill in on Nov 3.

## Spending limits to set now

- [ ] One API key per model per role (agents, reviewer, human sessions)
- [ ] A monthly limit on each key, sized from the pilot
- [ ] Lemonade Stand's daily USD limit high enough for 8 parallel trials
