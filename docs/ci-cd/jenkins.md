# Jenkins Deployment

> Status: stub. See `docs/LLM_DOCS.prompt.md` for how to complete this page.

## TODO

- Document the purpose of the `Jenkinsfile` at the repo root: an optional
  CI/CD pipeline that deploys the stack to a host running Jenkins, as an
  alternative/complement to manually running `docker compose up -d --build`.
- Document the "Setup Variables" stage: derives `REPO_NAME` from
  `env.GIT_URL` (strips the `.git` suffix), used to namespace the Jenkins
  credential IDs looked up in the next stage.
- Document, as a numbered prerequisite/setup list (per the "Document setup
  steps and prerequisites" rule in `docs/LLM_DOCS.prompt.md`), every Jenkins
  credential the pipeline expects to exist, named `<REPO_NAME>-<suffix>`:
  `-env` (secret file → copied to `.env`), `-team-json` (secret file →
  copied to `team.json`), `-config-json` (secret file → copied to
  `config.json`), `-plugins-discord-bot-py` (secret file → copied to
  `plugins/discord_bot.py`), `-file-1` (secret file → copied to
  `knowledge/Python_Machine_Learning_Second_Edition.pdf`, i.e. a
  knowledge-base seed file). Note the hardcoded filename on this last one
  as a limitation (only one arbitrary knowledge file can be seeded this
  way without modifying the `Jenkinsfile`).
- Document the "Deploy" stage's actual shell steps in order: creates
  `/media/knowledge` and `plugins/` directories, touches
  `plugins/__init__.py`, copies each credential file into place, strips
  Windows line endings from `.env` (`sed -i 's/\r$//' .env`), then runs
  `docker compose down` followed by `docker compose up -d --build` (down
  first specifically to release stale bind-mount handles, per the inline
  comment).
- Note the commented-out post-deploy `.env` cleanup line and explain the
  security trade-off it represents (leaving `.env` on disk with secrets vs.
  removing it and needing it for future manual `docker compose` invocations
  outside Jenkins).
- Cross-link to `scripts/lsJenkins.sh`, `scripts/lsWorkspace.sh`,
  `scripts/wipeJenkins.sh` (link to `docs/reference/scripts.md`) as
  Jenkins-workspace-inspection helpers used alongside this pipeline.
