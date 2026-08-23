# File Loaders (`loaders/`)

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Document the loader module contract: each `loaders/<ext>.py` file exposes
  a `get_source(file_path)` function returning a framework-agnostic
  `Knowledge.*` source object (from `ai_layer.orchestrator.Knowledge`,
  which is backed by CrewAI's knowledge source classes in
  `ai_layer/crewai.py`), or `None` if the file can't be loaded. The
  extension in the filename (minus `.py`) is what
  `knowledge_manager.py` matches against each `/knowledge` file's
  extension.
- Enumerate every shipped loader and which `Knowledge.*` class it maps to —
  read each file in `loaders/` individually rather than assuming a pattern,
  since they are not all consistent (e.g. `loaders/py.py`'s own docstring
  says it maps to a "JSON processor" for `.py` files, and `loaders/pdf.py`
  references a `PDFKnowledgeSource` name that is not imported anywhere in
  the file - call out this apparent bug explicitly rather than documenting
  it as working, since it would raise `NameError` at runtime):
  `csv.py`, `docx.py`, `html.py`, `jpg.py`, `js.py`, `json.py`, `log.py`,
  `md.py`, `ods.py`, `pdf.py`, `png.py`, `pptx.py`, `py.py`, `soap.py`,
  `tex.py`, `tsv.py`, `txt.py`, `xlsx.py`, `xml.py`, `yaml.py`.
- Document the `Knowledge` class itself
  (`ai_layer/crewai.py:Knowledge` - `CSV`, `Docling`, `JSON`, `Excel`,
  `TextFile`, `XML` members) and note that non-CrewAI framework adapters
  (`smolagents`, and the `.example` langgraph/autogen adapters) only provide
  placeholder/stub versions of this class, so knowledge ingestion is
  effectively CrewAI-specific today - cross-link to
  `docs/ai_layer/frameworks.md`.
- Document that an unsupported extension (no matching `loaders/<ext>.py`)
  causes that file to be silently skipped with a warning, per
  `knowledge_manager.py:validate_loaders`, and there is currently **no**
  `loaders/zip.py` - archives placed in `/knowledge` are not extracted or
  read.
- Document how to add a new loader: create `loaders/<ext>.py` with a
  `get_source(file_path)` function returning an appropriate
  `Knowledge.*` source (or a new native knowledge-source class added to the
  active framework adapter first, if none of the existing `Knowledge.*`
  members fit).
