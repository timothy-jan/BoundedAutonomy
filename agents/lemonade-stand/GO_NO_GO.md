# Lemonade Stand in Harbor: go/no-go (Person D)

Confirmed on the frozen source, **1.0.0-rc.57 (commit 92ae62f)**, on Tue Oct 27.
This replaces the Oct 25 version, which was checked on rc.29.

## Short answer

**Headless: GO.** **As a fair comparison: still blocked on one decision.**
rc.57's bots cannot run code. Every other agent in the study can. Nothing
in rc.57 changed this.

## What was checked on rc.57

| Question | Result |
|---|---|
| Does the server start on Linux with no desktop window? | **Yes.** `app/server/stand.py` booted in 0.5 s with no display, standard-library Python only. It also runs from a copy with `app/desktop`, `research` and `modeltest` removed (18 MB). |
| Chat API | Unchanged from rc.29: `POST /api/chat` with `{"text", "conversation_id": null, "model", "effort"}`, streamed as server-sent events. Tested end to end in fake-model mode. |
| App token | `<home>/secrets/api-token`, minted on first start, sent as `X-Stand`. |
| Provider keys | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY`, `GOOGLE_AI_API_KEY` (not `GEMINI_API_KEY`; the agent maps it). |
| Tokens and cost | Ledger table `spend_events` in `<home>/stand.db`, written to `usage.json` and Harbor's `result.json`. |
| Spending limit | **Changed in rc.57.** One owner daily USD limit replaces all the per-run and per-bot caps. Saved as `{"version": 2, "daily_limit_usd": X}` in `<home>/spend-limits.json`. Default $10/day. |
| Model switching | When a call is refused for cost, rc.57 lowers effort and then moves to a cheaper model, **unless the model was chosen explicitly**. The driver always sends an explicit roster label, so the model never changes mid-trial. The driver also records any `downgrade` or `escalate` events. |
| Token cap (5M) | Enforced by the driver: it polls the ledger, and at the cap calls `POST /api/halt`, which refuses every new paid call. Tested: the next call was refused with code `halted`. The trial is marked `capped`. |
| File access | Bots read and write `/app` through the app's files folder (a link to `/app`); `/app/result.json` and relative paths both work, paths outside are refused. Limits: UTF-8 text only, 1 MiB per file, **256 MiB for the whole folder** (every write fails once `/app` holds more). gw_cosmo tasks are simulations, so this should not bite there. |
| **Can bots run code?** | **No.** 45 tools; `harness_state` itself says the app has no code runner, terminal or sandbox. `calculator_app` evaluates arithmetic only. |
| Turn length | rc.57's technical caps allow **12 tool rounds and 24 model calls per chat turn** (`ceilings.json` `tool_loop`). The driver sends the instruction as one turn. |

## Bugs fixed in the draft agent

1. **Trials would have hung.** The server was started with `cd … && nohup … &`,
   which backgrounds a subshell that keeps the exec's output open. The exec
   (including `docker exec`) never returned, and the cleanup killed the
   subshell instead of the server. Found by running Harbor 0.25.0's real
   `setup()`/`run()` against a local stand-in environment.
2. **No per-trial dollar limit.** The draft wrote the old eight-cap format.
   rc.57 only reads its `user_day` value and silently ignores the rest.
3. **`_resolve_env` overrode a Harbor base-class method** with a different
   return type, which breaks Harbor's own environment and key lookups.
   Renamed to `_ls_env`.
4. `--ak` examples used `key:float=value`. Harbor 0.25.0 takes `key=value`.
5. Harbor's `--effort` flag was ignored. It now sets Lemonade Stand's effort.

## Task data access (added Nov 1)

ReplicationBench puts task data in `/assets` and paper context in
`/app/resources`. rc.57's file tools see only the files folder (`/app`),
reject symlinks that leave it, and cap files at 1 MiB and the folder at
256 MiB. The agent copies `/assets` into `/app/assets` when it is ≤ 200 MiB
and records the outcome in `agent/assets.txt`. Bigger datasets stay out of
reach, a second gap versus shell-based agents. gw_cosmo has no data files,
so it isn't affected.

## Why the code question matters

All four gw_cosmo tasks ask for numbers that come from simulating 10,000
gravitational-wave events or fitting a posterior. Lemonade Stand's bots can
read `/app` and write `/app/result.json`, but they cannot run the simulation.
Expect near-zero scores, and read any correct answer as recall from the
paper (contamination), not replication.

The 12-round turn limit compounds this. Even with a code tool, one turn is
short next to what the other agents get in a 1-hour trial.

## Options for Timothy and the sponsor

1. **Run it frozen, as is.** The agent supports this today. The result
   mostly measures "no code tool", and the prospectus should say so.
2. **Give Lemonade Stand a shell tool for the benchmark only.** Changes the
   harness under study: needs the sponsor's approval, a new pinned commit
   and a decision-log entry (as `FROZEN_TAG.md` requires).
3. **Send "continue" turns until the bot stops or the trial times out.** A
   driver choice, not a code change, but it is a protocol decision and must
   be logged. Lifts the 12-round limit; does not fix the missing code tool.

The prospectus fallback (reduced set by Nov 1) still applies if none of these
is settled in time.

## Daily USD limit

Harbor gives every trial a fresh container, so each trial has its own
Lemonade Stand ledger. **The daily limit therefore applies to one trial, not
to the 8 parallel trials together.** Parallel trials cannot exhaust each
other's limit.

The limit must never end a trial before the 5M-token cap does. At 5M tokens
(95% input with no cache discount, 5% output), rc.57's own prices give at
most $30 for Opus 5, $12 for Sonnet 5, $8 for GPT-5. The default is
**$100 per trial**. Raise it to $150 only for GPT-6 Astra (up to $90 at 20%
output). Set per run with `--ak daily_usd_limit=150`.

Total exposure with 8 parallel trials is at most 8 × $100. The real guard is
the monthly limit on each provider key (`docs/budget.md`).

## Models

The two study models are confirmed at the Nov 3 milestone. rc.57's roster
covers GPT-5 mini, GPT-5, GPT-6 Luna/Astra, Haiku 4.5, Sonnet 5, Opus 5,
Grok 4.20 Fast/4.3/4.7 and Gemini 3.5 Flash-Lite/3.8 Flash. **Claude Opus 5.5
and Sonnet 5.5 are priced in rc.57 but not on its roster**, so the frozen
app cannot run them; the agent fails such trials instead of letting the app
pick another model.

## Still to do

- Run one gw_cosmo task per study model in Docker with real keys
  (`run_gw_cosmo.sh`). Not possible from the session that wrote this: no
  Docker daemon and no keys. A free smoke test first: `FAKE=1`.
- Decision on the code tool (above).

## Draft message to Timothy

> Lemonade Stand go/no-go, now confirmed on rc.57 (92ae62f): **headless is a
> GO.** The server starts in half a second with no display, and the Harbor
> agent runs a full trial (install, chat, tokens and cost into result.json)
> through Harbor 0.25.0's own setup and run code, in fake-model mode.
>
> **The blocker from Sunday stands:** rc.57's bots have no way to run code
> ("no code runner, terminal or sandbox", in its own tool list), and one chat
> turn allows 12 tool rounds. All four gw_cosmo tasks need simulation, so
> expect near-zero scores, and correct answers would come from recall.
>
> Decision needed from you/Sean: (1) run frozen and report the gap, (2) add a
> shell tool for the benchmark (new pinned commit + decision-log entry), or
> (3) let the driver send "continue" turns (protocol decision; fixes turn
> length, not the code gap).
>
> Spending: rc.57 has one daily USD limit, and since each trial is a fresh
> container it acts per trial. Set to $100, above what 5M tokens costs on any
> roster model except GPT-6 Astra. The driver enforces the 5M-token cap
> itself.
>
> Also: Opus 5.5 / Sonnet 5.5 are not on rc.57's roster, so the frozen app
> can't run them if either becomes a study model.
>
> Next: one gw_cosmo task per model with real keys, once the models are set.
