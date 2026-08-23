# Installation

> Status: stub. See `docs/LLM_DOCS.prompt.md` for how to complete this page.

## TODO

- Document prerequisites: Docker & Docker Compose, NVIDIA Container Toolkit
  (for GPU acceleration, used by the `ollama` service's `deploy.resources`
  block in `docker-compose.yml`), and optionally Jenkins. Source: README.md
  "Prerequisites" section and `docker-compose.yml` `ollama` service.
- Document the clone + bootstrap steps: `git clone`, then copying
  `config.json.example` → `config.json`, `team.json.example` → `team.json`,
  and creating `plugins/discord_bot.py` / `plugins/discord_notifications.py`
  (note: these plugin source files are referenced by README.md but are not
  present in this repo checkout - flag this as a gap the reader needs to
  supply their own implementation for, based on the `ai_io/discord.py` /
  `ai_io/webhook.py` plugin pattern documented in
  `docs/ai_io/output-channels.md`).
- Document creating `.env` from `.env.example` and filling in required values
  (`ADMIN_PASSWORD` is enforced via `docker-compose.yml`'s
  `${ADMIN_PASSWORD:?set ADMIN_PASSWORD in .env}`; other keys have defaults).
  Link to `docs/configuration/env-file.md` for the full key reference instead
  of repeating it here.
- Document the `docker compose up -d --build` launch step and what a
  successful first boot looks like (service startup order via `depends_on`/
  `condition: service_healthy` in `docker-compose.yml`: ollama → litellm →
  chromadb/searxng → open-webui → tool-installer, and separately
  the-architect waits on litellm + chromadb).
- Document that on first boot, `ollama`'s entrypoint (see `docker-compose.yml`
  `ollama.entrypoint`) automatically pulls `${MODEL_NAME}` and
  `nomic-embed-text`, and that this can take a while depending on model size
  and network speed.
- Document how to verify the install worked: which ports to check
  (`UI_PORT` for Open WebUI, `LITELLM_PORT` for the LiteLLM proxy), and what
  log lines to look for from `docker logs -f the-architect` (see
  `lib/logger.py` emoji-prefixed log format and `main.py`'s
  `wait_for_llm` "Model {model} confirmed ready!" message).
- Link to `docs/getting-started/quickstart.md` for first-run usage once
  installed.
