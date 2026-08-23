"""
ai_io/discord.py and ai_io/webhook.py both implement the same plugin
contract main.py's load_agent_and_tools() scans for (register(), tools,
broadcast_status). webhook.py was a near-duplicate of discord.py with
several real bugs - see the module docstring in webhook.py's git history
/ PR notes - that have since been fixed to match discord.py's (correct)
behavior:
  - _send_msg() returning a truthy string instead of False on missing
    credentials, which made discord_interaction() report success even when
    nothing was sent
  - a malformed Discord API URL missing /api/v10/channels/
  - register()'s identity_prefix reading a lowercase SETTINGS key that
    never matched the actual (uppercase) key, so it silently always fell
    through to the default

One thing intentionally NOT fixed here: both modules register a tool
literally named "discord_interaction". If both files are present under
ai_io/ at once, main.py's plugin-hook scan (see
tests/test_main_load_agent_and_tools.py) will register two different
tools under the same name for every agent. That's a cross-file design
decision - rename one, retire one, or otherwise disambiguate - rather
than a bug either individual file's tests can meaningfully assert about.
"""
import requests
import pytest

import ai_io.discord as discord_mod
import ai_io.webhook as webhook_mod


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture(autouse=True)
def reset_settings():
    """Both modules' SETTINGS dicts are module-level mutable globals; reset
    them around each test so one test's monkeypatching can't bleed into the
    next."""
    discord_defaults = dict(discord_mod.SETTINGS)
    webhook_defaults = dict(webhook_mod.SETTINGS)
    yield
    discord_mod.SETTINGS.clear()
    discord_mod.SETTINGS.update(discord_defaults)
    webhook_mod.SETTINGS.clear()
    webhook_mod.SETTINGS.update(webhook_defaults)


@pytest.mark.parametrize("mod", [discord_mod, webhook_mod])
class TestSendMsgCredentialResolution:
    def test_returns_false_when_no_credentials_configured_anywhere(self, mod, no_env_leak, isolated_cwd):
        assert mod._send_msg("hello") is False

    def test_settings_dict_takes_priority_over_config(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        mod.SETTINGS["BOT_TOKEN"] = "settings-token"
        mod.SETTINGS["SERVER_ID"] = "settings-server"
        mod.SETTINGS["CHANNEL_ID"] = "settings-channel"

        def fake_post(url, headers=None, json=None, timeout=None):
            assert headers["Authorization"] == "Bot settings-token"
            return FakeResponse(200)

        monkeypatch.setattr(requests, "post", fake_post)
        assert mod._send_msg("hello") is True

    def test_returns_false_when_channel_id_missing(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        mod.SETTINGS["BOT_TOKEN"] = "t"
        mod.SETTINGS["SERVER_ID"] = "s"
        # CHANNEL_ID deliberately left empty in both SETTINGS and env
        assert mod._send_msg("hello") is False

    def test_http_error_status_returns_false(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        mod.SETTINGS["BOT_TOKEN"] = "t"
        mod.SETTINGS["SERVER_ID"] = "s"
        mod.SETTINGS["CHANNEL_ID"] = "c"
        monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(403))
        assert mod._send_msg("hello") is False

    def test_network_exception_returns_false(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        mod.SETTINGS["BOT_TOKEN"] = "t"
        mod.SETTINGS["SERVER_ID"] = "s"
        mod.SETTINGS["CHANNEL_ID"] = "c"

        def boom(*a, **kw):
            raise requests.ConnectionError("no network")
        monkeypatch.setattr(requests, "post", boom)
        assert mod._send_msg("hello") is False

    def test_successful_post_returns_true(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        mod.SETTINGS["BOT_TOKEN"] = "t"
        mod.SETTINGS["SERVER_ID"] = "s"
        mod.SETTINGS["CHANNEL_ID"] = "c"
        monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(201))
        assert mod._send_msg("hello") is True


@pytest.mark.parametrize("mod", [discord_mod, webhook_mod])
class TestDiscordInteractionTool:
    def test_reports_success_message_when_send_succeeds(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        monkeypatch.setattr(mod, "_send_msg", lambda message: True)
        result = mod.discord_interaction("hi")
        assert "successfully posted" in result

    def test_reports_error_message_when_send_fails(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        monkeypatch.setattr(mod, "_send_msg", lambda message: False)
        result = mod.discord_interaction("hi")
        assert "Discord API Error" in result

    def test_missing_credentials_correctly_reports_failure_not_success(
        self, mod, no_env_leak, isolated_cwd
    ):
        """
        Regression guard for webhook.py's original bug: _send_msg used to
        return a non-empty *string* on missing credentials, which is
        truthy in Python, so `"✅..." if success else "❌..."` would
        incorrectly report success. With no credentials configured at all,
        this must report failure.
        """
        result = mod.discord_interaction("hi")
        assert "Discord API Error" in result


@pytest.mark.parametrize("mod", [discord_mod, webhook_mod])
class TestBroadcastStatus:
    def test_delegates_to_send_msg_and_returns_bool(self, mod, no_env_leak, isolated_cwd, monkeypatch):
        monkeypatch.setattr(mod, "_send_msg", lambda message: True)
        assert mod.broadcast_status("status update") is True

    def test_returns_false_not_a_string_on_failure(self, mod, no_env_leak, isolated_cwd):
        # No credentials configured: exercises the real _send_msg path
        # end-to-end, confirming it's a bool and not a truthy string.
        result = mod.broadcast_status("status update")
        assert result is False


class TestWebhookUsesCorrectDiscordApiUrl:
    """Pins down the fixed URL specifically, since a malformed URL would
    silently fail against the real Discord API even with valid
    credentials - the earlier version was missing /api/v10/channels/."""

    def test_url_includes_api_v10_channels_path(self, no_env_leak, isolated_cwd, monkeypatch):
        webhook_mod.SETTINGS["BOT_TOKEN"] = "t"
        webhook_mod.SETTINGS["SERVER_ID"] = "s"
        webhook_mod.SETTINGS["CHANNEL_ID"] = "12345"
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            return FakeResponse(200)

        monkeypatch.setattr(requests, "post", fake_post)
        webhook_mod._send_msg("hello")
        assert captured["url"] == "https://discord.com/api/v10/channels/12345/messages"


class TestDiscordNestedConfigFallback:
    """
    discord.py's _send_msg has a second-tier fallback: if SETTINGS doesn't
    have a credential, it checks the nested DISCORD_BOT_SETTINGS dict from
    config.json before giving up. webhook.py has no such fallback (see
    TestWebhookFlatConfigFallback below) - these are exercised separately
    since the two modules' credential-resolution logic genuinely differs.
    """

    def test_server_id_resolved_via_nested_guild_id_key(self, no_env_leak, isolated_cwd, monkeypatch):
        discord_mod.SETTINGS["BOT_TOKEN"] = "t"
        discord_mod.SETTINGS["CHANNEL_ID"] = "c"
        # SERVER_ID deliberately left unset in SETTINGS
        (isolated_cwd / "config.json").write_text(
            '{"DISCORD_BOT_SETTINGS": {"GUILD_ID": "nested-server-id"}}'
        )
        monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(200))
        assert discord_mod._send_msg("hello") is True

    def test_returns_false_when_server_id_missing_from_both_settings_and_nested_config(
        self, no_env_leak, isolated_cwd
    ):
        discord_mod.SETTINGS["BOT_TOKEN"] = "t"
        discord_mod.SETTINGS["CHANNEL_ID"] = "c"
        (isolated_cwd / "config.json").write_text('{"DISCORD_BOT_SETTINGS": {}}')
        assert discord_mod._send_msg("hello") is False

    def test_register_defaults_prefix_true_when_nested_config_is_not_a_dict(self, no_env_leak, isolated_cwd):
        """
        Covers register()'s final else branch: DISCORD_BOT_SETTINGS present
        in config.json but not actually a dict (e.g. malformed by hand),
        so the isinstance guard fails and the function falls back to the
        hardcoded True default rather than raising.
        """
        discord_mod.SETTINGS["RESPONSE_PREFIX_ENABLED"] = None
        (isolated_cwd / "config.json").write_text('{"DISCORD_BOT_SETTINGS": "not-a-dict"}')
        reg = discord_mod.register()
        assert reg["identity_prefix"] is True


class TestWebhookFlatConfigFallback:
    """webhook.py falls back to flat top-level config/env keys (no nested
    DISCORD_BOT_SETTINGS support), unlike discord.py."""

    def test_server_id_resolved_via_flat_env_fallback(self, no_env_leak, isolated_cwd, monkeypatch):
        webhook_mod.SETTINGS["BOT_TOKEN"] = "t"
        webhook_mod.SETTINGS["CHANNEL_ID"] = "c"
        monkeypatch.setenv("SERVER_ID", "env-server-id")
        monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(200))
        assert webhook_mod._send_msg("hello") is True

    def test_returns_false_when_server_id_missing_from_both_settings_and_env(self, no_env_leak, isolated_cwd):
        webhook_mod.SETTINGS["BOT_TOKEN"] = "t"
        webhook_mod.SETTINGS["CHANNEL_ID"] = "c"
        assert webhook_mod._send_msg("hello") is False


class TestRegister:
    def test_discord_register_reflects_prefix_setting(self, no_env_leak, isolated_cwd):
        discord_mod.SETTINGS["RESPONSE_PREFIX_ENABLED"] = True
        reg = discord_mod.register()
        assert reg["tools"] == [discord_mod.discord_interaction]
        assert reg["enabled_for"] == ["*"]
        assert reg["identity_prefix"] is True

    def test_discord_register_falls_back_to_config_when_settings_unset(self, no_env_leak, isolated_cwd):
        discord_mod.SETTINGS["RESPONSE_PREFIX_ENABLED"] = None
        (isolated_cwd / "config.json").write_text(
            '{"DISCORD_BOT_SETTINGS": {"RESPONSE_PREFIX_ENABLED": false}}'
        )
        reg = discord_mod.register()
        assert reg["identity_prefix"] is False

    def test_webhook_register_reads_correct_uppercase_settings_key(self, no_env_leak, isolated_cwd):
        """
        Regression guard for the original bug: register() looked up
        SETTINGS.get("response_prefix_enabled") (lowercase), which never
        matched the dict's actual "RESPONSE_PREFIX_ENABLED" key and so
        always silently fell through to the True default regardless of
        configuration. Setting it False here must now actually take
        effect.
        """
        webhook_mod.SETTINGS["RESPONSE_PREFIX_ENABLED"] = False
        reg = webhook_mod.register()
        assert reg["identity_prefix"] is False

    def test_webhook_register_defaults_true_when_unset(self, no_env_leak, isolated_cwd):
        webhook_mod.SETTINGS.pop("RESPONSE_PREFIX_ENABLED", None)
        reg = webhook_mod.register()
        assert reg["identity_prefix"] is True
