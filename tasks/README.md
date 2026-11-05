# tasks

`tasks.csv` holds the 72 benchmark tasks from 14 ReplicationBench papers. Values, tolerances and instructions come unchanged from the official task files in [replicationbench-release](https://github.com/Christine8888/replicationbench-release); the `source` column names each file. The rows for gw_nsbh, gw_cosmo and mars_clouds keep the team's Oct 18 verification.

`papers.csv` lists the 14 papers and flags which belong to the paraphrase block, the fault block and the human conditions.

## Rewordings

`instruction_p1` and `instruction_p2` are needed for the 25 paraphrase-block tasks (gw_nsbh, gw_cosmo, mars_clouds, galaxy_manifold). Each keeps every number, symbol, parameter name and output format. A second person checks each pair and signs `paraphrase_checked_by`. The gw_nsbh, gw_cosmo and mars_clouds rewordings were drafted with Claude on Oct 20; galaxy_manifold's are still to write.

## Locking

Set `locked` to `yes` on every row once the Harbor oracle passes all 72 tasks, and say so in the commit message. Earlier versions: 30-task set at commit `4a1bf2c` (Oct 18).
