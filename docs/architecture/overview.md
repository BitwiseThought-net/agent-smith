# System Overview

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Describe the overall system at a high level: a Docker Compose stack
  running a local-first, multi-agent orchestration framework ("The
  Architect") on top of Ollama (local LLM inference) + LiteLLM (OpenAI-
  compatible proxy in front of Ollama) + Open WebUI (chat interface),
  with ChromaDB for RAG/knowledge storage and SearXNG for web search.
  Source: top of README.md and `docker-compose.yml` service list.
- Include a services diagram/table covering every service in
  `docker-compose.yml`: `the-architect`, `ollama`, `litellm`, `open-webui`,
  `chromadb`, `searxng`, `tool-installer`, `autoheal`, and how they depend
  on each other (`depends_on` + `condition: service_healthy` chains).
  Link to `docs/operations/docker-compose-services.md` for the full
  per-service settings breakdown rather than duplicating it here.
- Explain the mission execution flow end-to-end at a conceptual level:
  `team.json` defines an ordered list of agents and tasks → `main.py`
  iterates them → each agent is instantiated via the framework adapter
  named in its `"framework"` key (or the global `AI_FRAMEWORK` default) →
  results are chained via `running_context` → each result is persisted as a
  knowledge ledger and broadcast to its configured `"output"` channel(s).
  Link to `docs/ai_layer/frameworks.md`, `docs/configuration/team-json.md`,
  and `docs/ai_io/output-channels.md` for details instead of repeating them.
- Explain the two "tool" systems that exist side by side and how they
  differ (agent tools vs. Open WebUI tools) — see the project-wide note in
  `docs/README.md` — and link to `docs/tools/agent-tools.md` and
  `docs/tools/open-webui-tools.md`.
- Explain the knowledge/RAG subsystem at a conceptual level (`/knowledge`
  folder → per-extension loader in `loaders/` → ChromaDB via the active
  framework's knowledge sources) and link to
  `docs/knowledge/knowledge-base.md`.
- Reproduce (and keep in sync with) the "Project Structure Map" folder tree
  from README.md, verified against the actual repo layout.
