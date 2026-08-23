# Documentation Build Instructions (LLM Prompt)

This `docs/` folder is a **stub documentation set** for "The Architect" repository.
Every `.md` file in this folder (other than this one) may be a stub containing a
`## TODO` section instead of finished, human-readable documentation. The file
is the prompt/instructions for the LLM (e.g. an agent, or you, Claude) tasked
with turning those stubs into real documentation, one file — or one TODO item
— at a time.

**This file itself is never a target for the workflow below** — it is the
instruction set, not a stub.

---

## How to use this file

You will typically be handed one stub `.md` file (or one TODO item within it)
and asked to complete it. Follow this process exactly:

1. **Read the TODO list** at the bottom of the target file under `## TODO`.
   Each item is a short pointer to the source of truth (a file path, config
   key, script, or feature) that needs to be documented — not the
   documentation itself.
2. **Read the referenced source code/config directly** from the repository
   before writing anything. Do not guess or invent behavior — base every
   claim on what the code actually does. If a TODO references a file that no
   longer exists or has changed shape, document the code as it exists today.
3. **Write the finished documentation** into the body of the file, above the
   `## TODO` section, following the "Documentation standards" below.
4. **Remove each TODO item you complete** from the `## TODO` list as you
   finish it. If you complete every item in the list, delete the entire
   `## TODO` section (including its heading) so the file reads as finished,
   polished documentation with no leftover scaffolding.
5. If you complete only some of the TODO items in a pass, leave the remaining
   (incomplete) items in place under `## TODO` and only remove the ones you
   finished.
6. **Create new stub files as needed.** If, while documenting a topic, you
   discover a related file, tool, agent, config key, or feature that deserves
   its own page (or realize a topic is too large for one page), create a new
   stub `.md` file in the appropriate `docs/` subfolder. Give it:
   - A one-line title and short intro stating what it will cover.
   - A `## TODO` section listing what needs to be documented in it, written
     with the same brevity and file-path-pointer style as the other stubs in
     this repo.
   Then link to it from the page that spawned it, and, if it doesn't fit any
   existing subfolder, add a short entry for it to `docs/README.md` (the
   documentation index) so it stays discoverable.

Never leave placeholder text like "TBD" or "coming soon" or "..." in the finished
documentation body — either fully document the item or leave it as an
explicit TODO item you did not get to.

---

## Documentation standards

Apply these standards to every page you write in this folder:

### 1. Organize documentation cleanly
- Use clear Markdown heading hierarchy (`#` page title, `##` major sections,
  `###` subsections). Don't skip levels.
- Prefer tables for structured, parallel data (config keys, flags, ports,
  environment variables). Prefer prose or numbered steps for procedures.
- Keep each page focused on the topic implied by its filename/location. If a
  page is accumulating unrelated content, split it into a new stub (see step
  6 above) rather than letting it sprawl.
- Cross-link related pages using relative Markdown links (e.g.
  `[team.json](../configuration/team-json.md)`) instead of duplicating
  content across pages.
- Use fenced code blocks with a language hint (` ```json `, ` ```bash `,
  ` ```python `, ` ```yaml `) for every command, config snippet, or code
  excerpt.

### 2. Start with a summary
Every page must open with a short (2-5 sentence) summary immediately after
the title, before any other section, that:
- States what the file/feature/component is.
- States where it fits in the overall system (The Architect: a hot-swappable,
  local-first multi-agent orchestration framework running on Ollama +
  LiteLLM + Open WebUI, with CrewAI/AutoGen/LangGraph/smolagents as
  interchangeable execution backends).
- Is understandable on its own, without requiring the reader to have already
  read other pages first.

### 3. Document all configuration settings completely
Whenever a page covers a config surface (`config.json`, `.env`, `team.json`,
tool `Valves`, plugin `SETTINGS`, etc.), include **every** key found in the
corresponding example/source file, each with:
- The exact key name.
- Its default value (pull this from the `.example` file, the code's
  `get_config_value(key, default)` call, or the `Field(default=...)`
  declaration — cite the real default, not an assumed one).
- What it controls / how it's used, in one or two sentences.
- Which file(s) actually read it (e.g. "read by `lib/utils.py:get_config_value`
  and consumed in `main.py`").

Do not omit a key because it seems minor — an incomplete settings table is
worse than a long one. If a page's TODO says "document config", treat that as
"document every key in that config surface," not a representative sample.

### 4. Document every CLI flag / option and how behavior differs
For any script or entrypoint that accepts CLI arguments or flags (currently:
`main.py`, and the `scripts/*.sh` wrappers around it), document:
- Every flag/positional argument, its syntax, and whether it's optional.
- How output/behavior differs between each mode (e.g. no-argument default
  run, a bare positional instruction string, vs. `--agent <name>` targeted
  routing) — walk through what actually happens in the code for each case,
  since these code paths are easy to misdescribe.
- A concrete, copy-pasteable example command for each mode.

### 5. Document setup steps and prerequisites
For any feature that depends on external setup (Docker, NVIDIA Container
Toolkit, an Ollama model pull, a Discord Developer Portal application, a
GitHub personal access token, Jenkins credentials, etc.), give an ordered,
numbered list of the exact steps a human needs to take outside this repo
before the feature will work. Note any values the user must copy back into
this repo's config (and exactly where — which file, which key).

### 6. Document configuration steps clearly
Beyond just listing settings, give the reader a clear "how do I actually turn
this on" path: which file to copy from `*.example`, which keys to fill in,
what order to do things in, and how to verify it worked (e.g. a log line to
look for, a health check, an API call to test).

---

## Source-of-truth notes for the whole project

Keep these project-wide facts in mind while writing any page, so descriptions
stay consistent across files:

- The stack is Docker Compose-based: `the-architect` (the agent runtime),
  `ollama`, `litellm`, `open-webui`, `chromadb`, `searxng`, `tool-installer`,
  and `autoheal`, all defined in `docker-compose.yml` at the repo root.
- The agent runtime (`main.py`) is framework-agnostic: it never imports
  `crewai`/`autogen`/`langgraph`/`smolagents` directly. It goes through
  `ai_layer/orchestrator.py`, which dynamically imports the adapter module
  named by the `AI_FRAMEWORK` config value (or a per-agent `"framework"`
  override in `team.json`).
- Central configuration resolution always follows this priority order,
  implemented in `lib/utils.py:get_config_value`: (1) `config.json` if it
  exists and has a non-null value for the key, (2) OS environment
  variable / `.env`, (3) the hardcoded default passed by the calling code.
  State this priority order on every page that discusses configuration.
- `config.json`, `team.json`, and any real `plugins/*.py` (other than
  `__init__.py` and `*.py.example` files) are git-ignored — see
  `gitignore-snippet.txt` — and must be created locally from the matching
  `*.example` file.
- "Tools" in this repo exist in two distinct systems that are easy to
  conflate — call this out explicitly wherever both are discussed:
  1. **Agent tools** (`tools/*.py`): Python modules with a `get_tools()`
     function, loaded by `main.py` and attached to CrewAI/AutoGen/etc.
     agents per the `"tools"` array in `team.json`.
  2. **Open WebUI Tools** (`tools/github_repo_tool.py`,
     `tools/web_scraper_tool.py`): these follow the Open WebUI `Tools`
     class + `Valves` plugin convention and are installed into the Open
     WebUI chat UI itself by `scripts/install_tools.py` /
     the `tool-installer` Compose service — they are not wired into
     `team.json` agents.
