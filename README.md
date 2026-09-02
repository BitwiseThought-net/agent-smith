# The Architect
<img width="2508" height="1212" alt="Screenshot 2026-08-03 194246" src="https://github.com/user-attachments/assets/3838fce4-4ca7-42b2-9a27-c77329c97f83" />

"Your life is the sum of a remainder of an unbalanced equation inherent to the programming of the matrix."

**The Architect** is a hardened, production-ready autonomous agent orchestration framework built on an enterprise-grade Abstract Factory Engine. By completely decoupling agent blueprints, custom tools, and RAG ingestion from the underlying platform runtime, the system gives you the power to swap your entire operational engine across **CrewAI, Microsoft AutoGen, LangGraph, or Hugging Face smolagents** using a single configuration line. This hot-swapping occurs in real-time without requiring code rewrites or container restarts. Operating on a secure, local-first LLM infrastructure, the framework eliminates external API costs and guarantees absolute data privacy during complex multi-agent operations.

Or... if you just want a self-hosted LiteLLM OLLAMA instance that is easy to spin up. It's that too! (Just with features you can ignore.)

---

[![Tests](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml/badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)
[![Coverage](https://raw.githubusercontent.com/BitwiseThought-net/the-architect/main/badges/coverage-badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)
[![Tests Passing](https://raw.githubusercontent.com/BitwiseThought-net/the-architect/main/badges/tests-badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)

---

## 📖 Full Documentation

This README covers the essentials. For complete, code-verified reference
documentation - every config key and its default, every CLI flag, full
per-service Docker Compose settings, the agent/tool/output-channel systems,
and known discrepancies between this README and the current implementation -
see the [`docs/`](docs/README.md) folder, starting with
[`docs/README.md`](docs/README.md).

---

## 🚀 Key Features

- **The `ai_layer` Abstraction Engine**: A framework-agnostic gateway (`ai_layer/orchestrator.py`) that completely decouples your agent definitions, custom tools, and RAG ingestion from the underlying runtime.
- **Hybrid Multi-Framework Swarms**: Mix and match agent orchestration frameworks inside the exact same team pipeline manifest. Assign a CrewAI loop to your researcher, a sandboxed Microsoft AutoGen engine to your coder, and a LangGraph state machine to your tester simultaneously.
- **Local-First LLM Architecture**: Seamless integration with **Ollama** and **LiteLLM** for full data privacy and no API costs.
- **Dynamic Configuration**: Modify system settings (`config.json`) and agent team definitions (`team.json`) in real-time without restarting containers.
- **Terminal Command Interface**: Pass explicit natural language instructions directly to the crew on execution kickoff via command-line string parameters, automatically bypassing static task manifests on demand. Supports both global initial-agent routing and explicit, targeted single-agent commands.
- **Modular Output Channels**: Self-contained `ai_io/` plugins (e.g., a Discord bot integration) that register tools and identity rules automatically, and receive every completed task's result.
- **System Librarian**: Automated RAG (Retrieval-Augmented Generation) indexing that synchronizes local documentation from the `/knowledge` folder into ChromaDB.
- **Resilient Folder Bootstrapping**: Built-in total safety checks across `agents/`, `knowledge/`, and `loaders/` folders. The machine gracefully bypasses empty directories or missing handlers without crashing your active execution pipelines with unhandled Python exceptions.
- **Hardened Execution**: Mission-level timeouts and heartbeat monitoring for Docker auto-healing; a failed task does not retry itself, but `MAX_RETRIES` controls whether the container idles for inspection or moves on (see "Resilience & Health" below).
- **Sandboxed Execution**: Specialized tools for safe Python and Pytest execution within restricted directories.

---

## 📂 Project Structure Map

```ignore
.
├── ai_layer/                 # Framework Agnostic Factory Package
│   ├── __init__.py           # Package token initializer
│   ├── orchestrator.py       # Runtime manager & routing hub
│   ├── crewai.py             # Native CrewAI engine connector (active)
│   ├── smolagents.py         # smolagents local execution node (active)
│   ├── autogen.py.example    # AutoGen adapter - rename to .py to enable
│   └── langgraph.py.example  # LangGraph adapter - rename to .py to enable
├── ai_io/                    # Output-channel & identity plugins (log, discord, webhook)
├── agents/                   # Unified Agent Persona Scripts (Framework Agnostic)
├── tools/                    # Agent Tools + Open WebUI Tools (see docs/tools/)
├── loaders/                  # Document processors for the System Librarian
├── knowledge/                # Raw ingestion assets (PDF, CSV, TXT, XML)
├── output/                   # Secure host-mapped sandbox execution workspace
├── docs/                     # Full reference documentation
├── main.py                   # Main workflow coordinator
└── docker-compose.yml        # Multi-container service matrix
```

> **Note:** `autogen.py` and `langgraph.py` ship as `.py.example` files -
> they are not active until renamed, and their pip packages are not in
> `requirements.txt` by default. See
> [Supported Frameworks](docs/ai_layer/frameworks.md). There is no
> `plugins/` directory in this repo (see "🔌 Output Channels & Plugins"
> below for the mechanism that actually exists).

---

## 🛠 Installation

### Prerequisites
- **Docker & Docker Compose**
- **NVIDIA Container Toolkit** (for GPU acceleration)
- **Jenkins** (optional, for CI/CD deployment)

### Setup

1. **Clone the repository:**
   ```bash
   git clone github.com
   cd the-architect
   ```

2. **Initialize Configuration:**
   Copy the example files to create your active configuration (both are
   git-ignored so your local copies stay untracked):
   ```bash
   cp config.json.example config.json
   cp team.json.example team.json
   cp .env.example .env
   ```
   At minimum, set `ADMIN_PASSWORD` in `.env` - Docker Compose refuses to
   start without it (it's used to create the Open WebUI admin account that
   the Tools get installed under). See [`.env` Reference](docs/configuration/env-file.md)
   for every other key.

3. **Launch the System:**
   ```bash
   docker compose up -d --build
   ```
   First boot can take a while: `ollama` pulls `MODEL_NAME` and
   `nomic-embed-text` before it reports healthy, and every other service
   waits on that.

---

## ⚙️ Configuration

### 1. `config.json` (System Settings)
Controls the global fallback behavior of the machine. Changes are applied on the next agent action.


| Key | Description | Default |
| :--- | :--- | :--- |
| `AI_FRAMEWORK` | Global fallback multi-agent driver if an agent does not explicitly define one. | `"crewai"` |
| `MODEL_NAME` | The primary LLM model used by agents. | `qwen3.6:latest` |
| `TEMPERATURE` | Controls LLM creativity (0.0 = deterministic). | `0.3` |
| `MAX_TOKENS` | Maximum response length per agent call. | `4096` |
| `MAX_RETRIES` | Number of times to retry a failed mission. If `<= 1`, a failed task puts the container into an idle heartbeat loop instead of exiting (see "Resilience & Health" below). | `3` |
| `MISSION_TIMEOUT_SECONDS`| Hard cutoff for total mission duration. | `1800` |
| `TOOL_EXEC_TIMEOUT` | Hard sandbox execution duration threshold inside the terminal runner. | `30` |
| `SAFE_OUTPUT_DIR` | Enforced target path limit where agents can manipulate files. | `"/app/output"` |
| `VERBOSE` | Toggles detailed agent "thought" logs. | `true` |

> `config.json.example` also ships `EMBEDDING_MODEL`, `ANTHROPIC_API_KEY`,
> `RETRY_DELAY_SECONDS`, and `OLLAMA_URL` - none of these are currently read
> by any code path, so setting them has no effect. The embedding model is
> hardcoded to `nomic-embed-text` directly in `docker-compose.yml`'s
> `ollama` entrypoint instead. See
> [`config.json` Reference](docs/configuration/config-json.md) for the
> complete, verified key list (including a few undocumented-but-functional
> keys like `KNOWLEDGE_DIR` and `ledger_template`).

### 2. `team.json` (Agent Definitions)
Defines the framework layout, identities, and tasks of your active hybrid swarm pipeline manifest.
- **active_agents**: A list of agent objects configuration maps. Include the local `"framework"` target selection switch (`"crewai"`, `"autogen"`, `"langgraph"`, or `"smolagents"`) alongside the agent's `name`, `task_description`, and assigned `tools` array string keys.

### 3. `.env` (Infrastructure)
Used for fixed networking and boot-level security. Read directly by Docker
Compose, not by the Python app.
- `LITELLM_PORT`: Port for the LiteLLM proxy (default `4000`).
- `UI_PORT`: Port for the Open WebUI (`.env.example` ships `3000`; falls
  back to `8080` if unset entirely).
- `WEBUI_SECRET_KEY`: Security key for the WebUI session.
- `OLLAMA_BASE_URL` & `LITELLM_BASE_URL`: Inter-container internal bridge network addresses.
- `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NAME`: **`ADMIN_PASSWORD` is
  required** - Compose will refuse to start without it. This account is
  created (or signed into) in Open WebUI and used to install the custom
  Tools automatically on boot.

See [`.env` Reference](docs/configuration/env-file.md) for every key,
including a few (`ENABLE_RAG_WEB_SEARCH`, `RAG_WEB_SEARCH_ENGINE`,
`SEARXNG_QUERY_URL`) that are currently overridden by hardcoded values in
`docker-compose.yml` and have no effect when set here.

---

## 💻 Terminal Command Interface

You can bypass the static task files inside `team.json` and pass direct instructions to your agent crew straight from your shell console panel. 

The main orchestration engine intercepts the command string on the fly, applies it as a dynamic structural override on the targeted processing task, and cascades relevant context down the cross-framework sequential pipeline stack regardless of individual agent backend engines.

### 1. Global Initial Override (Legacy Fallback)
If no target agent flags are specified, the command string automatically intercepts and overrides the **very first agent** listed in your `team.json` manifest:
```bash
docker exec -it the-architect python main.py "YOUR_INSTRUCTION_HERE"
```

### 2. Targeted Agent Override (Flag Routing)
To bypass a task for one specific agent while keeping the baseline operational parameters intact for the remainder of your crew, inject the `--agent` parameter flag layout:
```bash
docker exec -it the-architect python main.py --agent <agent_name> "YOUR_TARGETED_INSTRUCTION_HERE"
```

#### Execution Routing Examples:
```bash
# Target only the Coder agent explicitly
docker exec -it the-architect python main.py --agent coder "Implement a strict token validation middleware loop inside auth.py"

# Target only the Researcher agent explicitly
docker exec -it the-architect python main.py --agent researcher "Find the latest CVE patches released for SQLite in 2026"
```

> ⚠️ **Known issue:** in the current `main.py`, the `--agent` detection
> compares `sys.argv` (a list) directly to the string `"--agent"`, which is
> never true. In practice this means the `--agent <name>` form above does
> **not** currently route to the named agent - it falls through to the
> Global Initial Override path instead (applied to the first agent in
> `team.json`, with the raw argument list embedded in the task
> description). If you need targeted routing today, set that agent's task
> directly in `team.json` instead of relying on `--agent`. See
> [CLI / Terminal Usage](docs/operations/cli-usage.md) for the fully
> verified behavior of every invocation mode.

---

## 🔌 Output Channels & Plugins

Hot-swappable functionality lives in `ai_io/`, not a separate `/plugins`
directory (there isn't one in this repo). Each `ai_io/<name>.py` module can
define a `register()` function (to add a tool and/or an identity-prefix rule
to every agent) and/or a `broadcast_status(message) -> bool` function (to
receive a copy of every completed task's result). A `team.json` agent opts
into a channel by listing it in that agent's `"output"` array - see
[`team.json` Reference](docs/configuration/team-json.md).

### `log` (default)
Prints the message to stdout. Every agent uses this unless `team.json`
specifies otherwise.

### `discord` (`ai_io/discord.py`) and `webhook` (`ai_io/webhook.py`)
Both post agent output to a Discord channel via the Discord Bot REST API
(not an actual webhook, despite the name) using a bot token, and both
register a `discord_interaction` tool available to every agent for the same
purpose. They differ only in where their config falls back to if the
in-file `SETTINGS` dict is left blank: `discord.py` falls back to
`config.json`'s nested `DISCORD_BOT_SETTINGS` object; `webhook.py` falls
back to flat top-level `BOT_TOKEN`/`SERVER_ID`/`CHANNEL_ID` config keys.
Setting `RESPONSE_PREFIX_ENABLED` (in `SETTINGS`, or
`DISCORD_BOT_SETTINGS.RESPONSE_PREFIX_ENABLED`) makes agents prepend
`agent_name: ` to their responses.

**Setup:** both modules embed the same numbered setup instructions in their
own `INFO["instructions"]` list - go to the Discord Developer Portal, create
an application and bot, enable the Message Content intent, generate an
OAuth2 invite URL with `bot` + `applications.commands` scopes and message
permissions, invite it to your server, then copy the bot token, server
(guild) ID, and channel ID into either the module's `SETTINGS` dict or
`config.json`'s `DISCORD_BOT_SETTINGS`.

### Adding a new channel
Create `ai_io/<name>.py` with a `broadcast_status(message: str) -> bool`
function (and optionally `register()`), then list `<name>` in a `team.json`
agent's `"output"` array. See
[Output Channels](docs/ai_io/output-channels.md) for full detail.

---

## 🔒 The Sandbox Environment

To ensure absolute system integrity during technical code execution steps, **The Architect** employs a layered, "Safe-by-Design" environment:
- **Restricted Writes**: The custom file tools strictly enforce that file manipulations are directed exclusively toward the `/app/output` directory.
- **Command Whitelisting**: The safe terminal runner only permits execution structures beginning with `python `, `pytest `, or `python3 ` to block arbitrary shell exploits.
- **Traversal Prevention**: Inputs containing malicious traversal characters (`../`) or absolute path indicators are instantly caught and rejected.

---

## 📚 Knowledge Management

Place any technical documentation (`.txt`, `.pdf`, `.csv`, `.json`, `.xml`, etc.) into the `/knowledge` directory.
- The **System Librarian** will automatically detect these files on kickoff.
- It uses the corresponding loader in `/loaders` to index the content.
- Framework-agnostic mapping abstractions automatically direct layout formats like XML or legacy document targets through optimized ingestion schemas (such as unified `Docling` layers).
- Agents with `allow_knowledge_retrieval=True` can then query this data during missions regardless of which active orchestration backend is running.
- **No archive support:** there is no `zip` (or similar archive) loader. A
  `.zip` dropped into `/knowledge` is skipped with a warning, not extracted
  - unpack any archive before placing its contents here. See
  [File Loaders](docs/knowledge/loaders.md) for the full supported-extension
  list.

---

## 🔄 Resilience & Health

- **Heartbeat**: The system writes to `/tmp/heartbeat` every loop pass.
- **Autoheal**: Docker monitors the heartbeat; if the process stalls for more than 5 minutes, the container is automatically restarted.
- **Idle State**: A failed task is **not** automatically retried. Instead,
  if a task raises an exception and `MAX_RETRIES` is `1` or less, the
  process enters an infinite heartbeat-only loop (keeping the container
  "healthy" so `autoheal` won't restart it) to allow log inspection before
  a human intervenes. If `MAX_RETRIES` is greater than `1` (the default,
  `3`), the mission instead just continues on to the next step without
  retrying the failed one.

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

For fast local iteration, `pytest-testmon` is included: `pytest --testmon`
(or `scripts/test-changed.sh`) only re-runs tests that are new/changed, or
whose previously-covered application code changed since the last run,
using an on-disk `.testmondata` map (git-ignored). This is a local dev
speed tool only - CI always runs the full suite with coverage
instrumentation. See [Testing](docs/reference/testing.md).

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code standards, framework abstraction protocols, and plugin development.

---

## 🛡️ License

This project is [licensed](LICENSE.md) under the **Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

*"Ergo, the concordance of thought is established."*
