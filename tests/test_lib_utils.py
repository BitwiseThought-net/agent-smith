import json
import os
import time
import signal
import pytest

import lib.utils as utils


class TestGetConfigValue:
    def test_returns_default_when_nothing_set(self, isolated_cwd, no_env_leak):
        assert utils.get_config_value("SOME_KEY", "fallback") == "fallback"

    def test_returns_default_none_when_unspecified(self, isolated_cwd, no_env_leak):
        assert utils.get_config_value("SOME_KEY") is None

    def test_env_var_used_when_no_config_file(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("SOME_KEY", "from-env")
        assert utils.get_config_value("SOME_KEY", "fallback") == "from-env"

    def test_config_json_takes_priority_over_env(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("SOME_KEY", "from-env")
        (isolated_cwd / "config.json").write_text(json.dumps({"SOME_KEY": "from-config"}))
        # utils.CONFIG_FILE_PATH is a module-level relative Path("config.json"),
        # resolved against cwd at call time, so chdir (via isolated_cwd) is enough.
        assert utils.get_config_value("SOME_KEY", "fallback") == "from-config"

    def test_config_json_null_value_falls_through_to_env(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("SOME_KEY", "from-env")
        (isolated_cwd / "config.json").write_text(json.dumps({"SOME_KEY": None}))
        assert utils.get_config_value("SOME_KEY", "fallback") == "from-env"

    def test_config_json_missing_key_falls_through_to_env(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("OTHER_KEY", "from-env")
        (isolated_cwd / "config.json").write_text(json.dumps({"SOME_KEY": "x"}))
        assert utils.get_config_value("OTHER_KEY", "fallback") == "from-env"

    def test_malformed_config_json_falls_through_to_env(self, isolated_cwd, no_env_leak, monkeypatch):
        monkeypatch.setenv("SOME_KEY", "from-env")
        (isolated_cwd / "config.json").write_text("{not valid json")
        assert utils.get_config_value("SOME_KEY", "fallback") == "from-env"

    def test_malformed_config_json_falls_through_to_default(self, isolated_cwd, no_env_leak):
        (isolated_cwd / "config.json").write_text("{not valid json")
        assert utils.get_config_value("SOME_KEY", "fallback") == "fallback"


class TestUpdateHeartbeat:
    def test_writes_current_unix_timestamp(self, tmp_path, monkeypatch):
        heartbeat_path = tmp_path / "heartbeat"
        # update_heartbeat hardcodes "/tmp/heartbeat"; redirect via monkeypatching
        # the open target is not trivial without changing the function, so we
        # instead verify against the real /tmp/heartbeat but clean up after.
        real_path = "/tmp/heartbeat"
        before = time.time()
        utils.update_heartbeat()
        after = time.time()
        with open(real_path) as f:
            written = int(f.read().strip())
        assert before - 1 <= written <= after + 1
        os.remove(real_path)

    def test_does_not_raise_if_tmp_unwritable(self, monkeypatch):
        def boom(*a, **kw):
            raise IOError("disk full")
        monkeypatch.setattr("builtins.open", boom)
        # Should be swallowed, not propagate
        utils.update_heartbeat()


class TestMissionTimeout:
    def test_timeout_raises_after_deadline(self):
        with pytest.raises(TimeoutError):
            utils.set_mission_timeout(1)
            time.sleep(2)
        utils.clear_mission_timeout()

    def test_clear_prevents_timeout_from_firing(self):
        utils.set_mission_timeout(1)
        utils.clear_mission_timeout()
        # If the alarm weren't cleared, this sleep would raise TimeoutError.
        time.sleep(1.5)

    def teardown_method(self, method):
        # Safety net: make sure no test leaves a pending SIGALRM armed,
        # which would otherwise fire during a later, unrelated test.
        signal.alarm(0)


class TestGetActivePlugins:
    def test_returns_empty_dict_when_file_missing(self, isolated_cwd):
        assert utils.get_active_plugins() == {}

    def test_reads_plugins_json(self, isolated_cwd):
        plugins_dir = isolated_cwd / "plugins"
        plugins_dir.mkdir()
        (plugins_dir / "plugins.json").write_text(json.dumps({"foo": True}))
        assert utils.get_active_plugins() == {"foo": True}

    def test_malformed_plugins_json_returns_empty_dict(self, isolated_cwd):
        plugins_dir = isolated_cwd / "plugins"
        plugins_dir.mkdir()
        (plugins_dir / "plugins.json").write_text("{not valid")
        assert utils.get_active_plugins() == {}
