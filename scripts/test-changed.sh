#!/bin/bash
# Fast local test loop: only runs tests that are new/modified, or that
# exercise application code that changed since the last run of this script.
#
# Backed by pytest-testmon, which keeps a small on-disk map (.testmondata,
# in the project root, git-ignored) from each test to the exact lines of
# code it executed. On each run it diffs the current source against that
# map and skips any test whose covered lines (and whose own test source)
# are unchanged.
#
# First run (or any run after deleting .testmondata) has nothing to compare
# against, so it runs the full suite once to build the map; every run after
# that is incremental. Delete .testmondata to force a full run again.
#
# This is a local dev convenience only - CI (`.github/workflows/tests.yml`)
# and a plain `pytest` invocation always run the full suite with coverage,
# since testmon's job is fast iteration, not the correctness/coverage gate.
#
# Usage:
#   scripts/test-changed.sh            # incremental run
#   scripts/test-changed.sh -k foo     # extra pytest args are passed through
set -euo pipefail
cd "$(dirname "$0")/.."
pytest --testmon "$@"
