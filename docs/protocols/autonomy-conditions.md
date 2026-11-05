# Autonomy conditions (§4.2)

| Condition | Human role | Volume |
|---|---|---|
| Autonomous | Sets bounds, no further contact | 2,096 Harbor trials |
| Checkpoint | Approves or redirects only after the plan and after the first result | 12 sessions |
| Human-assisted | Works the paper with the agent, may step in at any point | 12 sessions |

The human conditions use Claude Code on Model A, since its approval prompts give natural checkpoints. Each of six students runs gw_nsbh, gw_cosmo, mars_clouds and galaxy_manifold once, two papers per condition. Assignments: `experiments/human-conditions/assignments.csv` (seed 20261020). Every intervention and its cause is logged.
