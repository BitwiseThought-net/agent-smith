# Quickstart

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Assume the reader has already completed `docs/getting-started/installation.md`.
  Walk through running a first mission using the shipped `team.json.example`
  (copied to `team.json`) as-is, describing what the default 7-agent pipeline
  (librarian → researcher → architect → auditor_safe → coder → tester →
  writer) does end-to-end. Source: `team.json.example`.
- Document the default no-argument run: `docker compose up -d` (or
  `docker restart the-architect`) causes `main.py`'s `run_mission()` to
  execute every agent/task listed in `team.json` in order. Explain the
  `running_context` hand-off between agents (each step's result is appended
  to `running_context` and passed into the next task's description) —
  see `main.py:run_mission`.
- Document the single global terminal-override quickstart example from
  `scripts/command.sh` / README.md "Terminal Command Interface" section:
  `docker exec -it the-architect python main.py "YOUR_INSTRUCTION_HERE"`.
  Cross-link to `docs/operations/cli-usage.md` for the full flag reference
  instead of duplicating it.
- Document where to look for output: `output/` directory (host-mounted, see
  `SAFE_OUTPUT_DIR` in `docs/configuration/config-json.md`), the `knowledge/`
  directory for persisted agent knowledge ledgers (`main.py:persist_agent_knowledge`),
  and Discord if configured (link to `docs/ai_io/output-channels.md`).
- Document opening Open WebUI (`http://localhost:${UI_PORT}`) and mention
  that the GitHub Repository Reader and Web Page Scraper tools
  (`tools/github_repo_tool.py`, `tools/web_scraper_tool.py`) are
  auto-installed there by the `tool-installer` service - link to
  `docs/tools/open-webui-tools.md`.
