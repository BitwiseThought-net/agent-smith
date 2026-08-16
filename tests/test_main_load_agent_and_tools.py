"""
load_agent_and_tools() dynamically imports an ai_layer/<framework>.py
adapter file, resolved relative to main.py's own location (not cwd), so
these tests fake the file-existence check and the import itself rather than
writing real files into the repo's ai_layer/ directory. The ai_io/ hook
directory is also resolved relative to main.py's real location; since that
directory genuinely exists in this repo (discord.py, log.py, webhook.py),
tests that don't care about it force os.path.exists() to report it as
missing so the scan is skipped and the test stays hermetic.
"""
import os
import types
import importlib
import pytest

import main

# Captured once, at test-module import time, before any fixture or test has
# had a chance to monkeypatch os.path.exists. Local "real_exists = os.path.exists"
# captured *inside* a test function would instead grab whatever fixture-patched
# version is active by that point in the test's setup, silently chaining fakes
# together instead of falling back to genuine filesystem behavior.
_REAL_OS_PATH_EXISTS = os.path.exists


@pytest.fixture
def patch_exists_for_fake_framework(monkeypatch):
    """
    Makes os.path.exists() report True for a synthetic
    ai_layer/faketest.py and agents/<agent_name>.py path, False for the
    real ai_io/ directory (to skip that scan), and defers to the real
    implementation for everything else.
    """
    real_exists = _REAL_OS_PATH_EXISTS

    def fake_exists(path):
        p = str(path)
        if p.endswith(os.path.join("ai_layer", "faketest.py")):
            return True
        if p.endswith(os.path.join("agents", "testagent.py")):
            return True
        if p.endswith("ai_io"):
            return False
        return real_exists(path)

    monkeypatch.setattr(main.os.path, "exists", fake_exists)
    return fake_exists


def test_returns_none_none_when_framework_file_missing(isolated_cwd, no_env_leak):
    agent_config = {"name": "someagent", "framework": "definitely_not_a_real_framework"}
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)


def test_returns_none_none_when_framework_import_raises(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    def fake_import_module(name):
        if name == "ai_layer.faketest":
            raise ImportError("simulated broken adapter")
        raise ImportError(f"unexpected import in this test: {name}")

    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    agent_config = {"name": "someagent", "framework": "faketest"}
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)


def test_returns_none_none_when_agent_file_missing(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    fake_layer_module = types.ModuleType("ai_layer.faketest")

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        raise ImportError(f"unexpected import in this test: {name}")

    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    # Deliberately don't create agents/no_such_agent.py, and don't extend
    # patch_exists_for_fake_framework to cover it, so the real (missing)
    # file check applies.
    agent_config = {"name": "no_such_agent", "framework": "faketest"}
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)


def test_tool_import_failure_is_logged_and_skipped_others_still_load(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    """
    agent_config can list several tools; a broken one should only produce a
    warning log and be skipped, not abort loading the rest -- and shouldn't
    prevent the function from reaching the (later) agent-file check.
    """
    fake_layer_module = types.ModuleType("ai_layer.faketest")

    fake_good_tool_module = types.ModuleType("tools.good_tool")
    fake_good_tool_module.get_tools = lambda: ["good-tool-instance"]

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "tools.good_tool":
            return fake_good_tool_module
        if name == "tools.bad_tool":
            raise ImportError("simulated broken tool module")
        raise ImportError(f"unexpected import in this test: {name}")

    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    agent_config = {
        "name": "no_such_agent",  # missing on purpose: keeps this test focused
        "framework": "faketest",
        "tools": ["good_tool", "bad_tool"],
    }
    # Should not raise despite tools.bad_tool failing; falls through to the
    # (expected) agent-file-missing early return.
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)


def test_successful_construction_returns_agent_and_layer(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    """
    Documents a real coupling worth knowing about: load_agent_and_tools
    reads the LLM configuration off a *module-level global* `main.llm_config`
    rather than from its own `llm` parameter (which is accepted but never
    used). That global is normally only set as a side effect of run_mission()
    executing first. Calling load_agent_and_tools() on its own -- as this
    test does -- requires manually setting main.llm_config beforehand, or
    this raises NameError deep inside a broad try/except and silently
    returns (None, None) instead of constructing anything.
    """
    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeLLM:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_layer_module = types.ModuleType("ai_layer.faketest")
    fake_layer_module.Agent = FakeAgent
    fake_layer_module.LLM = FakeLLM

    fake_agent_file_module = types.ModuleType("agents.testagent")

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "agents.testagent":
            return fake_agent_file_module
        raise ImportError(f"unexpected import in this test: {name}")

    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(
        main,
        "llm_config",
        {
            "model": "ollama/testmodel",
            "base_url": "http://litellm:4000",
            "api_key": "sk-test",
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        raising=False,
    )

    agent_config = {
        "name": "testagent",
        "framework": "faketest",
        "role": "Tester",
        "backstory": "A test agent.",
    }
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert isinstance(agent, FakeAgent)
    assert layer is fake_layer_module
    assert agent.kwargs["role"] == "Tester"


def test_ai_io_import_failure_is_caught_and_logged(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    """
    The real ai_io/ directory does exist in this repo, so os.path.exists()
    for it isn't overridden here (patch_exists_for_fake_framework forces it
    False for other tests to skip this block entirely; this test instead
    exercises the outer try/except around importing the ai_io package
    itself, by making that one import call fail).
    """
    fake_layer_module = types.ModuleType("ai_layer.faketest")
    fake_layer_module.Agent = lambda **kw: None
    fake_layer_module.LLM = lambda **kw: None
    monkeypatch.setattr(main, "llm_config", {
        "model": "m", "base_url": "u", "api_key": "k", "temperature": 0.1, "max_tokens": 10,
    }, raising=False)

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "ai_io":
            raise ImportError("simulated broken ai_io package")
        raise ImportError(f"unexpected import in this test: {name}")

    # Override just the framework-path portion of the fixture's behavior;
    # leave the real ai_io/ directory's existence check untouched so the
    # block is actually entered.
    real_exists = _REAL_OS_PATH_EXISTS

    def fake_exists(path):
        p = str(path)
        if p.endswith(os.path.join("ai_layer", "faketest.py")):
            return True
        return real_exists(path)

    monkeypatch.setattr(main.os.path, "exists", fake_exists)
    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)

    agent_config = {"name": "no_such_agent", "framework": "faketest"}
    # Falls through to the (expected) agent-file-missing branch afterward.
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)


def test_ai_io_hook_registers_tools_and_appends_identity_prefix(
    isolated_cwd, no_env_leak, monkeypatch, tmp_path
):
    """
    Exercises the plugin-hook discovery loop: a module under ai_io/ that
    exposes a register() function returning {"enabled_for": [...],
    "tools": [...], "identity_prefix": True} should have its tools merged
    into the agent's tool list, and the identity_prefix instruction appended
    to the agent's backstory.
    """
    fake_pkg_dir = tmp_path / "fake_ai_io_pkg"
    fake_pkg_dir.mkdir()
    (fake_pkg_dir / "hook_module.py").write_text("# placeholder, only needs to exist on disk")

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_layer_module = types.ModuleType("ai_layer.faketest")
    fake_layer_module.Agent = FakeAgent
    fake_layer_module.LLM = lambda **kw: None
    monkeypatch.setattr(main, "llm_config", {
        "model": "m", "base_url": "u", "api_key": "k", "temperature": 0.1, "max_tokens": 10,
    }, raising=False)

    fake_ai_io_package = types.ModuleType("ai_io")
    fake_ai_io_package.__path__ = [str(fake_pkg_dir)]

    fake_hook_module = types.ModuleType("ai_io.hook_module")
    fake_hook_module.register = lambda: {
        "enabled_for": ["testagent"],
        "tools": ["tool-from-hook"],
        "identity_prefix": True,
    }

    fake_agent_file_module = types.ModuleType("agents.testagent")

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "ai_io":
            return fake_ai_io_package
        if name == "ai_io.hook_module":
            return fake_hook_module
        if name == "agents.testagent":
            return fake_agent_file_module
        raise ImportError(f"unexpected import in this test: {name}")

    real_exists = _REAL_OS_PATH_EXISTS

    def fake_exists(path):
        p = str(path)
        if p.endswith(os.path.join("ai_layer", "faketest.py")):
            return True
        if p.endswith(os.path.join("agents", "testagent.py")):
            return True
        return real_exists(path)

    monkeypatch.setattr(main.os.path, "exists", fake_exists)
    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(main.importlib, "reload", lambda m: m)

    agent_config = {"name": "testagent", "framework": "faketest", "backstory": "A test agent."}
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert isinstance(agent, FakeAgent)
    assert "tool-from-hook" in agent.kwargs["tools"]
    assert "IMPORTANT: Start every response with 'testagent: '." in agent_config["backstory"]


def test_ai_io_hook_module_error_is_caught_and_other_hooks_unaffected(
    isolated_cwd, no_env_leak, monkeypatch, tmp_path
):
    """A single broken ai_io hook module shouldn't abort discovery of the rest."""
    fake_pkg_dir = tmp_path / "fake_ai_io_pkg"
    fake_pkg_dir.mkdir()
    (fake_pkg_dir / "broken_hook.py").write_text("# placeholder")

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_layer_module = types.ModuleType("ai_layer.faketest")
    fake_layer_module.Agent = FakeAgent
    fake_layer_module.LLM = lambda **kw: None
    monkeypatch.setattr(main, "llm_config", {
        "model": "m", "base_url": "u", "api_key": "k", "temperature": 0.1, "max_tokens": 10,
    }, raising=False)

    fake_ai_io_package = types.ModuleType("ai_io")
    fake_ai_io_package.__path__ = [str(fake_pkg_dir)]
    fake_agent_file_module = types.ModuleType("agents.testagent")

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "ai_io":
            return fake_ai_io_package
        if name == "ai_io.broken_hook":
            raise RuntimeError("simulated hook module failure")
        if name == "agents.testagent":
            return fake_agent_file_module
        raise ImportError(f"unexpected import in this test: {name}")

    real_exists = _REAL_OS_PATH_EXISTS

    def fake_exists(path):
        p = str(path)
        if p.endswith(os.path.join("ai_layer", "faketest.py")):
            return True
        if p.endswith(os.path.join("agents", "testagent.py")):
            return True
        return real_exists(path)

    monkeypatch.setattr(main.os.path, "exists", fake_exists)
    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(main.importlib, "reload", lambda m: m)

    agent_config = {"name": "testagent", "framework": "faketest"}
    # Should not raise, despite the hook module blowing up.
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert isinstance(agent, FakeAgent)


def test_missing_llm_config_global_causes_silent_none_none(
    isolated_cwd, no_env_leak, monkeypatch, patch_exists_for_fake_framework
):
    """
    The flip side of the coupling documented above: if main.llm_config was
    never set (e.g. load_agent_and_tools is called without run_mission
    having run first), construction fails with a NameError that's caught
    by the function's own broad except-and-log, so the caller just sees
    (None, None) with no indication in the return value that anything
    unusual happened -- only the logged error explains it.
    """
    monkeypatch.delattr(main, "llm_config", raising=False)

    class FakeAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeLLM:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_layer_module = types.ModuleType("ai_layer.faketest")
    fake_layer_module.Agent = FakeAgent
    fake_layer_module.LLM = FakeLLM
    fake_agent_file_module = types.ModuleType("agents.testagent")

    def fake_import_module(name):
        if name == "ai_layer.faketest":
            return fake_layer_module
        if name == "agents.testagent":
            return fake_agent_file_module
        raise ImportError(f"unexpected import in this test: {name}")

    monkeypatch.setattr(main.importlib, "import_module", fake_import_module)
    agent_config = {"name": "testagent", "framework": "faketest"}
    agent, layer = main.load_agent_and_tools(agent_config, None)
    assert (agent, layer) == (None, None)
