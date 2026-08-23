# `.env` Reference

`.env` is the environment file consumed directly by Docker Compose (every
service in `docker-compose.yml` declares `env_file: - .env`) and, inside the
`the-architect` container, acts as the second-priority fallback source for
`lib/utils.py:get_config_value()` - checked only when a key is absent or
null in `config.json`. See [`config.json` Reference](config-json.md) for the
full three-tier priority order. `.env` is created locally by copying
`.env.example` and is git-ignored.

## How to configure it

1. Copy the template: `cp .env.example .env`.
2. At minimum, set `ADMIN_PASSWORD` - Compose refuses to start the
   `tool-installer` service without it (see below).
3. Fill in any other keys you want to override from their defaults (see the
   table below).
4. Run `docker compose up -d --build`. To verify values took effect, check
   the relevant service's logs (`docker compose logs <service>`) or, for
   `the-architect`-side settings, `scripts/logs.sh`.

## Settings reference

Every key present in `.env.example`, whether or not `docker-compose.yml`
currently wires it up:

| Key | Default (if unset) | Used for | Consumed by |
|---|---|---|---|
| `MODEL_NAME` | *(no default - required for a working boot; `.env.example` ships `qwen3.6:latest`)* | The Ollama model tag to pull and serve. Used both by the `ollama` service's boot entrypoint (`ollama pull ${MODEL_NAME}`) and its healthcheck, and - via the separate `config.json`/`.env` fallback chain inside the app container - as the `MODEL_NAME` config key agents use for chat completions. | `docker-compose.yml` `ollama` service; `lib/utils.py:get_config_value` inside `the-architect` |
| `LITELLM_PORT` | `4000` | Host port the LiteLLM proxy's `4000` container port is published on. | `docker-compose.yml` `litellm` service (`${LITELLM_PORT:-4000}:4000`) |
| `UI_PORT` | `8080` (Compose default) - **note:** `.env.example` ships `UI_PORT=3000` as a placeholder value, which does not match Compose's own fallback default; if you leave `.env`'s value as-is you'll get Open WebUI on port 3000, not 8080 | Host port Open WebUI's `8080` container port is published on. | `docker-compose.yml` `open-webui` service (`${UI_PORT:-8080}:8080`) |
| `WEBUI_SECRET_KEY` | `"change-this-secret"` (Compose fallback) | Open WebUI's session/auth signing secret. | `docker-compose.yml` `open-webui` service (`WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-change-this-secret}`) |
| `ENABLE_SIGNUP` | `false` (`.env.example` value) | Native Open WebUI setting controlling whether new users can self-register in the chat UI. **Not referenced via `${...}` substitution anywhere in `docker-compose.yml`**, but is passed straight through to the `open-webui` container via that service's `env_file: - .env`, and read directly by the Open WebUI image itself. | Open WebUI image directly (via `env_file` pass-through) |
| `OLLAMA_BASE_URL` | *(no Compose fallback - required)* | Base URL the `litellm` service uses to reach Ollama (`OLLAMA_API_BASE=${OLLAMA_BASE_URL}`, no `:-default`, so it must be set for LiteLLM to find Ollama). `.env.example` ships `http://ai-ollama:11434`. | `docker-compose.yml` `litellm` service |
| `LITELLM_BASE_URL` | `http://litellm:4000` (Compose fallback) | Base URL other services use to reach the LiteLLM proxy. Used both by `the-architect` (`OPENAI_API_BASE`) and `open-webui` (`OPENAI_API_BASE_URL`). `.env.example` ships `http://ai-litellm:4000/v1`. | `docker-compose.yml` `the-architect` and `open-webui` services |
| `NOTIFY_WEBHOOK_URL` | *(none - ships blank)* | Intended as a generic notification webhook target. **Not referenced anywhere in `docker-compose.yml`, and not read via `get_config_value()` anywhere in the Python codebase** (the actual webhook output channel, `ai_io/webhook.py`, uses its own `BOT_TOKEN`/`SERVER_ID`/`CHANNEL_ID` keys instead - see [Output Channels](../ai_io/output-channels.md)). This key currently has no effect. | - |
| `OLLAMA_PORT` | `11434` | Host port the Ollama server's `11434` container port is published on. | `docker-compose.yml` `ollama` service (`${OLLAMA_PORT:-11434}:11434`) |
| `LITELLM_MASTER_KEY` | `"sk-change-me"` (Compose fallback) | Dual role: (1) LiteLLM's own `general_settings.master_key` in `litellm-config.yaml` (via `os.environ/LITELLM_MASTER_KEY`), the key LiteLLM requires callers to authenticate with; (2) Open WebUI's `OPENAI_API_KEY`, since Open WebUI talks to LiteLLM as if it were an OpenAI-compatible endpoint and must present the same key LiteLLM expects. Must be the same value across both for Open WebUI's chat requests to succeed. | `docker-compose.yml` `litellm` and `open-webui` services |
| `ENABLE_RAG_WEB_SEARCH` | *(inert - see note)* | Intended to toggle Open WebUI's native web-search feature. **`docker-compose.yml` hardcodes `ENABLE_RAG_WEB_SEARCH=true` as a literal value** in the `open-webui` service's `environment:` block (not a `${...}` substitution), which always wins over whatever `.env` sets. This key currently has no effect. | Hardcoded in `docker-compose.yml` instead |
| `RAG_WEB_SEARCH_ENGINE` | *(inert - see note; also ships with no `=value` in `.env.example`, i.e. malformed/empty)* | Intended to select which search engine backs Open WebUI's native web search. Same hardcoding issue as `ENABLE_RAG_WEB_SEARCH` above - `docker-compose.yml` hardcodes `RAG_WEB_SEARCH_ENGINE=searxng` literally. This key currently has no effect. | Hardcoded in `docker-compose.yml` instead |
| `SEARXNG_QUERY_URL` | *(inert - see note)* | Intended to tell Open WebUI where to query SearXNG. Same hardcoding issue - `docker-compose.yml` hardcodes `SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>` literally. This key currently has no effect. | Hardcoded in `docker-compose.yml` instead |
| `SEARXNG_VERSION` | *(inert)* | Intended to pin the SearXNG image tag. `docker-compose.yml`'s `searxng` service hardcodes `image: searxng/searxng:latest` rather than referencing `${SEARXNG_VERSION}`. This key currently has no effect. | - |
| `SEARXNG_HOST` | *(none set by default; passed through if set)* | SearXNG's own listen-address setting, read by the SearXNG image itself from its container environment (passed through via the `searxng` service's `env_file: - .env`, not referenced by `docker-compose.yml` directly). See [SearXNG's own settings docs](https://docs.searxng.org/admin/settings/settings_server.html#settings-server). | SearXNG image directly (via `env_file` pass-through) |
| `SEARXNG_PORT` | `8080` (`.env.example` value; **not** the same as the host-side port mapping, which is hardcoded to `8081:8080` in `docker-compose.yml`) | SearXNG's own internal listen-port setting, read by the SearXNG image itself. Do not confuse with the host port (always `8081`, fixed in Compose). | SearXNG image directly (via `env_file` pass-through) |
| `ADMIN_EMAIL` | `"admin@example.com"` (Compose fallback) | Email for the Open WebUI account `scripts/install_tools.py` signs up (or signs into) and installs the custom Tools under. | `docker-compose.yml` `tool-installer` service |
| `ADMIN_PASSWORD` | **required - no default.** Compose uses `${ADMIN_PASSWORD:?set ADMIN_PASSWORD in .env}`, which makes `docker compose up` refuse to start at all if this is blank. | Password for the same admin account. | `docker-compose.yml` `tool-installer` service |
| `ADMIN_NAME` | `"Admin"` (Compose fallback) | Display name for the same admin account, only used if the account doesn't already exist. | `docker-compose.yml` `tool-installer` service |
| `OLLAMA_CONTEXT_LENGTH` | *(none set by default; passed through if set)* | Ollama's own context-window-size setting, read by the Ollama server image itself from its container environment (passed through via the `ollama` service's `env_file: - .env`, not referenced by `docker-compose.yml` directly). `.env.example` ships `65536`. | Ollama image directly (via `env_file` pass-through) |

## Related pages

- [`config.json` Reference](config-json.md) - the first-priority config
  source; several keys above (`MODEL_NAME`, `LITELLM_URL`/`LITELLM_BASE_URL`,
  etc.) exist in both files under related-but-not-identical names, since
  `.env` is Docker Compose's host-level config while `config.json` is the
  app-level config read inside `the-architect`.
- [Docker Compose Services](../operations/docker-compose-services.md) - how
  each of these values plugs into the service definitions as a whole.
