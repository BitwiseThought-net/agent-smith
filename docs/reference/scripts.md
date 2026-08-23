# Helper Scripts (`scripts/`)

> Status: stub. See `docs/README.md` for how to complete this page.

## TODO

Document each script in `scripts/` in its own short subsection: what it
does, what it assumes about the current working directory / running
containers, and a copy-pasteable usage example. Note which are meant to be
run on the Docker host vs. inside a container.

- `scripts/command.sh` — currently a comments-only reference file (no
  active commands) documenting the `main.py` CLI invocation patterns; link
  to `docs/operations/cli-usage.md` for the authoritative, verified version
  of these examples instead of trusting this file's comments verbatim.
- `scripts/ingest.sh` — runs `python ingest.py` inside the container named
  after the current directory's basename (`$(basename "$PWD")`) via
  `docker exec`; note this naming assumption (expects to be run from the
  project directory, and expects the container name to match it — point out
  that this could mismatch the actual `container_name: the-architect` set
  in `docker-compose.yml` depending on the folder name, which is a
  potential gotcha worth calling out).
- `scripts/install_tools.py` — already documented in
  `docs/tools/open-webui-tools.md`; link there instead of duplicating.
- `scripts/logs.sh` — `docker logs -f the-architect`, tails the main
  container's logs.
- `scripts/prune.sh` — `docker system prune -a`; document this as a
  destructive, host-wide Docker cleanup command (removes *all* unused
  Docker data, not just this project's) and flag the risk clearly.
- `scripts/trim.sh` — `docker compose down -v --rmi all --remove-orphans`;
  document this as a full teardown of this project's stack including
  volumes (data loss: Ollama models, Open WebUI data, Chroma data) and
  images.
- `scripts/update.sh` — has a shebang typo (`!#/bin/bash` instead of
  `#!/bin/bash`) that likely prevents it from being interpreted as intended
  — flag this explicitly; document its intent (`git commit -m "updates"`
  then `git push -u origin HEAD`) while noting the hardcoded, non-
  descriptive commit message as a limitation.
- `scripts/lsJenkins.sh` / `scripts/lsWorkspace.sh` / `scripts/wipeJenkins.sh`
  — Jenkins workspace inspection/cleanup helpers operating on
  `/var/lib/docker/volumes/jenkins_jenkins_data/_data/workspace`; document
  alongside `docs/ci-cd/jenkins.md` and link both directions. Flag
  `wipeJenkins.sh` as destructive (recursively deletes the entire Jenkins
  workspace directory).
