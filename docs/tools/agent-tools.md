# Agent Tools (`tools/` + `team.json`)

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Explain this is one of the two distinct "tool" systems in the repo (see
  the project-wide note in `docs/LLM_INSTRUCTIONS.md`) - these are Python modules
  loaded by `main.py:load_agent_and_tools` and attached to an agent based on
  its `"tools"` array in `team.json`. Contrast briefly with
  `docs/tools/open-webui-tools.md` and link to it.
- Document the module contract: each `tools/<name>.py` file exposes a
  `get_tools()` function returning a list of framework-native tool objects/
  callables; the filename (minus `.py`) is the string used in `team.json`'s
  `"tools"` array. Source: `main.py:load_agent_and_tools`'s
  `importlib.import_module(f"tools.{t_name}")` / `tool_module.get_tools()`
  call, and any `tools/*.py` file.
- Document each shipped agent tool, what it does, and what backing
  framework primitive it wraps:
  - `tools/file_read.py` → `ai_layer.orchestrator.FileReadTool`.
  - `tools/file_write.py` → `ai_layer.orchestrator.FileWriterTool`
    (unrestricted write location - contrast with `file_write_safe` below).
  - `tools/file_write_safe.py` → custom `@tool("file_write_safe")` function;
    document its sandboxing behavior (writes only under
    `SAFE_OUTPUT_DIR`, blocks `..` and absolute paths) and link to
    `docs/reference/security-sandbox.md` for the full security model.
  - `tools/terminal.py` → `ai_layer.orchestrator.EXECTool` (framework's
    native/unrestricted shell execution tool, when the active adapter
    provides one).
  - `tools/terminal_safe.py` → custom `@tool("safe_terminal_exec")`
    function; document its sandboxing behavior (command must start with
    `python `, `pytest `, or `python3 `, blocks `..`, runs with
    `cwd=SAFE_OUTPUT_DIR` and a `TOOL_EXEC_TIMEOUT`-second timeout) and
    link to `docs/reference/security-sandbox.md`.
  - `tools/search_duckduckgo.py` → `ai_layer.orchestrator.DuckDuckGoSearchTool`.
  - `tools/github_repo_tool.py` and `tools/web_scraper_tool.py` - note these
    two are *dual-purpose*: they also implement the Open WebUI `Tools`
    class convention and get auto-installed into Open WebUI. Cover their
    `get_tools()`-style usage (if any) here, but put the full Valves/config
    breakdown in `docs/tools/open-webui-tools.md` and link to it rather
    than duplicating.
- Document that a tool load failure is non-fatal: `main.py` catches
  exceptions per-tool and logs a warning (`log_warn(f"Failed to load tool
  {t_name}: {e}")`) rather than aborting the whole agent/mission.
