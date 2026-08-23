# Open WebUI Tools

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

- Explain this is the second of the two distinct "tool" systems in the repo
  (see the project-wide note in `docs/LLM_INSTRUCTIONS.md`): these are Open WebUI
  plugin-style Python modules (a `Tools` class with a nested `Valves`
  pydantic model, and a docstring frontmatter with `title`/`author`/
  `description`/`version`), installed directly into the Open WebUI chat
  interface - not wired into `team.json` agents. Contrast briefly with
  `docs/tools/agent-tools.md` and link to it.
- Document `tools/github_repo_tool.py` fully:
  - What it does: given a public (or, with a token, private) GitHub repo
    URL, fetches the repo's default branch (or a `/tree/<branch>` URL),
    walks its file tree via the GitHub REST API, filters out binary/lockfile/
    vendor noise (list the `SKIP_DIRS` and `SKIP_EXTS` sets), downloads raw
    file contents up to configured limits, and returns a single text digest.
  - Its `Valves` (config settings, exposed in the Open WebUI tool settings
    UI): `GITHUB_TOKEN` (default `""`; raises the unauthenticated 60/hr
    GitHub API rate limit to 5000/hr and enables private-repo access),
    `MAX_FILES` (default `40`), `MAX_FILE_CHARS` (default `4000`),
    `MAX_TOTAL_CHARS` (default `30000`). Document each one's exact effect on
    the returned digest.
  - Its one public method, `read_github_repository(repo_url)`, its
    parameters, and its return format (repo header, filtered file tree,
    then `--- FILE: path ---` sections), including how it truncates
    individual files and stops early once `MAX_FILES`/`MAX_TOTAL_CHARS` is
    hit.
  - Note explicitly: it does **not** accept an uploaded zip file or local
    path - only a `github.com/owner/repo[...]` URL string.
- Document `tools/web_scraper_tool.py` fully:
  - What it does: fetches a URL and returns cleaned plain-text content
    (script/style/markup stripped via BeautifulSoup).
  - Its `Valves`: `MAX_CHARS` (default `8000`), `TIMEOUT` (default `15`
    seconds, request timeout). Read the full file to confirm exact
    truncation/error-handling behavior before writing this section.
  - Its public method `scrape_web_page(url)`, required `http(s)://` prefix
    validation, and error return format.
- Document the installation mechanism end-to-end:
  `scripts/install_tools.py`, run by the `tool-installer` Compose service
  (`docker-compose.yml`), which: waits for Open WebUI's `/health` endpoint,
  signs up (or signs in as a fallback) an admin account from
  `ADMIN_EMAIL`/`ADMIN_PASSWORD`/`ADMIN_NAME`, then POSTs every `.py` file
  in `/tools` (mounted read-only from the repo's `tools/` dir) to Open
  WebUI's Tools API - deriving each tool's id from its filename and its
  display name/description from the docstring frontmatter. Document that it
  is idempotent/non-destructive: it **skips** (never overwrites) a tool id
  that already exists in Open WebUI, and the documented way to push a source
  change is to delete the tool in Open WebUI first (or give it a new id)
  and re-run. Also document its own env vars: `OPEN_WEBUI_URL`,
  `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NAME`, `TOOLS_DIR` (default
  `/tools`).
