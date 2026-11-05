# agents/lemonade-stand

Lemonade Stand (frozen at 1.0.0-rc.57, commit 92ae62f; see
`harness/lemonade-stand/FROZEN_TAG.md`) as a custom Harbor agent. Built
against Harbor 0.25.0. Checked on rc.57 and run through Harbor's own
`setup()`/`run()` in fake-model mode on Oct 27; see `GO_NO_GO.md`.

| File | What it is |
|---|---|
| `lemonade_stand_agent.py` | The Harbor agent (`BaseInstalledAgent`): `name()`, `install()`, `run()`, `populate_context_post_run()`. |
| `ls_driver.py` | Runs inside the container, standard library only. Sends the instruction as one chat, optionally stops at a token cap, saves the reply stream, final reply and usage. |
| `run_gw_cosmo.sh` | One gw_cosmo task on each model given. |
| `probe_headless.sh` | Go/no-go check on a checkout: headless start (fake mode, no keys) and whether any code-execution tool exists. |
| `GO_NO_GO.md` | Findings on rc.57, the open decision, daily-limit reasoning, message to Timothy. |

In Harbor 0.25.0 an installed agent implements `install()` itself; Harbor's
`setup()` calls it. The install-script template from the task list no longer
exists in this version, so there is none here.

## How a trial runs

1. `install()` refuses any checkout that isn't rc.57 (override with
   `--ak allow_unfrozen:bool=true`, tests only), uploads it (minus
   `app/desktop`, `research`, `modeltest`), checks for Python ≥ 3.10, makes
   a fresh home, links the home's `files` folder to `/app`, copies `/assets`
   into `/app/assets` when it is ≤ 200 MiB, and writes the daily USD limit in
   rc.57's format.
2. `run()` starts `python3 app/server/stand.py` in the background with
   `LEMONADE_STAND_HOME` set, then runs `ls_driver.py`.
3. The driver waits for `/api/health`, maps the Harbor model to rc.57's
   roster label (unknown models fail the trial), posts the instruction to
   `/api/chat`, and reads the stream until it ends or `turn_timeout_sec`
   (3,300 s) runs out. If `max_tokens` is set and the ledger reaches it, it
   calls `/api/halt` and marks the trial capped. It is off by default: the
   study's 5M token cap is applied to every agent in scoring, not live.
4. Bots read task inputs and write `/app/result.json` through their file
   tools. Harbor's verifier then scores it like any other agent.
   `run_gw_cosmo.sh` passes `--artifact /app/result.json`, which copies the
   answer to `<trial>/artifacts/app/result.json` where
   `scoring/src/build_trial_table.py` reads the reported value. Pass the same
   flag when calling `harbor run` directly.

Copying `/assets` only helps with text data. rc.57's file tools read UTF-8
text only, up to 1 MiB per file, so binary data in `/app/assets` (FITS,
`.npy`, HDF5) stays out of the bots' reach even when it was copied.

## Run

Smoke test, free (fake model, no keys):

```bash
FAKE=1 agents/lemonade-stand/run_gw_cosmo.sh \
  datasets/batch_04/gw_cosmo__h0_scaling ~/lemonade-stand anthropic/claude-sonnet-5
```

Real run, one trial per model (keys from your shell):

```bash
agents/lemonade-stand/run_gw_cosmo.sh \
  datasets/batch_04/gw_cosmo__h0_scaling ~/lemonade-stand \
  anthropic/claude-sonnet-5 openai/gpt-5
```

Or directly:

```bash
PYTHONPATH=agents/lemonade-stand harbor run \
  -p <gw_cosmo task dir> \
  -a lemonade_stand_agent:LemonadeStandAgent \
  -m anthropic/claude-sonnet-5 \
  --artifact /app/result.json \
  --ae LS_SOURCE_DIR=$HOME/lemonade-stand
```

The folder name has a hyphen, so it isn't a Python package; `PYTHONPATH` plus
the bare module name is how Harbor imports it.

Options (`--ak key=value`): `daily_usd_limit` (default 100),
`max_tokens` (default 0 = off; the study cap is applied in scoring), `effort` (auto/low/medium/high;
Harbor's `--effort` also works), `fake` (true for the fake model),
`turn_timeout_sec` (3300).

Provider keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY`,
`GOOGLE_AI_API_KEY` (`GEMINI_API_KEY` or `GOOGLE_API_KEY` are mapped to it).

## Output contract for Person E

Token and cost totals are copied into Harbor's standard `agent_result` in each
trial's `result.json` (`n_input_tokens` including cache, `n_cache_tokens`,
`n_output_tokens`, `cost_usd`, `model_usage` per model), so Lemonade Stand
reads the same way as every other agent. `agent_result.metadata` adds
`final_status`, `capped`, `model_label`, `bots`, `n_tool_calls`,
`daily_usd_limit` and the Lemonade Stand version and commit.

Each trial's `agent/` folder also holds:

* `usage.json`: the totals above plus `per_model`, `bots{agent_id: cost_usd}`,
  `n_calls`, `n_tool_calls`, `final_status` (`done`, `timeout`, `error`,
  `token_cap`, `spend_limit`, `http_<code>`, `connection_error`,
  `stream_error`), `capped`, `capped_at_tokens`,
  `max_tokens`, `wall_sec`, `model_label`, `model_used`, `models_seen`,
  `n_downgrades`, `n_escalations`, `n_spend_refusals`, `server_version`,
  `fake`.
* `stream.jsonl`: every event frame from the chat.
* `final_reply.md`: the reply text.
* `assets.txt`: whether `/assets` was copied in for the bots, and its size.
* `server.log`, `driver.txt`: raw logs.

`fake: true` trials are plumbing tests and do not count.
