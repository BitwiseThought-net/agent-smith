# The `ai_layer` Abstraction Engine

> Status: stub. See `docs/LLM_DOCS.prompt.md` for how to complete this page.

## TODO

- Explain the purpose and design of `ai_layer/orchestrator.py`: it reads the
  `AI_FRAMEWORK` config value, dynamically imports `ai_layer.<framework>`,
  and re-exports a unified set of names (`Agent`, `Task`, `Crew`, `LLM`,
  `tool`, `Process`, `Knowledge`, `FileReadTool`, `FileWriterTool`,
  `EXECTool`, `DuckDuckGoSearchTool`) that the rest of the codebase imports
  from - never from a framework package directly. Source:
  `ai_layer/orchestrator.py`.
- Document the "Unified Interface Boundary" contract every adapter module
  must implement (`Agent`, `Task`, `Crew`, `LLM`, `tool`, plus the
  `Knowledge`/`DuckDuckGoSearchTool` stub classes) - summarize this from
  `CONTRIBUTING.md`'s "Abstraction Architecture Paradigm" and "Step-by-Step
  Factory Integration Protocol" sections, rewritten for a documentation
  audience rather than a contributor checklist.
- Document each shipped/example adapter module and its native backend, one
  subsection per framework:
  - `ai_layer/crewai.py` - wraps native CrewAI, `crewai_tools`
    (`FileReadTool`, `FileWriterTool`), and knowledge source classes; also
    defines the inline `NativeShellInterpreter` (`EXECTool`) and
    `NativeDuckDuckGoSearch` fallback tools.
  - `ai_layer/smolagents.py` - wraps Hugging Face `smolagents`
    (`CodeAgent` + `LiteLLMModel`), including the `AdapterTool` class that
    reflects a Python function's signature into a smolagents `Tool`.
  - `ai_layer/langgraph.py.example` - an example-only adapter (not active
    unless renamed to `.py`) built on `langgraph`/`langchain_openai`,
    including its `StateGraph`-based `Crew.kickoff()` implementation.
  - `ai_layer/autogen.py.example` - an example-only adapter (not active
    unless renamed to `.py`) built on Microsoft AutoGen's
    `AssistantAgent`/`UserProxyAgent`.
  For each, note what happens if a `team.json` agent requests a framework
  whose `.py` file doesn't exist (`main.py:load_agent_and_tools` logs an
  error and skips that agent rather than crashing the whole mission).
- Explain per-agent framework selection: `team.json` agents can set their own
  `"framework"` key to mix frameworks within a single mission (see
  README.md "Hybrid Multi-Framework Swarms" and the mixed
  crewai/langgraph/autogen/smolagents example in `team.json.example`), while
  agents without an explicit `"framework"` fall back to the global
  `AI_FRAMEWORK` config value.
- Document how to add a new framework adapter, condensed from
  `CONTRIBUTING.md`'s integration protocol, aimed at a reader who wants to
  extend the system (not just use it).
