# Supported Frameworks

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

This page duplicates/overlaps with `docs/architecture/ai-layer-abstraction.md`
— when completing both, decide a clean split (e.g. this page = practical
"how do I pick/switch a framework" guide; the architecture page = "how the
abstraction mechanism itself works") and cross-link rather than repeat.

- Document how to select a framework globally: set `AI_FRAMEWORK` in
  `config.json` (or `.env`) to one of `crewai`, `smolagents`, `langgraph`,
  `autogen` — the value must match a filename in `ai_layer/` (case-
  insensitive, per `ai_layer/orchestrator.py`'s `.lower()` call).
- Document how to select a framework per-agent by setting `"framework"` in
  a `team.json` agent entry, overriding the global default for that agent
  only — link to `docs/configuration/team-json.md`.
- For each framework, document: whether it ships active (`ai_layer/crewai.py`,
  `ai_layer/smolagents.py`) or only as an example requiring rename
  (`ai_layer/langgraph.py.example`, `ai_layer/autogen.py.example`), which
  Python packages it requires (cross-check against `requirements.txt` —
  note `langgraph`/`langchain_core`/`autogen`/`smolagents` packages are
  **not** currently listed in `requirements.txt`, only `langchain_openai`
  is — flag this as a prerequisite the reader must add manually if they
  enable those frameworks), and any framework-specific behavior worth
  knowing (e.g. smolagents' `CodeAgent` runs LLM-authored Python with
  `additional_authorized_imports=["os", "requests", "json", "time",
  "pytest"]`).
- Document the concrete steps to enable an example adapter (rename
  `ai_layer/langgraph.py.example` → `ai_layer/langgraph.py` or
  `ai_layer/autogen.py.example` → `ai_layer/autogen.py`, install the extra
  dependencies, then set `AI_FRAMEWORK` or a per-agent `"framework"` value
  to match).
