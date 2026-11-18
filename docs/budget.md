# API budget

Total: $3,000 in API tokens (sponsor, Nov 15).

| Block | Trials |
|---|---|
| Pilot | 48 |
| Reliability core | 1,728 |
| Paraphrase | 200 |
| Fault injection | 120 |
| Total | 2,096 |

Plus 24 human sessions with Claude Code on Model A, and Automated Reviewer calls on 324 reports (300 sampled trials and 24 human sessions).

Tokens are recorded for every trial and capped at 5,000,000 per trial in scoring (`docs/protocols/trial-protocol.md`). Agents are not stopped live, so a trial can spend past the cap; the 3,600 s limit bounds it. Estimated cost = trials × mean cost per trial for each configuration, measured in the pilot. Fill in when the pilot is reviewed.

## Spending limits to set now

- [ ] One API key per model per role (agents, reviewer, human sessions)
- [ ] A monthly limit on each key, sized from the pilot
