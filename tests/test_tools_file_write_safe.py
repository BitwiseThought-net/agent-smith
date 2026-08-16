import json
import os
import pytest

from tools.file_write_safe import file_write_safe, get_tools


class TestFileWriteSafe:
    def test_writes_file_inside_default_sandbox(self, isolated_cwd, no_env_leak, monkeypatch):
        sandbox = isolated_cwd / "output"
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))
        result = file_write_safe.func("notes.txt", "hello world") \
            if hasattr(file_write_safe, "func") else file_write_safe("notes.txt", "hello world")
        assert "Success" in result
        assert (sandbox / "notes.txt").read_text() == "hello world"

    def test_creates_sandbox_dir_if_missing(self, isolated_cwd, no_env_leak, monkeypatch):
        sandbox = isolated_cwd / "does" / "not" / "exist"
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))
        assert not sandbox.exists()
        _call(sandbox, "a.txt", "content")
        assert sandbox.exists()
        assert (sandbox / "a.txt").read_text() == "content"

    @pytest.mark.parametrize("bad_filename", [
        "../escape.txt",
        "../../etc/passwd",
        "subdir/../../escape.txt",
        "/etc/passwd",
        "/absolute/path.txt",
    ])
    def test_blocks_path_traversal_and_absolute_paths(self, isolated_cwd, no_env_leak, monkeypatch, bad_filename):
        sandbox = isolated_cwd / "output"
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))
        result = _call(sandbox, bad_filename, "malicious content")
        assert "Security Violation" in result
        # Nothing should have been written anywhere as a result of the call
        if sandbox.exists():
            assert list(sandbox.rglob("*")) == []

    def test_overwrites_existing_file(self, isolated_cwd, no_env_leak, monkeypatch):
        sandbox = isolated_cwd / "output"
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))
        _call(sandbox, "same.txt", "first")
        _call(sandbox, "same.txt", "second")
        assert (sandbox / "same.txt").read_text() == "second"

    def test_returns_error_string_not_exception_on_write_failure(self, isolated_cwd, no_env_leak, monkeypatch):
        sandbox = isolated_cwd / "output"
        sandbox.mkdir()
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))
        # Writing to a filename that collides with an existing directory
        # should fail at open() and be caught, not raise.
        (sandbox / "is_a_dir").mkdir()
        result = _call(sandbox, "is_a_dir", "content")
        assert "File Write Error" in result


    def test_returns_error_string_when_sandbox_dir_cannot_be_created(self, isolated_cwd, no_env_leak, monkeypatch):
        sandbox = isolated_cwd / "unmakeable"
        monkeypatch.setenv("SAFE_OUTPUT_DIR", str(sandbox))

        def boom(*a, **kw):
            raise PermissionError("no permission")
        monkeypatch.setattr(os, "makedirs", boom)

        result = _call(sandbox, "a.txt", "content")
        assert "System Error" in result

    def test_get_tools_returns_the_tool_function(self):
        tools_list = get_tools()
        assert tools_list == [file_write_safe]


def _call(sandbox, filename, content):
    """Helper to call the tool whether or not the @tool decorator wraps it
    in something that requires unwrapping via .func (depends on the fake
    orchestrator's tool decorator, which passes the function through as-is)."""
    fn = file_write_safe.func if hasattr(file_write_safe, "func") else file_write_safe
    return fn(filename, content)
