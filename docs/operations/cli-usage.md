# CLI / Terminal Usage

> Status: stub. See `docs/LLM_INSTRUCTIONS.md` for how to complete this page.

## TODO

Follow the "Document every CLI flag / option" rule in `docs/LLM_INSTRUCTIONS.md`
closely for this page - read `main.py:run_mission`'s argument parsing at the
top of the function very carefully, since the different invocation modes are
easy to misdescribe.

- Document Mode 1 - no arguments: `docker exec -it the-architect python
  main.py` (or letting the container's default `CMD` run it). Every agent in
  `team.json` runs its normal `tasks` in order; no override occurs.
- Document Mode 2 - global/legacy override: a bare instruction string,
  e.g. `docker exec -it the-architect python main.py "YOUR_INSTRUCTION_HERE"`.
  Precisely document which agent/task actually receives the override per
  the code (`is_legacy_match` condition in `main.py:run_mission`): it
  applies only to the very first agent in `active_agents`, and only to that
  agent's first task (`sub_idx == 0`); every other agent/task in the
  mission still runs normally afterward using `expected_output` reset to a
  generic "terminal request output summary" string.
- Document Mode 3 - targeted agent override:
  `docker exec -it the-architect python main.py --agent <agent_name>
  "YOUR_TARGETED_INSTRUCTION_HERE"`. Document precisely how targeting
  resolves (`is_explicit_match` condition): it matches the *first* task
  (`sub_idx == 0`) of the agent whose `name` (case-insensitive) equals
  `<agent_name>`, anywhere in `active_agents`, not just the first agent in
  the list - every other agent/task still runs normally.
- **Verify the argv parsing bug before documenting exact syntax**: re-read
  `main.py:run_mission`'s `if sys.argv == "--agent" and len(sys.argv) > 3`
  line character-by-character - `sys.argv` is a list, so comparing it
  directly to the string `"--agent"` and passing the whole list into
  `.lower()`/`.strip()` looks like it cannot behave as the README's examples
  describe. Confirm by tracing the actual code path (and/or running it) and
  document the CLI's *real, current* behavior rather than the intended
  behavior from README.md - call out the discrepancy explicitly if the
  `--agent` flag does not work as documented in README.md, since this is a
  correctness-critical detail for anyone trying to use targeted routing.
- Include the concrete example commands from README.md's "Terminal Command
  Interface" section and `scripts/command.sh` (which contains the same
  examples as shell comments) once the above is verified against real
  behavior - do not simply copy them without checking.
- Document `scripts/logs.sh` (`docker logs -f the-architect`) as the
  companion command for watching a triggered run.
