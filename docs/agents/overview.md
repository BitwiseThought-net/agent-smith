# Built-in Agents

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Explain the `agents/<name>.py` module contract: each file exposes a
  `get_agent(tools=None, model_name=None)` function returning a framework-
  agnostic `Agent` (from `ai_layer.orchestrator`), and the module filename
  (minus `.py`) is the `"name"` value `team.json` entries must match.
  Source: any `agents/*.py` file plus `main.py:load_agent_and_tools`'s
  `agent_path = os.path.join("agents", f"{agent_name}.py")` lookup.
- Note that `main.py:load_agent_and_tools` currently constructs the `Agent`
  directly via `_layer.Agent(...)` rather than calling each module's
  `get_agent()` — confirm this by re-reading `main.py` and the `agents/*.py`
  files together, and document the actual code path precisely (flag if
  `get_agent()` appears to be dead/unused code versus called from
  elsewhere, e.g. tests).
- Document each shipped agent persona in its own subsection: role, goal,
  backstory (summarized, not quoted verbatim), default model fallback
  (differs per agent — e.g. `analyst`/`auditor`/`auditor_safe`/`manager`/
  `writer` default to `llama3:latest`; `architect`/`coder`/`tester` default
  to `codellama:latest`; `librarian`/`researcher` default to
  `mistral:latest` — when no `MODEL_NAME` config or explicit argument is
  given), and whether `allow_knowledge_retrieval=True` is set:
  `agents/analyst.py`, `agents/architect.py`, `agents/auditor.py`,
  `agents/auditor_safe.py`, `agents/coder.py`, `agents/librarian.py`,
  `agents/manager.py`, `agents/researcher.py`, `agents/tester.py`,
  `agents/writer.py`.
- Call out the difference between `agents/auditor.py` and
  `agents/auditor_safe.py` specifically (both are "Cybersecurity Auditor"
  role but different goal/backstory focus — `auditor_safe` is scoped to
  verifying sandbox path compliance) so readers pick the right one in
  `team.json`.
- Document how to add a new custom agent (new `agents/<name>.py` file
  following the `get_agent()` contract, then reference it by name in
  `team.json`).
