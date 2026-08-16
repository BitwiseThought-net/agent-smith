import pytest
import requests

from tools.github_repo_tool import Tools, SKIP_DIRS, SKIP_EXTS


@pytest.fixture
def tools():
    return Tools()


class TestParseRepoUrl:
    def test_simple_https_url(self, tools):
        owner, repo, branch = tools._parse_repo_url("https://github.com/anthropics/claude")
        assert (owner, repo, branch) == ("anthropics", "claude", None)

    def test_url_with_git_suffix(self, tools):
        owner, repo, branch = tools._parse_repo_url("https://github.com/anthropics/claude.git")
        assert (owner, repo, branch) == ("anthropics", "claude", None)

    def test_url_with_branch_tree_path(self, tools):
        owner, repo, branch = tools._parse_repo_url(
            "https://github.com/anthropics/claude/tree/feature-branch"
        )
        assert (owner, repo, branch) == ("anthropics", "claude", "feature-branch")

    def test_non_github_url_returns_none_triple(self, tools):
        assert tools._parse_repo_url("https://gitlab.com/anthropics/claude") == (None, None, None)

    def test_garbage_input_returns_none_triple(self, tools):
        assert tools._parse_repo_url("not a url at all") == (None, None, None)


class TestHeaders:
    def test_no_token_omits_authorization(self, tools):
        headers = tools._headers()
        assert "Authorization" not in headers

    def test_token_adds_authorization_bearer(self, tools):
        tools.valves.GITHUB_TOKEN = "secret123"
        headers = tools._headers()
        assert headers["Authorization"] == "Bearer secret123"


class TestReadGithubRepository:
    def test_unparseable_url_short_circuits_without_network(self, tools, monkeypatch):
        def fail_if_called(*a, **kw):
            raise AssertionError("requests.get should not be called for an unparseable URL")
        monkeypatch.setattr(requests, "get", fail_if_called)
        result = tools.read_github_repository("not-a-github-url")
        assert "Could not parse" in result

    def test_repo_metadata_fetch_failure_returns_error_string(self, tools, monkeypatch):
        class FakeResp:
            status_code = 404
            text = "Not Found"
        monkeypatch.setattr(requests, "get", lambda *a, **kw: FakeResp())
        result = tools.read_github_repository("https://github.com/owner/repo")
        assert "Error fetching repo metadata" in result

    def test_network_exception_is_caught(self, tools, monkeypatch):
        def boom(*a, **kw):
            raise requests.ConnectionError("no network")
        monkeypatch.setattr(requests, "get", boom)
        result = tools.read_github_repository("https://github.com/owner/repo")
        assert "Error contacting GitHub API" in result

    def test_filters_skip_dirs_and_skip_exts_and_builds_digest(self, tools, monkeypatch):
        calls = {"n": 0}

        class FakeRepoMetaResp:
            status_code = 200
            def json(self):
                return {"default_branch": "main"}

        class FakeTreeResp:
            status_code = 200
            def json(self):
                return {"tree": [
                    {"type": "blob", "path": "src/app.py", "size": 100},
                    {"type": "blob", "path": "node_modules/lib.js", "size": 50},
                    {"type": "blob", "path": "assets/logo.png", "size": 200},
                    {"type": "blob", "path": "huge_file.py", "size": 999_999},
                    {"type": "tree", "path": "src"},  # not a blob, should be skipped
                ]}

        class FakeRawResp:
            status_code = 200
            text = "print('hello')"

        def fake_get(url, headers=None, timeout=None, **kw):
            calls["n"] += 1
            if "raw.githubusercontent.com" in url:
                return FakeRawResp()
            if "/git/trees/" in url:
                return FakeTreeResp()
            return FakeRepoMetaResp()

        monkeypatch.setattr(requests, "get", fake_get)

        result = tools.read_github_repository("https://github.com/owner/repo")

        assert "src/app.py" in result
        assert "node_modules/lib.js" not in result
        assert "assets/logo.png" not in result
        assert "huge_file.py" not in result  # excluded: size > 200_000
        assert "Repository: owner/repo (branch: main)" in result
        assert "[Included 1 of 1 candidate files]" in result

    def test_max_files_valve_limits_included_file_count(self, tools, monkeypatch):
        tools.valves.MAX_FILES = 1

        class FakeRepoMetaResp:
            status_code = 200
            def json(self):
                return {"default_branch": "main"}

        class FakeTreeResp:
            status_code = 200
            def json(self):
                return {"tree": [
                    {"type": "blob", "path": "a.py", "size": 10},
                    {"type": "blob", "path": "b.py", "size": 10},
                ]}

        class FakeRawResp:
            status_code = 200
            text = "x = 1"

        def fake_get(url, headers=None, timeout=None, **kw):
            if "raw.githubusercontent.com" in url:
                return FakeRawResp()
            if "/git/trees/" in url:
                return FakeTreeResp()
            return FakeRepoMetaResp()

        monkeypatch.setattr(requests, "get", fake_get)
        result = tools.read_github_repository("https://github.com/owner/repo")
        assert "[Included 1 of 2 candidate files]" in result
