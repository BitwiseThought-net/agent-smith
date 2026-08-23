# System Overview

**The Architect** is a local-first, multi-agent orchestration framework: a
Docker Compose stack that runs sequenced teams of LLM agents against a
locally-hosted model (via Ollama), routes every model call through an
OpenAI-compatible proxy (LiteLLM), and exposes both a chat UI (Open WebUI)
and a headless mission-runner (`main.py`) on top of it. Its defining feature
is the `ai_layer/` abstraction: agent orchestration logic is written once
against a framework-agnostic interface and can run on CrewAI, Microsoft
AutoGen, LangGraph, or Hugging Face smolagents interchangeably, selected by
a single config value. This page gives a conceptual map of how the pieces
fit together; each linked page below covers its area in full detail.

## The Docker Compose stack

Every service lives in `docker-compose.yml` at the repo root:

| Service | Role |
|---|---|
| `the-architect` | The agent runtime — runs `main.py`, executes missions defined in `team.json` |
| `ollama` | Local LLM inference server; pulls and serves the configured model plus the embedding model |
| `litellm` | OpenAI-compatible proxy in front of Ollama; the single endpoint every other component talks to for chat completions |
| `open-webui` | Chat UI, pointed at LiteLLM as its backend; also hosts the installed custom Tools |
| `chromadb` | Vector database backing the knowledge/RAG subsystem |
| `searxng` | Self-hosted meta search engine backing Open WebUI's native web search feature |
| `tool-installer` | One-shot container that installs the repo's custom Tools into Open WebUI on boot |
| `autoheal` | Watches container health status and restarts anything unhealthy |

Startup order is enforced through `depends_on` + `condition: service_healthy`
chains: `ollama` comes up first (pulling models), `litellm` and `chromadb`
wait on `ollama`/nothing respectively, `open-webui` waits on `litellm` +
`searxng` + `ollama`, `tool-installer` waits on `open-webui`, and
`the-architect` waits on `litellm` + `chromadb`. See
[Docker Compose Services](../operations/docker-compose-services.md) for the
full per-service settings breakdown (ports, volumes, environment variables,
health checks).

## Mission execution flow

A "mission" is one run of `main.py`. At a conceptual level:

1. `team.json` defines an ordered list of agents (`active_agents`), each with
   its own tasks, tools, output channels, and optionally its own execution
   framework.
2. `main.py` iterates that list in order. For each agent, it dynamically
   loads the agent's persona from `agents/<name>.py` and instantiates it
   through whichever framework adapter is named — either the agent's own
   `"framework"` key or the global `AI_FRAMEWORK` config default.
3. Each agent's task(s) run in turn. The text result of every completed task
   is appended to a running context string, which gets prefixed onto the
   *next* task's description — so later agents see a summary of everything
   earlier agents produced, without needing shared memory or a database.
4. After each task, its result is persisted to a knowledge ledger file and
   broadcast to every output channel listed in that agent's `"output"`
   array (e.g. `log`, `discord`).

See [The `ai_layer` Abstraction Engine](ai-layer-abstraction.md) for how the
framework-agnostic layer itself works,
[`team.json` Reference](../configuration/team-json.md) for the full mission
manifest schema, and
[Output Channels](../ai_io/output-channels.md) for the broadcast mechanism.

## Two distinct "tool" systems

The word "tool" refers to two unrelated things in this repo, and it's easy
to conflate them:

1. **Agent tools** (`tools/*.py` with a `get_tools()` function) — attached to
   `team.json` agents via their `"tools"` array, and invoked by the LLM
   during a mission. See [Agent Tools](../tools/agent-tools.md).
2. **Open WebUI Tools** (`tools/github_repo_tool.py`,
   `tools/web_scraper_tool.py`) — Open WebUI plugin-convention modules
   installed directly into the Open WebUI chat interface by the
   `tool-installer` service. They are available to a human chatting in Open
   WebUI, not to `team.json` agents. See
   [Open WebUI Tools](../tools/open-webui-tools.md).

## The knowledge/RAG subsystem

Files dropped into the `/knowledge` folder (mounted into the
`the-architect` container) are picked up by `knowledge_manager.py`, matched
to a per-extension loader module in `loaders/`, converted into a
framework-native knowledge source object, and made queryable by any agent
with `allow_knowledge_retrieval=True` set. The `librarian` agent is the
one that actively triggers this scan as part of a mission. See
[Knowledge Base & Ingestion](../knowledge/knowledge-base.md) and
[File Loaders](../knowledge/loaders.md) for the full mechanics.

## Project structure

Verified against the actual repository layout (not just README.md's
description — see the discrepancy note below):

```
.
├── agents/             # Agent persona modules (role, goal, backstory, model)
├── ai_io/              # Output-channel + identity plugin modules (log, discord, webhook)
├── ai_layer/           # Framework-agnostic abstraction layer (orchestrator + per-framework adapters)
├── badges/             # Generated test/coverage badge SVGs (CI-managed)
├── docs/               # This documentation set
├── knowledge/          # Raw ingestion assets for the RAG subsystem (host-mounted)
├── lib/                # Shared helpers: config resolution, logging, sandbox utilities
├── loaders/             # Per-file-extension knowledge source loaders
├── output/               # Sandboxed workspace for agent file writes / safe command execution
├── scripts/               # Operational shell/py scripts (logs, ingest, install tools, CI helpers)
├── tests/                  # pytest test suite
├── tools/                   # Agent tools + Open WebUI Tools (see above)
├── config.json.example       # Template for the git-ignored config.json
├── docker-compose.yml          # Full service stack definition
├── ingest.py                    # Manual knowledge-source sync entrypoint
├── knowledge_manager.py          # Scans /knowledge and dispatches to loaders/
├── litellm-config.yaml            # LiteLLM proxy model list and settings
├── main.py                         # Mission runner / CLI entrypoint
├── pytest.ini                       # pytest configuration
├── requirements.txt / requirements-dev.txt
├── tasks.json                        # Sample mission manifest (same shape as team.json)
├── team.json.example                  # Template for the git-ignored team.json
└── test_discord.py                     # Root-level test file (outside tests/, see Testing docs)
```

> **Discrepancy note:** README.md's "Project Structure Map" and its `ai_layer/`
> feature description list `ai_layer/autogen.py` and `ai_layer/langgraph.py`
> as if they ship active. In this checkout they only exist as
> `ai_layer/autogen.py.example` and `ai_layer/langgraph.py.example` — inert
> until renamed. See
> [The `ai_layer` Abstraction Engine](ai-layer-abstraction.md) for what that
> means in practice. Similarly, README.md's setup steps reference
> `plugins/discord_bot.py.example` and `plugins/discord_notifications.py.example`,
> but no `plugins/` directory exists anywhere in this checkout — see
> [Output Channels](../ai_io/output-channels.md) for the plugin mechanism
> that actually ships (`ai_io/discord.py`, `ai_io/webhook.py`) instead.
