# `config.json` Reference

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Explain that `config.json` is the top-priority runtime config source (see
  the config-priority note in `docs/README.md`), is created by copying
  `config.json.example`, and is git-ignored (`gitignore-snippet.txt`) so
  each deployment keeps its own local copy. Explain it is re-read on every
  `get_config_value()` call (`lib/utils.py`), so edits take effect on the
  *next* agent action without a container restart (per README.md "Dynamic
  Configuration").
- Build a complete settings table from every key in `config.json.example`,
  following the "Document all configuration settings completely" rule in
  `docs/README.md`. At minimum cover: `PROJECT_NAME`, `AI_FRAMEWORK`,
  `MODEL_NAME`, `EMBEDDING_MODEL`, `TEMPERATURE`, `MAX_TOKENS`,
  `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MAX_RETRIES`,
  `RETRY_DELAY_SECONDS`, `MISSION_TIMEOUT_SECONDS`, `TOOL_EXEC_TIMEOUT`,
  `OLLAMA_URL`, `TEAM_CONFIG`, `SAFE_OUTPUT_DIR`, `VERBOSE`, `LITELLM_URL`,
  `DISCORD_BOT_SETTINGS` (nested object: `BOT_TOKEN`, `GUILD_ID`,
  `TARGET_CHANNEL_ID`, `RESPONSE_PREFIX_ENABLED`), and `ledger_template`.
  For each, cross-check against every call site that reads it via
  `get_config_value(key, default)` across `main.py`, `lib/utils.py`,
  `ai_layer/*.py`, `agents/*.py`, `tools/*.py`, and `ai_io/*.py` so the
  documented default matches the code's fallback default, not just the
  example file's value (note any mismatches you find, e.g. some
  `agents/*.py` files default `MODEL_NAME` differently per-agent —
  e.g. `llama3:latest` vs `codellama:latest` vs `mistral:latest` — when
  `config.json` doesn't set it and no `model_name` argument is passed).
- Note that `MAX_RETRIES` also has a special runtime effect beyond "how many
  times to retry a failed mission": in `main.py:run_mission`, if a task
  raises an exception and `MAX_RETRIES <= 1`, the process enters an infinite
  idle heartbeat loop (`while True: update_heartbeat(); time.sleep(60)`)
  instead of exiting — document this "Idle State" behavior and link to
  `docs/operations/resilience-health.md`.
- Document `ledger_template`: used by `main.py:persist_agent_knowledge`, can
  be a plain string (written as a `.txt` ledger file with
  `{agent_name}`/`{framework}`/`{timestamp}`/`{task_index}`/`{description}`/
  `{result}` placeholders) or a dict (written as a `.json` ledger with the
  same placeholders applied per-value). Also note `team.json` agents can
  override this per-agent via their own `"ledger_template"` key.
- Note the relationship between `TEAM_CONFIG` (defaults to `team.json`) and
  the actual `team.json`/`tasks.json` files present in the repo — link to
  `docs/configuration/team-json.md` for the mission-file schema itself
  rather than duplicating it here.
