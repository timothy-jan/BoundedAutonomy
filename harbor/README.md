# Harbor

[Harbor](https://github.com/harbor-framework/harbor) (Apache 2.0) runs every agent on the same containerized tasks. Its ReplicationBench adapter (`adapters/replicationbench/` in the Harbor repo) packages 90 expert-curated numeric tasks from 17 papers, with reported parity against the original benchmark. Owner: Person B.

## Setup

```
uv tool install harbor
git clone https://github.com/harbor-framework/harbor
cd harbor/adapters/replicationbench
cp <this repo>/harbor/exclude_papers.txt exclude_papers.txt
uv run replicationbench
```

The task count after generation must be 72. Record the Harbor version and adapter commit in `VERSION.md`.

## Validation

Run the oracle agent on all 72 tasks before any real agent. Every trial must score 1. Record any failure and its cause in `VERSION.md`.

```
harbor run -c adapters/replicationbench/replicationbench.yaml -a oracle \
  -x "*abacus__*" -x "*astm3__*" -x "*hubble_trails__*" \
  --no-delete -n 8
```

- The three `-x` filters drop the GPU papers, so the job has 72 tasks even if the dataset was generated without our exclude list or pulled from the registry (`-d replicationbench@1.0`, 90 tasks).
- `--no-delete` keeps each task's Docker image. With delete on, Harbor runs `docker compose down --rmi local` after every trial, so every trial rebuilds its image and re-downloads its dataset. Keep delete off for every run in this study and check disk with `docker system df`.
- `-n` sets parallel trials (Harbor's default is 4). Image builds are network and disk bound, so raise it as far as the machine allows.

## Job configs

| File | Block | Trials |
|---|---|---|
| `configs/pilot.yaml` | Pilot: 6 tasks (gw_cosmo, mars_clouds) × 8 configurations | 48 |
| `configs/core.yaml` | Reliability core: 72 tasks × 8 configurations × 3 repeats | 1,728 |

Replace `MODEL_A` and `MODEL_B` with the exact model version strings chosen at the pilot. Confirm that `n_attempts: 3` produces three independent trials per task and configuration. The Lemonade Stand entries are added once its Harbor agent works.

Trial limits come from the adapter's `task.toml`: 3,600 s agent time, 1 CPU, 4 GB memory, no GPU.
