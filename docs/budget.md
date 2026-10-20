# API budget

## Sessions

| Block | Sessions |
|---|---|
| Pilot (gw_nsbh, 1 model: 3 repeats + 1 pass of each of 4 variants) | 7 |
| Model and harness comparison | 100 |
| Architecture variants | 120 |
| Paraphrase | 40 |
| Fault injection | 30 |
| Human-assisted and checkpoint | 24 |
| Total | 321 |

## Tokens

| Case | Tokens per session | Total tokens |
|---|---|---|
| Worst case (every session hits the cap) | 5,000,000 | 1.605 billion |
| Planning case (half the cap) | 2,500,000 | 0.80 billion |
| Measured | From the pilot | Fill in Nov 3 |

Dollar cost = tokens × each model's blended price per token. Fill in once the two models are confirmed at the Nov 3 milestone. Split the session counts evenly between the two models, except fault injection (all 30 on one model).

The reviewer adds one review per session report (321 reports). With `num_reviews_ensemble=5` that is 1,605 GPT-4o calls on short reports.

## Spending limits to set now

- [ ] A separate API key per study model, used only by the driver
- [ ] A monthly spending limit on each key in the provider console, set to the planning case until the pilot measures real usage
- [ ] A separate key for the reviewer
- [ ] The Lemonade Stand daily USD limit (rc.57) set high enough for four parallel sessions
