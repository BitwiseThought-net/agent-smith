# Testing

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Document how to run the test suite locally: install
  `requirements-dev.txt`, then `pytest` (configured via `pytest.ini`:
  `testpaths = tests`, `python_files = test_*.py`, `addopts = -ra`).
  Include the exact coverage invocation used in CI, pulled from
  `.github/workflows/tests.yml`, so local runs can match CI's coverage
  report:
  ```
  pytest -q --cov=lib --cov=knowledge_manager --cov=tools --cov=loaders \
    --cov=main --cov=ai_io --cov-report=term-missing
  ```
- Document the `tests/conftest.py` fake-orchestrator fixture strategy:
  explain *why* it exists (avoids importing the real CrewAI/ChromaDB/
  LangChain dependency chain for unit tests that only need their own logic
  under test) and *what* it fakes (a lightweight stand-in
  `ai_layer.orchestrator` module installed into `sys.modules` before test
  imports, including a `_FakeKnowledgeSource` stand-in for CrewAI's
  knowledge source classes). Note its own docstring's guidance: tests
  needing real CrewAI behavior should be written as a separate,
  explicitly-marked integration suite instead.
- Document what each test module covers, one line each (read each file's
  top-level docstring/first few tests to summarize accurately rather than
  guessing from the filename alone): `test_lib_utils.py`,
  `test_github_repo_tool.py`, `test_main_wait_for_llm.py`,
  `test_main_persist_agent_knowledge.py`, `test_tools_legacy_wrappers.py`,
  `test_main_load_agent_and_tools.py`, `test_loaders.py`,
  `test_tools_file_write_safe.py`, `test_knowledge_manager.py`,
  `test_ai_io_discord_and_webhook.py`, `test_tools_terminal_safe.py`,
  `test_web_scraper_tool.py`, `test_main_run_mission.py`. Also document the
  root-level `test_discord.py` and clarify how/whether it differs from
  `tests/test_ai_io_discord_and_webhook.py` (note it lives outside
  `tests/` — confirm whether `pytest.ini`'s `testpaths = tests` setting
  means it's excluded from normal test runs, and document that explicitly).
- Document the coverage/badge pipeline referenced in
  `.github/workflows/tests.yml`'s inline comments: current coverage sits
  around 99%, with `main.py` intentionally slightly below 100% because of a
  few dead-code lines and the deliberately-untested infinite retry/idle
  loop (see `docs/operations/resilience-health.md`) — point to
  `tests/test_main_run_mission.py` for the specifics per the workflow
  comment, and link to `docs/ci-cd/github-actions.md` for the workflow
  itself rather than duplicating CI details here.
- Document the fast local incremental test loop backed by `pytest-testmon`
  (added to `requirements-dev.txt`): running `pytest --testmon` (or the
  `scripts/test-changed.sh` wrapper) only re-runs tests that are new/
  changed, or whose previously-covered application code changed since the
  last testmon run — explain the on-disk `.testmondata` map it keeps in the
  project root (git-ignored, see `.gitignore`) to make this decision, and
  that deleting `.testmondata` (or running without `--testmon`) forces a
  full run again. Make clear this is a *local dev speed* tool only: CI
  (`.github/workflows/tests.yml`) and a plain `pytest` invocation always run
  the full suite with coverage instrumentation, since testmon's job is fast
  iteration, not the correctness/coverage gate — cross-link to
  `docs/ci-cd/github-actions.md` rather than repeating why CI stays on the
  full run. Note testmon and `pytest-cov`'s `--cov` flags should not be
  combined in the same invocation (both instrument coverage internally);
  document them as two separate commands/workflows, not one merged one.
