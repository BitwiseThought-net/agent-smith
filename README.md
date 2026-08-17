# The Architect
<img width="2508" height="1212" alt="Screenshot 2026-08-03 194246" src="https://github.com/user-attachments/assets/3838fce4-4ca7-42b2-9a27-c77329c97f83" />

"Your life is the sum of a remainder of an unbalanced equation inherent to the programming of the matrix."

**The Architect** is a hardened, production-ready autonomous agent orchestration framework built on an enterprise-grade Abstract Factory Engine. By completely decoupling agent blueprints, custom tools, and RAG ingestion from the underlying platform runtime, the system gives you the power to swap your entire operational engine across **CrewAI, Microsoft AutoGen, LangGraph, or Hugging Face smolagents** using a single configuration line. This hot-swapping occurs in real-time without requiring code rewrites or container restarts. Operating on a secure, local-first LLM infrastructure, the framework eliminates external API costs and guarantees absolute data privacy during complex multi-agent operations.

---

[![Tests](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml/badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)
[![Coverage](https://raw.githubusercontent.com/BitwiseThought-net/the-architect/main/badges/coverage-badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)
[![Tests Passing](https://raw.githubusercontent.com/BitwiseThought-net/the-architect/main/badges/tests-badge.svg)](https://github.com/BitwiseThought-net/the-architect/actions/workflows/tests.yml)

---

## 🚀 Key Features

- **The `ai_layer` Abstraction Engine**: A framework-agnostic gateway (`ai_layer/orchestrator.py`) that completely decouples your agent definitions, custom tools, and RAG ingestion from the underlying runtime.
- **Hybrid Multi-Framework Swarms**: Mix and match agent orchestration frameworks inside the exact same team pipeline manifest. Assign a CrewAI loop to your researcher, a sandboxed Microsoft AutoGen engine to your coder, and a LangGraph state machine to your tester simultaneously.
- **Local-First LLM Architecture**: Seamless integration with **Ollama** and **LiteLLM** for full data privacy and no API costs.
- **Dynamic Configuration**: Modify system settings (`config.json`) and agent team definitions (`team.json`) in real-time without restarting containers.
- **Terminal Command Interface**: Pass explicit natural language instructions directly to the crew on execution kickoff via command-line string parameters, automatically bypassing static task manifests on demand. Supports both global initial-agent routing and explicit, targeted single-agent commands.
- **Modular Plugin System**: Self-contained Python plugins (e.g., Discord Bots, Notifications) that register tools and identity rules automatically.
- **System Librarian**: Automated RAG (Retrieval-Augmented Generation) indexing that synchronizes local documentation from the `/knowledge` folder into ChromaDB.
- **Resilient Folder Bootstrapping**: Built-in total safety checks across `agents/`, `knowledge/`, and `loaders/` folders. The machine gracefully bypasses empty directories or missing handlers without crashing your active execution pipelines with unhandled Python exceptions.
- **Hardened Execution**: Built-in retry logic, mission-level timeouts, and heartbeat monitoring for Docker auto-healing.
- **Sandboxed Execution**: Specialized tools for safe Python and Pytest execution within restricted directories.

---

## 📂 Project Structure Map

```ignore
.
├── ai_layer/              # Framework Agnostic Factory Package
│   ├── __init__.py        # Package token initializer
│   ├── orchestrator.py    # Runtime manager & routing hub
│   ├── crewai.py          # Native CrewAI engine connector
│   ├── autogen.py         # AutoGen conversational adapter
│   ├── langgraph.py       # LangGraph state machine wrapper
│   └── smolagents.py      # smolagents local execution node
├── agents/                # Unified Agent Persona Scripts (Framework Agnostic)
├── tools/                 # Framework Agnostic Custom Tool Libraries
├── loaders/               # Document processors for the System Librarian
├── plugins/               # Hot-swappable functional feature packages
├── knowledge/             # Raw ingestion assets (PDF, CSV, TXT, XML)
├── output/                # Secure host-mapped sandbox execution workspace
├── main.py                # Main workflow coordinator
└── docker-compose.yml     # Multi-container service matrix
```

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
   Copy the example files to create your active configuration:
   ```bash
   cp config.json.example config.json
   cp team.json.example team.json
   cp plugins/discord_bot.py.example plugins/discord_bot.py
   cp plugins/discord_notifications.py.example plugins/discord_notifications.py
   ```

3. **Launch the System:**
   ```bash
   docker compose up -d --build
   ```

---

## ⚙️ Configuration

### 1. `config.json` (System Settings)
Controls the global fallback behavior of the machine. Changes are applied on the next agent action.


| Key | Description | Default |
| :--- | :--- | :--- |
| `AI_FRAMEWORK` | Global fallback multi-agent driver if an agent does not explicitly define one. | `"crewai"` |
| `MODEL_NAME` | The primary LLM model used by agents. | `qwen3.6:latest` |
| `EMBEDDING_MODEL` | The model used for RAG/Knowledge indexing. | `nomic-embed-text` |
| `TEMPERATURE` | Controls LLM creativity (0.0 = deterministic). | `0.3` |
| `MAX_TOKENS` | Maximum response length per agent call. | `4096` |
| `MAX_RETRIES` | Number of times to retry a failed mission. | `3` |
| `MISSION_TIMEOUT_SECONDS`| Hard cutoff for total mission duration. | `1800` |
| `TOOL_EXEC_TIMEOUT` | Hard sandbox execution duration threshold inside the terminal runner. | `30` |
| `SAFE_OUTPUT_DIR` | Enforced target path limit where agents can manipulate files. | `"/app/output"` |
| `VERBOSE` | Toggles detailed agent "thought" logs. | `true` |

### 2. `team.json` (Agent Definitions)
Defines the framework layout, identities, and tasks of your active hybrid swarm pipeline manifest.
- **active_agents**: A list of agent objects configuration maps. Include the local `"framework"` target selection switch (`"crewai"`, `"autogen"`, `"langgraph"`, or `"smolagents"`) alongside the agent's `name`, `task_description`, and assigned `tools` array string keys.

### 3. `.env` (Infrastructure)
Used for fixed networking and boot-level security.
- `LITELLM_PORT`: Port for the LiteLLM proxy (default `4000`).
- `UI_PORT`: Port for the Open WebUI (default `3011`).
- `WEBUI_SECRET_KEY`: Security key for the WebUI session.
- `OLLAMA_BASE_URL` & `LITELLM_BASE_URL`: Inter-container internal bridge network addresses.

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

---

## 🔌 Plugins

The Architect supports "Hot-Swappable" Python plugins. Drop a `.py` file into the `/plugins` directory to enable new capabilities.

### Discord Bot (`plugins/discord_bot.py`)
Allows you to interact with agents via Slash Commands.
- **Identity Enforcement**: Automatically prepends `agent_name: ` to responses, ensuring strict identification protocol formatting.
- **Direct API Routing**: Bypasses loose webhooks to process interactive statements securely using a formal Bot Token.

### Discord Notifications (`plugins/discord_notifications.py`)
Provides a `send_notification` tool for outbound system alerts via Webhooks.
- Handles high-priority administrative pushes, general status changes, and final completed mission reports entirely out of a self-contained code module.

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

---

## 🔄 Resilience & Health

- **Heartbeat**: The system writes to `/tmp/heartbeat` every loop pass.
- **Autoheal**: Docker monitors the heartbeat; if the process stalls for more than 5 minutes, the container is automatically restarted.
- **Idle State**: If a mission reaches `MAX_RETRIES`, the container stays alive in an "Idle" state to allow log inspection and debugging.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code standards, framework abstraction protocols, and plugin development.

---

## 🛡️ License

This project is [licensed](LICENSE.md) under the **Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

*"Ergo, the concordance of thought is established."*
