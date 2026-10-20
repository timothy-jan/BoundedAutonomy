# Compute

## GPU need

Only astm3 needs a GPU. Its tasks train an Informer encoder, a GalSpecNet spectra encoder and the AstroM3 CLIP model (100 pre-training epochs, 50 fine-tuning epochs, 5 seeds). ReplicationBench marks it `needs_gpu: true` and runs GPU papers with device access through `nvidia-container-toolkit`.

| astm3 sessions | Count | GPU-hours at the 6 h cap |
|---|---|---|
| Model and harness comparison | 20 | 120 |
| Architecture variants | 24 | 144 |
| Paraphrase | 8 | 48 |
| Fault injection | 6 | 36 |
| Total | 58 | 348 (worst case) |

astm3 is excluded from the human conditions and from the pilot, so no human session needs a GPU.

## Options

| Option | How | Notes |
|---|---|---|
| Savio (Berkeley Research Computing) | A faculty PI requests a Faculty Computing Allowance in the MyBRC portal, then approves Timothy's "Join" request | No cost. Students cannot hold an allowance themselves. Savio supports Apptainer (Singularity) containers, which ReplicationBench also supports |
| Cloud GPU credits | Sponsor or department funds a single-GPU instance | Easiest to match Docker setup; cost scales with the 348 GPU-hour worst case |
| Drop astm3 from GPU blocks | Decision log entry and sponsor approval | Last resort; changes the paper set |

Action: ask a faculty PI to add the project to their allowance, or ask Major Allen whether the sponsor can fund cloud GPU time. Decide by Oct 23 so the setup is ready for Nov 4.

Sources: [Savio accounts](https://docs-research-it.berkeley.edu/services/high-performance-computing/getting-account), [ReplicationBench](https://github.com/Christine8888/replicationbench-release).
