# Fault injection set (§4.3)

Five papers (gw_nsbh, gw_cosmo, mars_clouds, galaxy_manifold, ver_waves) × three fault types = 15 faults. Each runs on all 8 configurations: 120 trials. Owner: Person A.

1. Each fault targets one task per paper (`target_task_id`).
2. Faults go into the Harbor task copy, never the instruction: missing files through the environment's Dockerfile, the other two through a wrapper script in the container.
3. Each fault is seeded so it is identical across agents.
4. Each fault states how to tell whether the agent detected it, repaired it, or carried it into the final answer.
