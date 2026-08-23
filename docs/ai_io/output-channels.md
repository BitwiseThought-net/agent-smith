# Output Channels (`ai_io/`)

> Status: stub. See `docs/LLM_DOCS.prompt.md` for how to complete this page.

## TODO

- Explain the `ai_io/` plugin system's two responsibilities, both driven by
  `main.py:load_agent_and_tools` and `main.py:run_mission`:
  1. **Tool + identity registration**: every `ai_io/*.py` module is
     imported/reloaded on each agent load; if it defines a `register()`
     function, its returned `tools` are added to that agent (filtered by
     `enabled_for`, an allow-list of agent names or `"*"` for all), and if
     `identity_prefix` is truthy, the agent's `backstory` gets an appended
     instruction to prefix responses with `"<agent_name>: "`.
  2. **Output routing**: after each task completes, `main.py` reloads and
     calls `ai_io.<channel>.broadcast_status(message)` for every channel
     name listed in that agent's `team.json` `"output"` array (default
     `["log"]`), and logs an error if a named module is missing the
     required `broadcast_status` function.
- Document `ai_io/log.py`: the default/fallback channel; just prints the
  message to stdout via `lib.logger.log_text` and always returns `True`.
- Document `ai_io/discord.py` and `ai_io/webhook.py` together (they overlap
  significantly - read both closely and document any real differences you
  find, e.g. config source names, rather than assuming they're identical):
  - Both provide a `discord_interaction` agent tool (registered for all
    agents via `enabled_for: ["*"]`) and a `broadcast_status` output-routing
    function that POST a message to a Discord channel via the Discord REST
    API (`https://discord.com/api/v10/channels/{CHANNEL_ID}/messages`,
    bot token auth).
  - Document their config resolution precedence: an in-file `SETTINGS`
    dict (edit-in-place; takes priority) falling back to `config.json`'s
    `DISCORD_BOT_SETTINGS` object (`BOT_TOKEN`→`bot_settings.BOT_TOKEN` for
    `discord.py`; note `webhook.py` instead falls back to flat top-level
    `get_config_value("BOT_TOKEN"/"SERVER_ID"/"CHANNEL_ID")` calls - confirm
    this discrepancy against the actual code before documenting it, since
    it affects which `config.json` shape the user needs).
  - Reproduce the numbered Discord Developer Portal setup steps from each
    module's `INFO["instructions"]` list as the prerequisite setup
    walkthrough (bot creation, token, intents, OAuth2 scopes/permissions,
    inviting the bot, enabling Developer Mode, getting server/channel IDs),
    per the "Document setup steps and prerequisites" rule in
    `docs/LLM_DOCS.prompt.md`.
  - Document `RESPONSE_PREFIX_ENABLED` and how it maps to the
    `identity_prefix` behavior described above.
- Document how to add a new output channel: create `ai_io/<name>.py` with a
  `broadcast_status(message: str) -> bool` function (and optionally
  `register()` for tool/identity registration), then reference `<name>` in
  a `team.json` agent's `"output"` array.
