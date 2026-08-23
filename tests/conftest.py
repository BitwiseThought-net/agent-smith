"""
Shared fixtures for the test suite.

The application's `ai_layer/orchestrator.py` imports CrewAI at module load
time (which pulls in a large dependency chain: crewai, chromadb, langchain,
etc). Since most of the code under test only cares about *its own* logic and
just imports names off the orchestrator, we install a lightweight fake
`ai_layer.orchestrator` module into sys.modules before any test code imports
it. This keeps the suite fast and dependency-free while still exercising the
real logic in tools/, loaders/, lib/, knowledge_manager.py, and main.py.

If you later add tests that need the *real* CrewAI behavior, write them as
a separate, explicitly-marked integration suite instead of relying on this
fake.
"""
import sys
import os
import types
import importlib
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class _FakeKnowledgeSource:
    """Stand-in for a CrewAI XxxKnowledgeSource class."""
    def __init__(self, file_path=None, metadata=None, **kwargs):
        self.file_path = file_path
        self.metadata = metadata or {}
        self.kwargs = kwargs

    def __repr__(self):
        return f"<FakeKnowledgeSource path={self.file_path!r} meta={self.metadata!r}>"

    def __eq__(self, other):
        return (
            isinstance(other, _FakeKnowledgeSource)
            and self.file_path == other.file_path
            and self.metadata == other.metadata
        )


class _FakeKnowledge:
    CSV = _FakeKnowledgeSource
    Docling = _FakeKnowledgeSource
    JSON = _FakeKnowledgeSource
    Excel = _FakeKnowledgeSource
    TextFile = _FakeKnowledgeSource
    XML = _FakeKnowledgeSource


def _fake_tool_decorator(name):
    """Mimics crewai.tools.tool: returns a decorator that tags a callable."""
    def decorator(fn):
        fn.tool_name = name
        return fn
    return decorator


class _FakeAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeTask:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeCrew:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def kickoff(self):
        return "fake-crew-result"


class _FakeLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeExecTool:
    def __init__(self, *a, **kw):
        pass


class _FakeFileReadTool:
    def __init__(self, *a, **kw):
        pass


class _FakeFileWriterTool:
    def __init__(self, *a, **kw):
        pass


class _FakeDuckDuckGoSearchTool:
    def __init__(self, *a, **kw):
        pass


def _install_fake_orchestrator():
    fake_module = types.ModuleType("ai_layer.orchestrator")
    fake_module.Agent = _FakeAgent
    fake_module.Task = _FakeTask
    fake_module.Crew = _FakeCrew
    fake_module.LLM = _FakeLLM
    fake_module.tool = _fake_tool_decorator
    fake_module.Process = None
    fake_module.Knowledge = _FakeKnowledge
    fake_module.FileReadTool = _FakeFileReadTool
    fake_module.FileWriterTool = _FakeFileWriterTool
    fake_module.EXECTool = _FakeExecTool
    fake_module.DuckDuckGoSearchTool = _FakeDuckDuckGoSearchTool
    sys.modules["ai_layer.orchestrator"] = fake_module
    return fake_module


# IMPORTANT: this must run at conftest *import* time, not inside a fixture.
# Pytest imports test modules (which in turn import tools.*/loaders.*, which
# import ai_layer.orchestrator) during collection, before any fixture - even
# an autouse session-scoped one - gets a chance to run. Installing the fake
# module here, at module load time, ensures it's in sys.modules before any
# test file is collected.
_install_fake_orchestrator()


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """
    Runs a test inside an empty temp directory and chdir's into it.
    Several modules under test resolve paths (config.json, knowledge/,
    plugins/plugins.json, /app/output fallback, etc.) relative to the
    process's current working directory, so isolating cwd per-test prevents
    tests from reading/writing real repo files or bleeding state into each
    other.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def no_env_leak(monkeypatch):
    """
    Strips a known set of config-relevant env vars so tests that check
    default-value fallback behavior aren't accidentally influenced by the
    shell environment the suite happens to run in.
    """
    for key in [
        "PROJECT_NAME", "MODEL_NAME", "AI_FRAMEWORK", "SAFE_OUTPUT_DIR",
        "TOOL_EXEC_TIMEOUT", "KNOWLEDGE_DIR", "MAX_RETRIES", "VERBOSE",
        "MISSION_TIMEOUT_SECONDS", "OPENAI_API_KEY", "TEMPERATURE", "MAX_TOKENS",
    ]:
        monkeypatch.delenv(key, raising=False)
