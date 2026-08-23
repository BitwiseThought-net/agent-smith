# Documentation Index

This is the table of contents for `docs/`. Keep it up to date: whenever a new
stub page is created (per the instructions in `docs/LLM_DOCS.prompt.md`), add
a line for it here in the appropriate section. ✅ marks pages that are fully
written; unmarked pages are still stubs with a `## TODO` list.

## Getting Started
- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)

## Architecture
- ✅ [System Overview](architecture/overview.md)
- [The `ai_layer` Abstraction Engine](architecture/ai-layer-abstraction.md)

## Configuration
- ✅ [`config.json` Reference](configuration/config-json.md)
- ✅ [`.env` Reference](configuration/env-file.md)
- ✅ [`team.json` Reference](configuration/team-json.md)

## Agents
- ✅ [Built-in Agents](agents/overview.md)

## Tools
- [Agent Tools (`tools/` + `team.json`)](tools/agent-tools.md)
- [Open WebUI Tools](tools/open-webui-tools.md)

## AI Layer / Framework Adapters
- [Supported Frameworks](ai_layer/frameworks.md)

## Output Routing (`ai_io/`)
- [Output Channels](ai_io/output-channels.md)

## Knowledge Base / RAG
- [Knowledge Base & Ingestion](knowledge/knowledge-base.md)
- [File Loaders](knowledge/loaders.md)

## Operations
- [Docker Compose Services](operations/docker-compose-services.md)
- [CLI / Terminal Usage](operations/cli-usage.md)
- [Resilience & Health Monitoring](operations/resilience-health.md)

## CI/CD
- [Jenkins Deployment](ci-cd/jenkins.md)
- [GitHub Actions Workflows](ci-cd/github-actions.md)

## Reference
- [Helper Scripts (`scripts/`)](reference/scripts.md)
- [Testing](reference/testing.md)
- [Security & Sandbox Model](reference/security-sandbox.md)
