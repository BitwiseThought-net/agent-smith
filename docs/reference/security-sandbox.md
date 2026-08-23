# Security & Sandbox Model

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Summarize the "Safe-by-Design" model from README.md's "The Sandbox
  Environment" section as the intro/framing for this page, then back each
  claim with the actual enforcing code (don't just restate the README
  prose) per the "start with a summary" and "base every claim on the code"
  rules in `docs/LLM_INSTRUCTIONS.md`.
- Document `lib/utils.py:ensure_sandbox_dir(safe_dir)`: the shared helper
  that creates the configured sandbox directory if missing, used by both
  safe tools below, and returns a formatted error string on failure that
  callers short-circuit on.
- Document `tools/file_write_safe.py`'s enforcement precisely: rejects any
  `filename` containing `..` or starting with `/`, resolves writes to
  `os.path.join(SAFE_OUTPUT_DIR, filename)` (config key, default
  `/app/output`), and returns explicit `❌ Security Violation` /
  `✅ Success` strings rather than raising exceptions. Contrast with the
  **unrestricted** `tools/file_write.py` (native `FileWriterTool`, no path
  checks) - document clearly when a `team.json` author would choose one
  over the other, since picking the wrong one defeats the sandbox.
- Document `tools/terminal_safe.py`'s enforcement precisely: allow-lists
  commands starting with `python `, `pytest `, or `python3 ` (rejects
  everything else), separately rejects any command containing `..`, runs
  via `subprocess.run(..., cwd=SAFE_OUTPUT_DIR, timeout=TOOL_EXEC_TIMEOUT)`
  (config key, default `30` seconds). Contrast with the **unrestricted**
  `tools/terminal.py` (framework-native `EXECTool`, e.g.
  `NativeShellInterpreter` in `ai_layer/crewai.py`, which runs arbitrary
  shell commands with only a 60-second timeout and no allow-list) - flag
  this contrast prominently, since including `terminal.py` in a `team.json`
  agent's tools effectively grants unrestricted shell access inside the
  container.
- Document the `agents/auditor_safe.py` agent's role as a *process*-level
  control (an LLM agent whose goal/backstory is to review other agents'
  proposed code/paths for sandbox compliance) versus the *code*-level
  controls above - make clear this is advisory (LLM judgment) rather than a
  hard technical enforcement mechanism, unlike the tool-level checks.
- Document the container-level sandbox boundary: the `the-architect`
  service's `output/` volume mount in `docker-compose.yml` is the only
  writable host path exposed by default (`SAFE_OUTPUT_DIR=/app/output`
  maps to `./output` on the host), and `config_mount`/`plugins` are mounted
  read-only (`:ro`).
- Note the `CONTRIBUTING.md` "Security & Sandbox Constraints" section's
  requirements for anyone adding new tools/plugins (must use
  `get_config_value("SAFE_OUTPUT_DIR", ...)`, must allow-list commands by
  string prefix, must support `importlib.reload`) as guidance for
  maintainers extending the sandbox, distinct from the end-user-facing
  guarantees documented above.
