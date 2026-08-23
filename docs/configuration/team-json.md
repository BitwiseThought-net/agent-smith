# `team.json` Reference

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Explain `team.json`'s role: it's the mission manifest read by
  `main.py:run_mission` (path controlled by the `TEAM_CONFIG` config key,
  default `team.json`), created by copying `team.json.example`, and
  git-ignored. Note the repo also ships a `tasks.json` at the root with the
  same schema/content as `team.json.example` (minus the multi-framework
  mix) — clarify its relationship to `team.json` (appears to be a sample/
  legacy artifact; confirm by checking whether anything in the codebase
  actually reads `tasks.json` before describing its purpose).
- Document the full schema, field by field, based on
  `team.json.example` and how `main.py:run_mission` consumes each field:
  - Top-level `mission_name` (descriptive only).
  - Top-level `active_agents`: ordered array, processed in list order.
  - Per-agent `name` (must match a `agents/<name>.py` module — see
    `docs/agents/overview.md`).
  - Per-agent `framework` (optional; overrides global `AI_FRAMEWORK` — link
    to `docs/ai_layer/frameworks.md`).
  - Per-agent `tools` (optional array of `tools/<name>.py` module names —
    link to `docs/tools/agent-tools.md`).
  - Per-agent `output` (string or array of `ai_io/<name>.py` module names;
    document that `main.py` normalizes a bare string into a single-item
    list, and defaults to `["log"]` if omitted — link to
    `docs/ai_io/output-channels.md`).
  - Per-agent `tasks` (array of `{description, expected}` objects); document
    the fallback when `tasks` is omitted (`main.py` synthesizes one task
    from the agent's top-level `task_description`/`expected_output` keys
    if present).
  - Per-agent `ledger_template` (optional; overrides the global
    `ledger_template` config value for that agent's knowledge ledger
    output — link to `docs/configuration/config-json.md`).
- Document the special-cased `librarian` agent name: `main.py:run_mission`
  checks `agent_name.lower() == "librarian"` to decide whether to scan
  `/knowledge` before kickoff, and separately short-circuits the whole
  crew-execution step (skipping LLM calls entirely) with a canned response
  if the librarian runs and `/knowledge` is empty. Explain why: to avoid
  stalling the pipeline on an empty RAG sync.
- Document the `running_context` hand-off mechanism between sequential
  tasks/agents (each completed task's result string is appended to a
  shared `running_context` and prefixed onto the next task's description as
  "HISTORICAL CONTEXT FROM PREVIOUS TASKS") — this is what makes the
  pipeline sequential/cooperative rather than independent per-agent runs.
- Document how the CLI terminal-instruction override (`docs/operations/cli-usage.md`)
  interacts with `team.json`: a bare instruction string replaces the first
  agent/task's `description`; `--agent <name>` targets a specific agent's
  first task instead. Link there instead of duplicating flag details.
