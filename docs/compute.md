# Compute

No GPU is needed: the three GPU papers are excluded.

Harbor runs each trial in a container with 1 CPU and 4 GB of memory. Eight trials in parallel need about 8 CPUs and 32 GB of memory, plus disk for datasets and images, measured at the oracle run.

| Option | Notes |
|---|---|
| Lab workstation with Docker | Simplest if one is free for Nov 4 to 24 |
| Cloud VM with Docker | Pay per hour; size for 8 CPUs and 32 GB |
| Harbor cloud sandbox providers (Daytona, Modal and others) | Harbor runs trials there directly; useful for more parallelism |
| Savio | Harbor supports Singularity environments; needs a faculty computing allowance |

At the 3,600 s limit with 8 trials in parallel, the 2,096 automated trials need at most 262 hours (about 11 days).
