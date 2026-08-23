# GitHub Actions Workflows

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Document `.github/workflows/tests.yml`: read the full file and describe
  its trigger conditions, the Python version(s) it runs against, how it
  installs dependencies (likely `requirements.txt` + `requirements-dev.txt`
  — confirm from the file), and what test/coverage commands it runs. Note
  its relationship to the `badges/tests-badge.svg` and
  `badges/coverage-badge.svg` files referenced in README.md's badge row
  (likely generated via `genbadge`, present in `requirements-dev.txt` —
  confirm how/where badge generation happens in the workflow).
- Document `.github/workflows/auto-pr.yml`: read the full file and describe
  its trigger and what it automates.
- Document `.github/workflows/pylint.yml.disabled`: note it is disabled
  (the `.disabled` suffix means GitHub Actions will not pick it up as a
  workflow), summarize what it would do if enabled, and note this as
  something a maintainer could opt into by renaming it to `.yml`.
- Document `.github/workflows/auto-delete-cache.vml`: note the unusual
  `.vml` extension (not `.yml`) — flag explicitly that GitHub Actions only
  recognizes `.yml`/`.yaml`, so this file is **not** currently an active
  workflow regardless of its content; summarize what it appears to intend
  to do and note this as a likely naming typo for a maintainer to fix.
- Cross-link to `docs/reference/testing.md` for what the test suite itself
  covers, rather than duplicating test details on this page.
