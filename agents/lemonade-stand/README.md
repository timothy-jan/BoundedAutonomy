# Lemonade Stand

Pinned at 1.0.0-rc.57, commit `92ae62f` (see `FROZEN_TAG.md`). Added to Harbor as a custom agent. Owner: Person D.

## Integration plan

1. Check whether the Python server starts headless on Linux without the desktop window.
2. Find the server API for starting a bot, sending an instruction and reading the reply, with the app token.
3. Go or no-go by Oct 22. If headless fails, run Lemonade Stand outside the container with tools that execute inside it.
4. Write the Harbor agent: a class extending `BaseInstalledAgent` with `name()`, `setup()` and `run()`, plus an install script template.
5. Write token and cost totals where scoring can read them.
6. Run one gw_cosmo task on each model.

If the agent is not working by Nov 1, Lemonade Stand runs on a reduced task set and the change is logged.
