# Resilience & Health Monitoring

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

- Document the heartbeat mechanism: `lib/utils.py:update_heartbeat()` writes
  a Unix timestamp to `/tmp/heartbeat` inside the container; it's called
  throughout `main.py` (loop iterations, `wait_for_llm` polling, before each
  task, etc.) so the file's mtime reflects "is the process still making
  progress," not just "is the process still running."
- Document the `the-architect` service `healthcheck` in
  `docker-compose.yml`: shells out to compare `date +%s` against
  `stat -c %Y /tmp/heartbeat`, failing if the gap exceeds 300 seconds (5
  minutes), checked every 1 minute with 3 retries and a 2-minute start
  period.
- Document the `autoheal` service (`willfarrell/autoheal`): watches Docker
  container health status via the mounted Docker socket and restarts any
  container labeled `autoheal: "true"` that goes unhealthy — list every
  service in `docker-compose.yml` carrying that label
  (`the-architect`, `open-webui`, `litellm`, `chromadb`, `ollama`).
- Document the "Idle State" behavior from `main.py:run_mission`: when a
  task-level exception occurs and `MAX_RETRIES` (config key, default `3`)
  is `<= 1`, the process enters an infinite `update_heartbeat(); sleep(60)`
  loop instead of exiting — explain that this deliberately keeps the
  container's heartbeat "alive" (so `autoheal` won't restart it) while
  halting mission progress, to allow log inspection via `scripts/logs.sh`
  before a human intervenes. Cross-link to
  `docs/configuration/config-json.md`'s `MAX_RETRIES` entry.
- Document `set_mission_timeout(seconds)` / `clear_mission_timeout()`
  (`lib/utils.py`, using `signal.alarm`): wraps each task's `Crew.kickoff()`
  call with a hard timeout from the `MISSION_TIMEOUT_SECONDS` config key
  (default `1800`), raising `TimeoutError` if exceeded.
- Document `wait_for_llm(url, model)` in `main.py`: polls
  `{LITELLM_URL}/models` every 15 seconds (up to a 600-second/10-minute
  total timeout) at mission start, checking for an `ollama/{model}` entry,
  before any agents run — explain this is why first boot can appear to
  "hang" while Ollama finishes pulling the model.
