# `config.json` Reference

`config.json` is the top-priority runtime configuration file for The
Architect. It's created locally by copying `config.json.example`, and it is
git-ignored (see `.gitignore` / `gitignore-snippet.txt`) so each deployment
keeps its own local copy with real secrets and settings out of version
control. Every setting it can hold is a fallback-driven value: the code
never requires a key to be present, and falls back to an environment
variable and then a hardcoded default if it's missing.

## Configuration priority order

Every setting in this repo is resolved by `lib/utils.py:get_config_value(key, default)`,
which always checks sources in this order:

1. **`config.json`** - if the file exists and has a non-null value for the
   key, that value wins.
2. **OS environment variable / `.env`** - via `os.getenv(key)`, checked only
   if `config.json` didn't provide the key.
3. **The hardcoded default** - passed by the calling code, used only if
   neither of the above provided a value.

Because `config.json` is re-read from disk on every call (rather than cached
at process start), edits take effect on the **next** agent action without
restarting the `the-architect` container - this is what README.md calls
"Dynamic Configuration."

## How to configure it

1. Copy the template: `cp config.json.example config.json`.
2. Edit the keys you want to override - see the full table below for every
   available key, its default, and what it controls. Any key you omit
   simply falls through to `.env` / the hardcoded default.
3. Save the file. No container restart is required - the next mission step
   that calls `get_config_value()` will pick up the change.
4. To verify a change took effect, watch `docker logs -f the-architect`
   (`scripts/logs.sh`) for the relevant behavior (e.g. a different model
   name in the `wait_for_llm` "Verifying ... is ready" log line, or a
   different agent model in its startup logs).

## Settings reference

| Key | Default | Used for | Read by |
|---|---|---|---|
| `PROJECT_NAME` | `"ai_architect"` (from `main.py`'s own fallback; `config.json.example` ships `"AI Architect"`) | Normalized (lowercased, spaces/hyphens → `_`) into a `project_id` at mission start; not currently used beyond that normalization. | `main.py:run_mission` |
| `AI_FRAMEWORK` | `"crewai"` | Selects which `ai_layer/<name>.py` adapter module powers agent execution globally. A `team.json` agent's own `"framework"` key overrides this per-agent. | `ai_layer/orchestrator.py`, `main.py:load_agent_and_tools` |
| `MODEL_NAME` | `"qwen3.6:latest"` in `main.py`'s top-level LLM config; individual `agents/<name>.py` modules have their own per-agent fallback if neither `config.json`/`.env` nor an explicit `model_name` argument is given - see the per-agent defaults table in [Built-in Agents](../agents/overview.md) | The Ollama model tag used for chat completions. Also used by `docker-compose.yml`'s `ollama` service entrypoint to decide which model to `ollama pull` on boot (via `${MODEL_NAME}` in `.env`, a separate but related setting - see [`.env` Reference](env-file.md)). | `main.py`, every `agents/*.py` module |
| `EMBEDDING_MODEL` | `"nomic-embed-text"` (`config.json.example` value; not read anywhere in the current Python code - see note below) | Intended to select the embedding model for RAG/knowledge indexing. | Not currently read via `get_config_value()` anywhere in the codebase - the embedding model is instead hardcoded as `nomic-embed-text` directly in `docker-compose.yml`'s `ollama` entrypoint. This key currently has no effect. |
| `TEMPERATURE` | `0.3` | LLM sampling temperature for every agent's `LLM` instance. | `main.py`, every `agents/*.py` module |
| `MAX_TOKENS` | `4096` | Max output tokens for the top-level mission LLM config built in `main.py`. (Individual `agents/*.py` modules hardcode `max_tokens=4096` directly rather than reading this key - so per-agent LLM instances are not actually affected by this setting; only the one built in `main.py` is.) | `main.py:run_mission` |
| `OPENAI_API_KEY` | `"sk-local-1234"` | The API key sent to LiteLLM by every agent's `LLM` client. Since LiteLLM proxies to local Ollama, this is a placeholder value rather than a real OpenAI key - it just needs to be non-empty and match what LiteLLM expects (see `LITELLM_MASTER_KEY` in [`.env` Reference](env-file.md)). | `main.py`, every `agents/*.py` module |
| `ANTHROPIC_API_KEY` | `"ollama"` (`config.json.example` value; not read anywhere in the current Python code) | Not currently read via `get_config_value()` anywhere in the codebase. This key currently has no effect. | - |
| `MAX_RETRIES` | `3` | Controls the "Idle State" failure behavior in `main.py:run_mission`: if a task raises an exception and `MAX_RETRIES <= 1`, the process enters an infinite heartbeat-only idle loop instead of exiting, to keep the container marked healthy for inspection rather than being restarted mid-failure. See [Resilience & Health Monitoring](../operations/resilience-health.md). | `main.py:run_mission` |
| `RETRY_DELAY_SECONDS` | `10` (`config.json.example` value; not read anywhere in the current Python code) | Not currently read via `get_config_value()` anywhere in the codebase. (Note: `scripts/install_tools.py` has an unrelated hardcoded `RETRY_DELAY_SECONDS = 3` Python constant of the same name used for its own Open WebUI readiness polling - that is a plain script constant, not this config key, and is not configurable via `config.json`.) This key currently has no effect. | - |
| `MISSION_TIMEOUT_SECONDS` | `1800` | Hard per-task execution timeout (via `signal.alarm`), enforced around every `Crew.kickoff()` call. | `main.py:run_mission` (via `lib/utils.py:set_mission_timeout`) |
| `TOOL_EXEC_TIMEOUT` | `30` | Timeout in seconds for commands run through the sandboxed `safe_terminal_exec` tool. | `tools/terminal_safe.py` |
| `OLLAMA_URL` | `"http://ai-ollama:11434"` (`config.json.example` value; not read anywhere in the current Python code) | Not currently read via `get_config_value()` anywhere in the codebase - agents talk to Ollama exclusively through LiteLLM (`LITELLM_URL`), never directly. This key currently has no effect. | - |
| `TEAM_CONFIG` | `"team.json"` | Path to the mission manifest file `main.py` loads at startup. | `main.py:run_mission` |
| `SAFE_OUTPUT_DIR` | `"/app/output"` | The sandbox root directory that `file_write_safe` and `safe_terminal_exec` confine all writes/command execution to. See [Security & Sandbox Model](../reference/security-sandbox.md). | `tools/file_write_safe.py`, `tools/terminal_safe.py` |
| `VERBOSE` | `true` | Passed straight through as the active framework's `Crew(verbose=...)` flag, controlling how much the underlying framework logs during execution. | `main.py:run_mission` |
| `LITELLM_URL` | `"http://ai-litellm:4000/v1"` | The base URL every agent's `LLM` client (and `main.py`'s `wait_for_llm` readiness check) talks to. | `main.py`, every `agents/*.py` module |
| `DISCORD_BOT_SETTINGS` | `{}` (nested object; `config.json.example` ships all four sub-keys empty/default) | Nested fallback source for the Discord output channel's bot token, guild ID, channel ID, and prefix toggle, used only when the plugin module's own in-file `SETTINGS` dict is left blank. Sub-keys: `BOT_TOKEN` (string, default `""`), `GUILD_ID` (string, default `""`), `TARGET_CHANNEL_ID` (string, default `""`), `RESPONSE_PREFIX_ENABLED` (bool, default `true`). See [Output Channels](../ai_io/output-channels.md) for exactly how `ai_io/discord.py` reads these. | `ai_io/discord.py` |
| `ledger_template` | A built-in multi-line text template (see `main.py:persist_agent_knowledge`'s `fallback_template`) | Format for the per-task knowledge ledger file written after every completed task. Can be a plain string (written as a `.txt` ledger) or a JSON object/dict (written as a `.json` ledger); either form supports `{agent_name}`, `{framework}`, `{timestamp}`, `{task_index}`, `{description}`, `{result}` placeholders. A `team.json` agent can override this globally-set value with its own per-agent `"ledger_template"` key. `config.json.example` ships a sample JSON-string override: `{"agent": "{agent_name}", "actions_logged": "{result}"}`. | `main.py:persist_agent_knowledge` |
| `KNOWLEDGE_DIR` | `"knowledge"` | Directory the knowledge ledger files (see `ledger_template` above) are written into after each task. **Not present in `config.json.example`** - undocumented there, but fully functional via the standard `config.json` → `.env` → default fallback chain if you choose to set it. | `main.py:persist_agent_knowledge` |

> **Note on unused keys:** `EMBEDDING_MODEL`, `ANTHROPIC_API_KEY`,
> `RETRY_DELAY_SECONDS`, and `OLLAMA_URL` all ship in `config.json.example`
> but are never read via `get_config_value()` anywhere in the current
> Python codebase (confirmed by searching every `get_config_value(...)` call
> site). Setting them in your own `config.json` will have no effect until
> the corresponding code is wired up - this is a discrepancy between the
> example file and the current implementation, not a documentation gap.

## Related pages

- [`.env` Reference](env-file.md) - the second-priority fallback source for
  every key above, plus Docker Compose-only settings that never go through
  `config.json` at all.
- [`team.json` Reference](team-json.md) - the mission manifest whose path is
  controlled by `TEAM_CONFIG`.
- [Output Channels](../ai_io/output-channels.md) - full detail on
  `DISCORD_BOT_SETTINGS` and the Discord/webhook plugin config precedence.
- [Resilience & Health Monitoring](../operations/resilience-health.md) -
  full detail on `MAX_RETRIES`'s idle-loop behavior and
  `MISSION_TIMEOUT_SECONDS`.
- [Security & Sandbox Model](../reference/security-sandbox.md) - full detail
  on `SAFE_OUTPUT_DIR` and `TOOL_EXEC_TIMEOUT`.
