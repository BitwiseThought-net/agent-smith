# Docker Compose Services

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

Document every service defined in `docker-compose.yml`, each as its own
subsection with: image/build source, purpose, key environment variables
(cross-link to `docs/configuration/env-file.md` for the full key
definitions rather than repeating them), exposed ports and their `.env`
overrides, volumes, `depends_on`/health-check relationships, and the
`autoheal: "true"` label where present (link to
`docs/operations/resilience-health.md` for what that label enables).

- `autoheal` - `willfarrell/autoheal` container watching Docker health
  status for any service labeled `autoheal: "true"`.
- `the-architect` - the core agent runtime (this repo, built from the local
  `Dockerfile`). Document its volumes precisely, including the commented-out
  `./knowledge:/app/knowledge` line vs. the active
  `/media/knowledge:/app/knowledge` line (flag this as something a reader
  needs to adjust for their own host layout), its `healthcheck` (heartbeat
  file staleness check, tied to `lib/utils.py:update_heartbeat`), and its
  `environment` block (`TEAM_CONFIG`, `PYTHONPATH`, `OPENAI_API_BASE`,
  `CHROMA_API_BASE`, `CREWAI_STORAGE_DIR`).
- `tool-installer` - one-shot `python:3.12-slim` container running
  `scripts/install_tools.py`; document its `restart: "no"` (one-shot) nature
  and its dependency on `open-webui` being healthy first. Link to
  `docs/tools/open-webui-tools.md` for what it actually installs.
- `open-webui` - the chat UI (`ghcr.io/open-webui/open-webui`); document how
  it's pointed at LiteLLM as an OpenAI-compatible backend
  (`OPENAI_API_BASE_URL`/`OPENAI_API_KEY`) and its built-in
  `ENABLE_RAG_WEB_SEARCH`/`SEARXNG_QUERY_URL` web-search integration (note
  in the doc that this is Open WebUI's *native* search feature, separate
  from the custom `web_scraper_tool.py`/`github_repo_tool.py` Tools - the
  compose file itself has a comment to this effect).
- `litellm` - the OpenAI-compatible proxy in front of Ollama
  (`ghcr.io/berriai/litellm`); document that it's driven by
  `litellm-config.yaml` (mounted read-only) rather than the commented-out
  inline `command` in the compose file - link to a `litellm-config.yaml`
  breakdown (add a TODO item to `docs/configuration/config-json.md` or
  create a new `docs/configuration/litellm-config.md` stub covering
  `model_list`, `litellm_settings.drop_params`, and
  `general_settings.master_key` if this page grows too large).
- `searxng` - self-hosted meta search engine backing Open WebUI's native web
  search; document the port mapping (`8081` host → `8080` container, i.e.
  distinct from `SEARXNG_PORT` in `.env.example`) and volume mounts.
- `chromadb` - vector DB backing the knowledge/RAG system; document
  `IS_PERSISTENT`/`ANONYMIZED_TELEMETRY` and its unusual Perl-based
  healthcheck.
- `ollama` - local LLM inference server; document its GPU
  `deploy.resources.reservations.devices` block (requires NVIDIA Container
  Toolkit - link to `docs/getting-started/installation.md`), its entrypoint
  auto-pulling `${MODEL_NAME}` and `nomic-embed-text` on boot, and its
  healthcheck (`ollama list | grep` for both models).
- Document the three named volumes (`ai_memory`, `ai_ollama_data`,
  `ai_open_webui_data`) and what each persists across container restarts.
