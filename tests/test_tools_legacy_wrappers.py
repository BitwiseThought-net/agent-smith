"""
file_read.py, file_write.py, terminal.py, and search_duckduckgo.py are thin
get_tools() wrappers around classes provided by the active ai_layer adapter
(here, our fake orchestrator from conftest). They carry no real logic of
their own beyond "instantiate and return in a list", but they're still
exercised code paths - e.g. team.json can reference these tool names
directly - so we confirm each one wires up correctly.
"""
from tools import file_read, file_write, terminal, search_duckduckgo
from ai_layer.orchestrator import (
    FileReadTool,
    FileWriterTool,
    EXECTool,
    DuckDuckGoSearchTool,
)


def test_file_read_get_tools_returns_one_file_read_tool_instance():
    tools_list = file_read.get_tools()
    assert len(tools_list) == 1
    assert isinstance(tools_list[0], FileReadTool)


def test_file_write_get_tools_returns_one_file_writer_tool_instance():
    tools_list = file_write.get_tools()
    assert len(tools_list) == 1
    assert isinstance(tools_list[0], FileWriterTool)


def test_search_duckduckgo_get_tools_returns_one_search_tool_instance():
    tools_list = search_duckduckgo.get_tools()
    assert len(tools_list) == 1
    assert isinstance(tools_list[0], DuckDuckGoSearchTool)


class TestTerminalGetTools:
    def test_returns_one_exec_tool_instance_when_available(self):
        tools_list = terminal.get_tools()
        assert len(tools_list) == 1
        assert isinstance(tools_list[0], EXECTool)

    def test_returns_empty_list_when_exectool_unavailable(self, monkeypatch):
        # Simulates a framework adapter that doesn't provide shell execution
        # at all (EXECTool = None), which terminal.py explicitly guards
        # against to avoid a runtime crash.
        monkeypatch.setattr(terminal, "EXECTool", None)
        assert terminal.get_tools() == []
