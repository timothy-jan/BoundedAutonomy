"""Lemonade Stand as a Harbor installed agent (Person D, prospectus §4.1).

Harbor: 0.25.0 (commit 872da94). In this version an installed agent implements
``install()`` directly; the install-script template named in the task list no
longer exists. Harbor's own ``setup()`` calls ``install()``.

Lemonade Stand facts below were checked on the frozen source, 1.0.0-rc.57
(commit 92ae62f), on Oct 27; see GO_NO_GO.md.

  * Server: ``python3 app/server/stand.py --port N``. Standard library only,
    no pip install, no display needed. Data lives in ``$LEMONADE_STAND_HOME``.
  * Auth: ``<home>/secrets/api-token`` minted on first start, sent as X-Stand.
  * Provider keys (keys.py): ANTHROPIC_API_KEY, OPENAI_API_KEY, XAI_API_KEY,
    GOOGLE_AI_API_KEY.
  * Spending: rc.57 enforces ONE limit, the owner's daily USD limit, saved as
    ``{"version": 2, "daily_limit_usd": X}`` in ``<home>/spend-limits.json``.
    The per-run and per-bot dollar caps are gone. Each trial gets a fresh home,
    so this daily limit applies to one trial only; parallel trials never share
    it.
  * When a call is refused for cost, rc.57 lowers effort and then switches to
    a cheaper model, unless the model was chosen explicitly. The driver always
    sends an explicit roster label, so the model never changes mid-trial.
  * Closing the chat connection cancels the turn; ``POST /api/halt`` blocks
    every new paid call. The driver uses both to enforce the study's
    per-session token cap.
  * File tools are confined to ``<home>/files``; we make that a link to the
    task's /app so bots can read inputs and write /app/result.json (absolute
    and relative paths both work). Limits: UTF-8 text only, 1 MiB per file,
    256 MiB for the whole folder.

Run (from the repo root):

    PYTHONPATH=agents/lemonade-stand harbor run \
        -p <gw_cosmo task dir> \
        -a lemonade_stand_agent:LemonadeStandAgent \
        -m anthropic/claude-sonnet-5 \
        --ae LS_SOURCE_DIR=$PWD/vendor/lemonade-stand
"""

from __future__ import annotations

import json
import math
import os
import shlex
import tarfile
import tempfile
from pathlib import Path

from harbor.agents.installed.base import BaseInstalledAgent, with_prompt_template
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext, ModelUsage

FROZEN_VERSION = "1.0.0-rc.57"
FROZEN_COMMIT = "92ae62f"

# Inside the task container.
LS_ROOT = "/installed-agent/lemonade-stand"
LS_SRC = f"{LS_ROOT}/src"
LS_SERVER = f"{LS_SRC}/app/server"
LS_HOME = f"{LS_ROOT}/home"  # fresh per trial: every container is new
TASK_DIR = "/app"  # ReplicationBench WORKDIR; grader reads /app/result.json
LOG_DIR = "/logs/agent"  # synced to <trial>/agent/ on the host
ASSETS_COPY_LIMIT_KB = 200 * 1024  # leave room under the 256 MiB folder cap

HERE = Path(__file__).resolve().parent
# Top-level folders the server never imports (checked on rc.57: the stripped
# tree boots and chats). Matching is on whole path parts, so keep names unique.
SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build", "__pycache__",
             "desktop", "modeltest", "research"}

# Harbor/host name -> the name rc.57 reads (keys.py NAMES).
PROVIDER_KEYS = {
    "ANTHROPIC_API_KEY": ("ANTHROPIC_API_KEY",),
    "OPENAI_API_KEY": ("OPENAI_API_KEY",),
    "XAI_API_KEY": ("XAI_API_KEY",),
    "GOOGLE_AI_API_KEY": ("GOOGLE_AI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
}


class LemonadeStandAgent(BaseInstalledAgent):
    """Runs Lemonade Stand's backend headless in the task container and sends
    the task instruction as one chat."""

    def __init__(
        self,
        *args,
        daily_usd_limit: float = 100.0,
        max_tokens: int = 5_000_000,
        effort: str = "auto",
        fake: bool = False,
        allow_unfrozen: bool = False,
        server_port: int = 8272,
        turn_timeout_sec: int = 3300,
        reasoning_effort: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # Harbor's --effort flag arrives as reasoning_effort; use it so the
        # same flag sets effort for every agent. rc.57 takes auto|low|medium|high.
        if reasoning_effort:
            effort = reasoning_effort
        if effort not in ("auto", "low", "medium", "high"):
            raise ValueError("effort must be auto, low, medium or high (rc.57)")
        # rc.57's only dollar limit. Because the home is fresh per trial it is
        # effectively a per-trial ceiling; it must stay above what max_tokens
        # can cost so the token cap, not the app, ends a long trial. See
        # GO_NO_GO.md for the arithmetic. Default install value is $10/day.
        amount = float(daily_usd_limit)
        if not (math.isfinite(amount) and 0.01 <= amount <= 1_000_000):
            raise ValueError("daily_usd_limit must be between 0.01 and 1,000,000")
        self.daily_usd_limit = round(amount, 2)
        # The study's per-session token cap (driver/README.md). 0 turns it off.
        self.max_tokens = int(max_tokens)
        self.effort = effort
        # Lemonade Stand's built-in fake model: no API calls, no cost. For
        # testing the plumbing only; results don't count.
        self.fake = str(fake).lower() in ("1", "true", "yes")
        # Every study session uses the frozen commit (repo README, rule 1).
        self.allow_unfrozen = str(allow_unfrozen).lower() in ("1", "true", "yes")
        self.server_port = int(server_port)
        # Headroom under the adapter's 3,600 s limit so usage.json is written.
        self.turn_timeout_sec = int(turn_timeout_sec)
        if self._version is None:
            self._version = f"{FROZEN_VERSION}+{FROZEN_COMMIT}"

    @staticmethod
    def name() -> str:
        return "lemonade-stand"

    # ------------------------------------------------------------------ install

    async def install(self, environment: BaseEnvironment) -> None:
        src = self._ls_env("LS_SOURCE_DIR")
        if not src or not (Path(src) / "app" / "server" / "stand.py").is_file():
            raise RuntimeError(
                "Set LS_SOURCE_DIR (--ae) to a Lemonade Stand checkout at commit "
                f"{FROZEN_COMMIT}; app/server/stand.py was not found there."
            )
        version_file = Path(src) / "VERSION"
        found = version_file.read_text().strip() if version_file.is_file() else "unknown"
        if found != FROZEN_VERSION:
            message = (
                f"LS_SOURCE_DIR is Lemonade Stand {found}, not the frozen "
                f"{FROZEN_VERSION} (commit {FROZEN_COMMIT}); see FROZEN_TAG.md."
            )
            if not self.allow_unfrozen:
                raise RuntimeError(
                    message + " Pass --ak allow_unfrozen:bool=true for tests only."
                )
            self.logger.warning(message + " Results will not count for the study.")

        await self.exec_as_root(
            environment,
            command=f"mkdir -p {LS_ROOT} && chmod 777 {LS_ROOT}",
        )
        # The backend is standard-library Python; just check the interpreter.
        await self.exec_as_agent(
            environment,
            command=(
                "python3 -c 'import sys; assert sys.version_info >= (3, 10), "
                "sys.version' && python3 -c 'import sqlite3'"
            ),
        )
        await self._upload_tree(environment, Path(src), LS_SRC)
        await environment.upload_file(HERE / "ls_driver.py", f"{LS_ROOT}/ls_driver.py")

        # Fresh home: the files folder pointed at /app, and the daily limit in
        # rc.57's own format (spend_limits.Settings.save_profile writes this).
        await self.exec_as_agent(
            environment,
            command=f"mkdir -p {LS_HOME} && ln -sfn {TASK_DIR} {LS_HOME}/files",
        )
        # ReplicationBench puts task data in /assets, outside the files folder.
        # rc.57's file tools reject symlinks that leave the folder and cap it
        # at 256 MiB, so copy the data in when it fits and log the outcome.
        # Shell-based agents read /assets directly.
        await self.exec_as_root(
            environment,
            command=(
                f"mkdir -p {LOG_DIR}; "
                "if [ -d /assets ] && [ -n \"$(ls -A /assets 2>/dev/null)\" ]; then "
                "kb=$(du -sk /assets | cut -f1); "
                f"if [ \"$kb\" -le {ASSETS_COPY_LIMIT_KB} ]; then "
                f"mkdir -p {TASK_DIR}/assets && cp -a /assets/. {TASK_DIR}/assets/ "
                f"&& chmod -R a+rX {TASK_DIR}/assets && echo \"assets copied: ${{kb}} KB\"; "
                "else echo \"assets NOT copied: ${kb} KB is over the limit\"; fi; "
                "else echo 'no /assets data'; fi "
                f"| tee {LOG_DIR}/assets.txt"
            ),
            timeout_sec=600,
        )
        await self._upload_config_text(
            environment,
            content=json.dumps({"version": 2, "daily_limit_usd": self.daily_usd_limit}),
            remote_path=f"{LS_HOME}/spend-limits.json",
            filename="spend-limits.json",
        )

    # --------------------------------------------------------------------- run

    @with_prompt_template
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        env = self._runtime_env()
        port = self.server_port

        # Only the server goes to the background, with every stream redirected.
        # Backgrounding "cd X && nohup ..." as one list leaves a subshell
        # holding the exec's stdout, so the exec (docker exec included) never
        # returns, and $! would be that subshell's pid, not the server's.
        await self.exec_as_agent(
            environment,
            command=(
                f"cd {LS_SERVER} || exit 1; "
                f"nohup python3 stand.py --port {port} "
                f"> {LOG_DIR}/server.log 2>&1 < /dev/null & "
                f"echo $! > {LS_ROOT}/server.pid"
            ),
            env=env,
        )

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(instruction)
            local_instr = fh.name
        try:
            await environment.upload_file(local_instr, f"{LS_ROOT}/instruction.md")
        finally:
            os.unlink(local_instr)

        driver = (
            f"python3 {LS_ROOT}/ls_driver.py "
            f"--base-url http://127.0.0.1:{port} "
            f"--home {LS_HOME} --server-dir {LS_SERVER} "
            f"--instruction-file {LS_ROOT}/instruction.md "
            f"--timeout {self.turn_timeout_sec} --log-dir {LOG_DIR} "
            f"--max-tokens {self.max_tokens} "
            f"--model {shlex.quote(self.model_name or '')} "
            f"--effort {shlex.quote(self.effort)} "
            f"{'--fake ' if self.fake else ''}"
            f"2>&1 | tee {LOG_DIR}/driver.txt"
        )
        try:
            await self.exec_as_agent(
                environment,
                command=driver,
                env=env,
                timeout_sec=self.turn_timeout_sec + 120,
            )
        finally:
            await environment.exec(
                command=f"kill $(cat {LS_ROOT}/server.pid) 2>/dev/null || true"
            )

    # ------------------------------------------------------- usage → context

    def populate_context_post_run(self, context: AgentContext) -> None:
        """Copy usage.json into Harbor's AgentContext so it appears in each
        trial's result.json alongside the other agents' numbers."""
        path = self.logs_dir / "usage.json"
        if not path.exists():
            self.logger.debug("No usage.json for this trial")
            return
        try:
            usage = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            self.logger.debug(f"Unreadable usage.json: {exc}")
            return

        context.n_input_tokens = usage.get("n_input_tokens")
        context.n_output_tokens = usage.get("n_output_tokens")
        context.n_cache_tokens = usage.get("n_cache_tokens")
        context.cost_usd = usage.get("cost_usd")
        if per_model := usage.get("per_model"):
            context.model_usage = {m: ModelUsage(**u) for m, u in per_model.items()}
        context.metadata = {
            **(context.metadata or {}),
            "lemonade_stand_version": usage.get("server_version"),
            "lemonade_stand_commit": FROZEN_COMMIT,
            "model_label": usage.get("model_label"),
            "bots": usage.get("bots"),
            "n_tool_calls": usage.get("n_tool_calls"),
            "final_status": usage.get("final_status"),
            "capped": usage.get("capped"),
            "daily_usd_limit": self.daily_usd_limit,
        }

    # ----------------------------------------------------------------- helpers

    def _ls_env(self, *names: str) -> str | None:
        """First non-empty value among ``names`` from Harbor's env sources
        (--ae values first, then the host). Not named ``_resolve_env``: that
        is a base-class method with a different return type."""
        for source in self._env_sources():
            for key in names:
                if source.get(key):
                    return source[key]
        return None

    def _runtime_env(self) -> dict[str, str]:
        env = {"LEMONADE_STAND_HOME": LS_HOME}
        if self.fake:
            env["LEMONADE_STAND_FAKE"] = "1"
            return env  # no keys in fake mode: nothing can be spent
        if self.model_name:
            try:
                env.update(self.model_connection.env)
            except Exception as exc:  # noqa: BLE001
                self.logger.debug(f"Harbor model connection unavailable: {exc}")
        for target, names in PROVIDER_KEYS.items():
            if value := self._ls_env(*names):
                env[target] = value
        return env

    async def _upload_tree(
        self, environment: BaseEnvironment, src: Path, dest: str
    ) -> None:
        """Tar the checkout without desktop/build folders, then unpack it."""
        def keep(info: tarfile.TarInfo):
            return None if any(p in SKIP_DIRS for p in Path(info.name).parts) else info

        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "ls.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(src, arcname="src", filter=keep)
            await environment.upload_file(archive, f"{LS_ROOT}/ls.tar.gz")
        await self.exec_as_agent(
            environment,
            command=(
                f"tar -xzf {LS_ROOT}/ls.tar.gz -C {Path(dest).parent} "
                f"&& rm {LS_ROOT}/ls.tar.gz"
            ),
        )
