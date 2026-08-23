# `team.json` Reference

`team.json` is the mission manifest: the ordered list of agents, their
tools, output channels, and tasks that `main.py:run_mission` executes on
each run. Its path is controlled by the `TEAM_CONFIG` config key (default
`team.json` - see [`config.json` Reference](config-json.md)). It's created
locally by copying `team.json.example`, and is git-ignored so each
deployment can run its own mission without checking in
deployment-specific instructions.

The repo also ships a `tasks.json` at the root with the identical schema
(and near-identical content, minus the multi-framework mix) to
`team.json.example`. **`tasks.json` is not read by any code in this repo** -
confirmed by searching every Python file for the string `tasks.json` and
finding no references. It appears to be a legacy or sample artifact left
over from an earlier iteration; treat it as reference material only, not as
something the application consumes.

## Schema

```json
{
  "mission_name": "Descriptive name (informational only, not read by any code)",
  "active_agents": [
    {
      "name": "researcher",
      "framework": "crewai",
      "tools": ["search_duckduckgo"],
      "output": ["discord"],
      "ledger_template": null,
      "tasks": [
        {
          "description": "What this agent should do.",
          "expected": "What a good result looks like."
        }
      ]
    }
  ]
}
```

| Field | Required | Description |
|---|---|---|
| `mission_name` (top-level) | No | Informational label only; not read by any code path. |
| `active_agents` (top-level) | Yes | Ordered array, processed in list order by `main.py:run_mission`. |
| `name` (per-agent) | Yes | Must match an `agents/<name>.py` module - this is how `main.py:load_agent_and_tools` locates `agents/{agent_name}.py` and imports `agents.{agent_name}`. See [Built-in Agents](../agents/overview.md). |
| `framework` (per-agent) | No | Overrides the global `AI_FRAMEWORK` config value for this agent only, selecting which `ai_layer/<framework>.py` adapter powers it. Defaults to the agent's own `.get("framework", get_config_value("AI_FRAMEWORK", "crewai"))` fallback if omitted. See [Supported Frameworks](../ai_layer/frameworks.md). |
| `tools` (per-agent) | No | Array of `tools/<name>.py` module names to attach to this agent - must be *agent tools*, not Open WebUI Tools. See [Agent Tools](../tools/agent-tools.md). Defaults to none if omitted. |
| `output` (per-agent) | No | A string or array of `ai_io/<name>.py` module names each completed task's result is broadcast to. `main.py` normalizes a bare string into a single-item list. Defaults to `["log"]` if omitted. See [Output Channels](../ai_io/output-channels.md). |
| `tasks` (per-agent) | No | Array of `{"description": ..., "expected": ...}` objects, run in order for that agent. If omitted (or empty), `main.py` synthesizes a single task from that agent's top-level `task_description`/`expected_output` keys, if present - otherwise it falls back to the generic defaults `"Execute pipeline tasks"` / `"Final response string"`. |
| `ledger_template` (per-agent) | No | Overrides the global `ledger_template` config value for this agent's knowledge ledger output only. See [`config.json` Reference](config-json.md) for the format. |

## Sequential hand-off between agents

Every task's result feeds into the next task's context. `main.py:run_mission`
accumulates a `running_context` string: as each task completes, its result
is appended to `running_context`, and that accumulated context is prefixed
onto the *next* task's `description` as `"HISTORICAL CONTEXT FROM PREVIOUS
TASKS:\n{running_context}"`. This is what makes a `team.json` mission behave
as a cooperative pipeline (researcher findings flow into the architect's
design, the architect's design flows into the coder's implementation, and so
on) rather than independent, isolated agent runs - there is no shared
database or memory store involved, just string concatenation carried
through the loop.

## The `librarian` special case

`main.py:run_mission` special-cases any agent whose `name` (case-insensitive)
is `"librarian"` in two ways:

1. **Before that agent's tasks run**, it calls
   `knowledge_manager.py:get_all_knowledge_sources()` to scan `/knowledge`
   and builds the `knowledge_sources` list passed into that step's
   `Crew(...)` call - no other agent triggers this scan.
2. **If `/knowledge` is empty**, it skips the LLM call entirely for that
   task and substitutes a canned result string
   (`"Librarian: Verification complete. The /knowledge directory is
   currently empty. Staged and ready for incoming asset uploads."`) instead
   of invoking `Crew.kickoff()`. This exists specifically to avoid stalling
   the pipeline on an empty RAG sync - some frameworks' knowledge-source
   handling doesn't behave well with an empty source list.

See [Knowledge Base & Ingestion](../knowledge/knowledge-base.md) for the
scan mechanics themselves.

## Interaction with CLI overrides

The CLI terminal-instruction override (see
[CLI / Terminal Usage](../operations/cli-usage.md)) modifies which
`team.json` task actually runs, without editing the file: a bare instruction
string overrides the first agent's first task description; `--agent <name>`
targets a specific agent's first task instead. Every other agent/task in
the mission still runs normally either way. See
[CLI / Terminal Usage](../operations/cli-usage.md) for the full, verified
behavior of each mode (including a possible bug in the `--agent` argument
parsing that's documented there).

## Example: hybrid multi-framework mission

`team.json.example` ships a 7-agent pipeline
(`librarian → researcher → architect → auditor_safe → coder → tester →
writer`) that mixes frameworks per-agent - `librarian`/`researcher`/`coder`/
`tester`/`writer` on `crewai`, `architect` on `langgraph`, `auditor_safe` on
`autogen` - to demonstrate that a single mission can span multiple
orchestration engines simultaneously. Note that `langgraph` and `autogen`
only ship as `.py.example` adapter files in this checkout (see
[Supported Frameworks](../ai_layer/frameworks.md)), so running this exact
example as-is requires enabling those adapters first; `tasks.json` at the
repo root is the same manifest with every agent set to `crewai` instead, as
a version that works without enabling the example adapters.
