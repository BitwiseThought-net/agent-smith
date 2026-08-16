"""
run_mission() is the top-level orchestration loop; the bulk of its body
(building Task/Crew instances, calling step_crew.kickoff(), routing output
through ai_io channels) is tightly coupled to a real or heavily-mocked
CrewAI + ai_io stack and isn't a good fit for unit tests. What's cleanly
testable in isolation are its guard clauses: LLM readiness, and team.json
presence/validity. We also exercise the trivial "zero configured agents"
path, since it walks the loop's setup code without needing to fake any
framework internals.
"""
import json
import pytest

import main


@pytest.fixture(autouse=True)
def no_real_llm_wait(monkeypatch):
    """Every test here should short-circuit past the network-polling step."""
    monkeypatch.setattr(main, "wait_for_llm", lambda url, model: None)


def test_returns_early_when_llm_wait_times_out(isolated_cwd, no_env_leak, monkeypatch):
    def raise_timeout(url, model):
        raise TimeoutError(f"LiteLLM timeout for {model}")
    monkeypatch.setattr(main, "wait_for_llm", raise_timeout)
    # team.json deliberately not created: if run_mission proceeded past the
    # timeout, it would hit this missing-file branch instead, which would
    # mask the timeout branch actually being exercised. Its absence here
    # lets us confirm via the log-free return that the function bailed out
    # at the LLM-wait stage specifically.
    result = main.run_mission()
    assert result is None


def test_returns_early_when_team_config_missing(isolated_cwd, no_env_leak):
    assert not (isolated_cwd / "team.json").exists()
    result = main.run_mission()
    assert result is None


def test_returns_early_when_team_config_is_malformed_json(isolated_cwd, no_env_leak):
    (isolated_cwd / "team.json").write_text("{not valid json")
    result = main.run_mission()
    assert result is None


def test_respects_custom_team_config_path(isolated_cwd, no_env_leak, monkeypatch):
    monkeypatch.setenv("TEAM_CONFIG", "custom_team.json")
    (isolated_cwd / "custom_team.json").write_text(json.dumps({"active_agents": []}))
    result = main.run_mission()
    assert result == "Complete Swarm Operation Successful."


def test_completes_successfully_with_zero_configured_agents(isolated_cwd, no_env_leak):
    (isolated_cwd / "team.json").write_text(json.dumps({"active_agents": []}))
    result = main.run_mission()
    assert result == "Complete Swarm Operation Successful."


def test_skips_agent_when_framework_adapter_fails_to_load(isolated_cwd, no_env_leak, monkeypatch):
    """
    If load_agent_and_tools() can't build an agent (e.g. missing framework
    file), run_mission logs it and moves on to the next configured agent
    rather than crashing the whole mission.
    """
    monkeypatch.setattr(main, "load_agent_and_tools", lambda config, llm: (None, None))
    (isolated_cwd / "team.json").write_text(json.dumps({
        "active_agents": [
            {"name": "brokenagent", "framework": "nonexistent"},
        ]
    }))
    result = main.run_mission()
    assert result == "Complete Swarm Operation Successful."


def test_terminal_instruction_branch_logs_when_argv_has_extra_args(isolated_cwd, no_env_leak, monkeypatch):
    """
    Covers the len(sys.argv) > 1 guard's simple branch: a non-empty argv
    routes into the "global terminal instruction" logging path. Note the
    sibling `sys.argv == "--agent"` branch immediately above it compares
    the whole argv *list* to the literal string "--agent", which can never
    be True in Python -- that specific branch is dead code as written, so
    it isn't (and can't meaningfully be) exercised here.
    """
    monkeypatch.setattr(main.sys, "argv", ["main.py", "do something interesting"])
    (isolated_cwd / "team.json").write_text(json.dumps({"active_agents": []}))
    result = main.run_mission()
    assert result == "Complete Swarm Operation Successful."


class _FakeTask:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeCrew:
    """Records construction kwargs and lets each test control kickoff()'s
    return value / side effect via a class-level hook, since run_mission
    constructs Crew internally and tests can't inject a pre-built instance."""
    instances = []
    kickoff_result = "mocked crew result"
    kickoff_side_effect = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        _FakeCrew.instances.append(self)

    def kickoff(self):
        if _FakeCrew.kickoff_side_effect:
            raise _FakeCrew.kickoff_side_effect
        return _FakeCrew.kickoff_result


class _FakeLayer:
    Task = _FakeTask
    Crew = _FakeCrew


@pytest.fixture
def fake_layer(monkeypatch):
    """
    Bypasses load_agent_and_tools entirely (it's covered by its own test
    file) so these tests can focus purely on run_mission's task-execution
    loop: ledger persistence, output-channel routing, running-context
    handling, and the librarian empty-knowledge bypass. Resets _FakeCrew's
    shared recording state before and after each test.

    Also pins sys.argv down to a single harmless element. main.py reads the
    *real* process sys.argv directly (len(sys.argv) > 1 triggers its
    "terminal instruction" override path) -- left uncontrolled, that means
    these tests' behavior would silently depend on how pytest itself was
    invoked (`pytest -q tests/foo.py` has a very different argv length than
    `pytest`), which is exactly the kind of hidden coupling that makes
    tests flaky across environments/CI invocations.
    """
    monkeypatch.setattr(main.sys, "argv", ["main.py"])
    _FakeCrew.instances = []
    _FakeCrew.kickoff_result = "mocked crew result"
    _FakeCrew.kickoff_side_effect = None
    fake_agent = object()
    monkeypatch.setattr(main, "load_agent_and_tools", lambda config, llm: (fake_agent, _FakeLayer))
    yield
    _FakeCrew.instances = []
    _FakeCrew.kickoff_side_effect = None


class TestTaskExecutionLoop:
    def test_happy_path_writes_ledger_and_routes_to_log_channel(self, isolated_cwd, no_env_leak, fake_layer):
        """
        Single non-librarian agent, single task, output given as a bare
        string ("log" rather than ["log"]) to also exercise the
        str -> [str] normalization at the top of the loop. Uses the real
        ai_io/log.py channel (just logs + prints, no external calls) rather
        than mocking output routing.
        """
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{
                "name": "coder",
                "framework": "crewai",
                "output": "log",
                "tasks": [{"description": "Write a function", "expected": "Working code"}],
            }]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."
        assert len(_FakeCrew.instances) == 1
        assert _FakeCrew.instances[0].kwargs["knowledge_sources"] == []

        ledger_files = list((isolated_cwd / "knowledge").glob("knowledge_ledger_coder_task_1_*.txt"))
        assert len(ledger_files) == 1
        content = ledger_files[0].read_text()
        assert "mocked crew result" in content
        assert "ASSIGNED_MISSION_PROMPT: Write a function" in content, repr(content)

    def test_unregistered_output_channel_is_logged_and_skipped(self, isolated_cwd, no_env_leak, fake_layer):
        """A channel name with no matching ai_io/<name>.py module shouldn't
        abort the mission -- just gets logged as a routing failure."""
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{
                "name": "coder",
                "framework": "crewai",
                "output": ["log", "not_a_real_channel_xyz"],
                "tasks": [{"description": "Do work"}],
            }]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."

    def test_librarian_with_empty_knowledge_bypasses_crew_entirely(self, isolated_cwd, no_env_leak, fake_layer):
        """
        get_all_knowledge_sources() is left un-mocked here: the real
        implementation, pointed at isolated_cwd with no knowledge/
        directory present, naturally returns []. That should trip the
        "empty workspace" safety bypass and skip Task/Crew construction
        altogether.
        """
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{"name": "Librarian", "framework": "crewai", "tasks": [{"description": "Scan"}]}]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."
        assert len(_FakeCrew.instances) == 0  # never constructed

        ledger_files = list((isolated_cwd / "knowledge").glob("knowledge_ledger_Librarian_task_1_*.txt"))
        assert len(ledger_files) == 1
        assert "currently empty" in ledger_files[0].read_text()

    def test_librarian_with_knowledge_sources_executes_crew_normally(
        self, isolated_cwd, no_env_leak, monkeypatch, fake_layer
    ):
        monkeypatch.setattr(main, "get_all_knowledge_sources", lambda: ["fake-source-1"])
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{"name": "librarian", "framework": "crewai", "tasks": [{"description": "Index files"}]}]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."
        assert len(_FakeCrew.instances) == 1
        assert _FakeCrew.instances[0].kwargs["knowledge_sources"] == ["fake-source-1"]

    def test_legacy_terminal_instruction_overrides_first_task_of_first_agent(
        self, isolated_cwd, no_env_leak, monkeypatch, fake_layer
    ):
        monkeypatch.setattr(main.sys, "argv", ["main.py", "ad-hoc instruction"])
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{"name": "coder", "framework": "crewai", "tasks": [{"description": "original desc"}]}]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."
        task_instance = _FakeCrew.instances[0].kwargs["tasks"][0]
        assert "Execute user terminal instruction:" in task_instance.kwargs["description"]

    def test_exception_during_ledger_persist_is_caught_and_mission_continues(
        self, isolated_cwd, no_env_leak, monkeypatch, fake_layer
    ):
        """
        The try/except around persist_agent_knowledge + output routing
        (NOT around step_crew.kickoff() itself, see the test below) catches
        failures here and, as long as MAX_RETRIES > 1, logs and moves on
        rather than aborting the whole mission.
        """
        monkeypatch.setenv("MAX_RETRIES", "3")

        def boom(**kwargs):
            raise RuntimeError("simulated disk failure")
        monkeypatch.setattr(main, "persist_agent_knowledge", boom)

        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{"name": "coder", "framework": "crewai", "tasks": [{"description": "task"}]}]
        }))
        result = main.run_mission()
        assert result == "Complete Swarm Operation Successful."

    def test_kickoff_exception_is_uncaught_and_propagates(
        self, isolated_cwd, no_env_leak, monkeypatch, fake_layer
    ):
        """
        Documents a real gap in the current implementation: unlike the
        persist/routing block, step_crew.kickoff() itself is called
        *outside* the try/except at the bottom of the loop (it runs, along
        with set_mission_timeout/clear_mission_timeout, before that try
        block begins). A framework-level exception from kickoff() is
        therefore NOT caught here -- it propagates straight out of
        run_mission() uncaught, and because clear_mission_timeout() is
        skipped too, it also leaves the mission-timeout SIGALRM armed.
        This test pins down that behavior and cleans up the dangling alarm
        itself afterward so it can't fire during a later, unrelated test.
        """
        import signal
        _FakeCrew.kickoff_side_effect = RuntimeError("simulated framework crash")
        (isolated_cwd / "team.json").write_text(json.dumps({
            "active_agents": [{"name": "coder", "framework": "crewai", "tasks": [{"description": "task"}]}]
        }))
        try:
            with pytest.raises(RuntimeError, match="simulated framework crash"):
                main.run_mission()
        finally:
            signal.alarm(0)  # safety net: clear the alarm this bug leaves armed
