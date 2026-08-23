# `.env` Reference

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Explain that `.env` is created by copying `.env.example`, is consumed by
  Docker Compose (`env_file: - .env` on most services in
  `docker-compose.yml`) and, per the config-priority note in
  `docs/README.md`, also acts as the second-priority fallback source for
  `get_config_value()` inside the `the-architect` container. Note it is
  git-ignored (`gitignore-snippet.txt`).
- Build a complete settings table from every key in `.env.example`,
  following the "Document all configuration settings completely" rule in
  `docs/README.md`, including keys that currently have no inline comment.
  At minimum cover: `MODEL_NAME`, `LITELLM_PORT`, `UI_PORT`,
  `WEBUI_SECRET_KEY`, `ENABLE_SIGNUP`, `OLLAMA_BASE_URL`,
  `LITELLM_BASE_URL`, `NOTIFY_WEBHOOK_URL`, `OLLAMA_PORT`,
  `LITELLM_MASTER_KEY`, `ENABLE_RAG_WEB_SEARCH`, `RAG_WEB_SEARCH_ENGINE`,
  `SEARXNG_QUERY_URL`, `SEARXNG_VERSION`, `SEARXNG_HOST`, `SEARXNG_PORT`,
  `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NAME`, `OLLAMA_CONTEXT_LENGTH`.
  For each, note which `docker-compose.yml` service(s) actually consume it
  (grep for `${KEY}` usage across the compose file) and its effective
  default if unset there (e.g. `UI_PORT` compose default is `8080` even
  though `.env.example`'s comment says `3000` — flag this discrepancy
  explicitly rather than silently picking one).
- Flag `ADMIN_PASSWORD` as required/non-optional: `docker-compose.yml`'s
  `tool-installer` service uses
  `${ADMIN_PASSWORD:?set ADMIN_PASSWORD in .env}`, which makes Compose
  refuse to start if it's blank. Document that `ADMIN_EMAIL`/`ADMIN_NAME`/
  `ADMIN_PASSWORD` become the Open WebUI account that
  `scripts/install_tools.py` signs up (or signs into) and under which the
  Tools get installed — link to `docs/tools/open-webui-tools.md`.
- Document the SearXNG-specific keys and link out to SearXNG's own docs
  (URLs already present as comments in `.env.example`) rather than
  re-documenting SearXNG itself.
- Note `LITELLM_MASTER_KEY` is used both by the `litellm` service itself
  (as its `general_settings.master_key` per `litellm-config.yaml`) and by
  `open-webui` (as its `OPENAI_API_KEY`, since Open WebUI talks to LiteLLM
  as if it were an OpenAI-compatible endpoint) — explain this dual role.
