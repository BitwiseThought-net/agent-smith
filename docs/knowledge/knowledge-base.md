# Knowledge Base & Ingestion

> Status: stub. See `docs/LLM_DOCS.prompt.md` for how to complete this page.

## TODO

- Explain the overall RAG pipeline: files dropped in `/knowledge` (host path
  configurable via the `docker-compose.yml` volume mount, currently
  `/media/knowledge:/app/knowledge` with a commented-out
  `./knowledge:/app/knowledge` alternative - note this discrepancy so
  readers know which host path actually feeds the container) are scanned by
  `knowledge_manager.py:get_all_knowledge_sources()`, converted into
  framework knowledge-source objects via per-extension loaders in
  `loaders/`, and made queryable by any agent with
  `allow_knowledge_retrieval=True` (see `docs/agents/overview.md`) through
  the active framework's `Crew(..., knowledge_sources=...)` mechanism -
  backed by ChromaDB (`docker-compose.yml` `chromadb` service).
- Document `knowledge_manager.py` in detail:
  - `validate_loaders(knowledge_files)`: checks a `loaders/<ext>.py` module
    exists for every file extension found in `/knowledge`; missing ones are
    logged as a warning and skipped (does not crash).
  - `get_all_knowledge_sources()`: lists `/knowledge` (skipping dotfiles and
    subdirectories), validates loaders, dynamically imports
    `loaders.<ext>` per file, and calls its `get_source(file)`. Document
    the safety behavior when `/knowledge` is missing or empty (logs and
    returns `[]` rather than erroring).
- Document `ingest.py` / `scripts/ingest.sh`: a standalone manual sync
  entrypoint (`docker exec -it <container> python ingest.py`, wrapped by
  `scripts/ingest.sh`) that calls the same `get_all_knowledge_sources()`
  and logs a summary - note from reading `ingest.py` closely whether it
  actually pushes data into ChromaDB itself or only lists/validates sources
  (the current implementation appears to only log which sources *would* be
  processed - confirm and document precisely, since this affects whether
  users need to rely on the `librarian` agent/mission run instead for actual
  indexing).
- Document the automatic librarian-driven sync path: when the `librarian`
  agent runs as part of a `team.json` mission, `main.py:run_mission` calls
  `get_all_knowledge_sources()` before kickoff and passes the results into
  that step's `Crew(knowledge_sources=...)` - link to
  `docs/configuration/team-json.md`'s librarian special-case notes.
- Document supported file types by listing every `loaders/*.py` module
  present, and link to `docs/knowledge/loaders.md` for the loader-by-loader
  breakdown rather than repeating it here.
- Document the setup step from README.md: "place technical documentation
  (.txt, .pdf, .csv, .json, .xml, etc.) into `/knowledge`", and note the
  Jenkinsfile's example of doing this via a Jenkins credential file copy
  (`FILE_1` → `knowledge/Python_Machine_Learning_Second_Edition.pdf`) as a
  CI/CD-driven alternative - link to `docs/ci-cd/jenkins.md`.
