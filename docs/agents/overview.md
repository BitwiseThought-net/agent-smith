# Built-in Agents

Agent persona modules live in `agents/`, one file per agent, and are what a
`team.json` mission entry's `"name"` field refers to (see
[`team.json` Reference](../configuration/team-json.md)). Each module defines
a role, goal, backstory, and default model for that persona, framed as a
framework-agnostic `Agent` built through `ai_layer.orchestrator` (see
[The `ai_layer` Abstraction Engine](../architecture/ai-layer-abstraction.md)).

## The module contract - and an important runtime caveat

Every `agents/<name>.py` file exposes:

```python
def get_agent(tools=None, model_name=None):
    ...
    return Agent(role=..., goal=..., backstory=..., llm=local_llm, tools=tools or [], ...)
```

The filename (minus `.py`) is the exact string a `team.json` entry's
`"name"` field must match - `main.py:load_agent_and_tools` looks for
`agents/{agent_name}.py` on disk and errors out if it isn't found.

**However, tracing `main.py:load_agent_and_tools` closely shows it does
not call `get_agent()`.** It does:

```python
agent_module = importlib.import_module(f"agents.{agent_name}")

native_llm = _layer.LLM(...)  # built from the mission-wide llm_config, not this module

agent = _layer.Agent(
    role=agent_config.get("role", agent_name),
    goal=agent_config.get("task_description", "Execute mission assignments"),
    backstory=agent_config.get("backstory", f"Expert {agent_name} operative."),
    llm=native_llm,
    tools=all_tools
)
```

`agent_module` (the result of importing `agents.<name>`) is assigned but
never used again - the import only proves the file exists and is
syntactically valid Python. The actual `Agent` is built directly by
`main.py` from `team.json`'s own `"role"` / `"task_description"` /
`"backstory"` keys, falling back to generic strings (`role` = the raw agent
name, `backstory` = `"Expert {agent_name} operative."`) if `team.json`
doesn't set them - which the shipped `team.json.example` doesn't, for any
agent. **Practical effect:** with the example manifests as shipped, none of
the curated personas below (their specific role titles, goals, backstories,
or per-agent default models) are actually applied at runtime - every agent
runs with a generic role/backstory and the single mission-wide model set in
`main.py:run_mission`'s top-level `llm_config` (from the `MODEL_NAME`
config key). `get_agent()` and its per-agent model fallback are effectively
dead code on the current mission-execution path; they may be intended for a
different/future call site, or as a library API for programmatic use
outside `main.py`, but nothing in this repo currently invokes them.

To actually get one of these curated personas in a live mission, set that
agent's `"role"`, `"task_description"`, and `"backstory"` explicitly in
`team.json` to match what's described below.

## Shipped agents

| Agent | Role (per `get_agent()`, not currently applied - see above) | Default model fallback (only used if `get_agent()` were called) | `allow_knowledge_retrieval` |
|---|---|---|---|
| `agents/analyst.py` | Data Insights Analyst - extracts and interprets patterns from structured/unstructured data | `llama3:latest` | Yes |
| `agents/architect.py` | Solution Architect - designs scalable, modular system structures | `codellama:latest` | Yes |
| `agents/auditor.py` | Cybersecurity Auditor - reviews code/research for vulnerabilities and injection risks broadly (general OWASP-style review) | `llama3:latest` | No |
| `agents/auditor_safe.py` | Cybersecurity Auditor - same role title as `auditor`, but scoped specifically to verifying file operations stay inside `/app/output` and flagging absolute-path/`..` traversal attempts | `llama3:latest` | No |
| `agents/coder.py` | Senior Software Engineer - turns requirements/research into Python code | `codellama:latest` | No |
| `agents/librarian.py` | System Librarian - indexes and organizes local documentation | `mistral:latest` | Yes |
| `agents/manager.py` | Autonomous Project Manager - coordinates handoffs between agents | `llama3:latest` | Yes |
| `agents/researcher.py` | Documentation Specialist - retrieves/cross-references technical info from local docs and the web | `mistral:latest` | Yes |
| `agents/tester.py` | Quality Assurance Engineer - writes pytest suites, finds edge cases | `codellama:latest` | Yes |
| `agents/writer.py` | Technical Content Strategist - produces README/API/system documentation | `llama3:latest` | Yes |

All ten follow the same internal shape: resolve a target model (explicit
`model_name` argument → `MODEL_NAME` config value → the per-agent hardcoded
default above), build an `LLM` via `ai_layer.orchestrator.LLM` pointed at
`LITELLM_URL`/`OPENAI_API_KEY`/`TEMPERATURE` (config keys - see
[`config.json` Reference](../configuration/config-json.md)), then return an
`Agent` with `memory=True` and `verbose=True`.

### `auditor` vs. `auditor_safe`

Both share the "Cybersecurity Auditor" role title, which makes them easy to
confuse in a `team.json` `"name"` field. The difference is scope:
`auditor.py`'s goal/backstory is a general OWASP-style security review
("Zero Trust", injection risks, data leaks); `auditor_safe.py`'s is
narrower and specifically about verifying that other agents' file
operations stay confined to `/app/output` and don't attempt absolute paths
or `..` traversal. `team.json.example` uses `auditor_safe`. See
[Security & Sandbox Model](../reference/security-sandbox.md) for how that
relates to the actual code-level sandboxing tools do (the auditor agent
itself is an LLM-judgment control, not a technical enforcement mechanism).

## Adding a custom agent

1. Create `agents/<name>.py` following the `get_agent(tools=None,
   model_name=None)` contract shown above (copy an existing agent as a
   starting point).
2. Reference `<name>` in a `team.json` entry's `"name"` field.
3. Since `get_agent()` is not currently invoked by `main.py` (see the
   caveat above), also set that `team.json` entry's own `"role"`,
   `"task_description"`, and `"backstory"` keys directly if you want a
   persona distinct from the generic defaults - don't rely on the new
   module's `get_agent()` body taking effect on its own.
