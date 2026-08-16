import time
import requests
import pytest

import main


class FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data


def test_returns_immediately_when_model_already_ready(monkeypatch):
    calls = {"n": 0}

    def fake_get(url, timeout=None):
        calls["n"] += 1
        return FakeResponse(200, {"data": [{"id": "ollama/mymodel"}]})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    main.wait_for_llm("http://litellm:4000", "mymodel")
    assert calls["n"] == 1


def test_retries_until_model_appears(monkeypatch):
    responses = [
        FakeResponse(200, {"data": []}),
        FakeResponse(200, {"data": []}),
        FakeResponse(200, {"data": [{"id": "ollama/mymodel"}]}),
    ]

    def fake_get(url, timeout=None):
        return responses.pop(0)

    sleep_calls = {"n": 0}
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.__setitem__("n", sleep_calls["n"] + 1))
    main.wait_for_llm("http://litellm:4000", "mymodel")
    assert responses == []
    assert sleep_calls["n"] == 2


def test_non_200_response_is_treated_as_not_ready(monkeypatch):
    responses = [FakeResponse(503), FakeResponse(200, {"data": [{"id": "ollama/mymodel"}]})]

    def fake_get(url, timeout=None):
        return responses.pop(0)

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    main.wait_for_llm("http://litellm:4000", "mymodel")
    assert responses == []


def test_connection_exception_is_swallowed_and_retried(monkeypatch):
    attempts = {"n": 0}

    def fake_get(url, timeout=None):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise requests.ConnectionError("litellm not up yet")
        return FakeResponse(200, {"data": [{"id": "ollama/mymodel"}]})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    main.wait_for_llm("http://litellm:4000", "mymodel")
    assert attempts["n"] == 3


def test_raises_timeout_error_after_600_seconds(monkeypatch):
    # Simulate time marching forward past the 600s ceiling without the
    # model ever showing up in the response.
    fake_clock = {"t": 1_000_000.0}

    def fake_time():
        return fake_clock["t"]

    def fake_sleep(seconds):
        fake_clock["t"] += 601  # jump straight past the deadline on first sleep

    monkeypatch.setattr(requests, "get", lambda url, timeout=None: FakeResponse(200, {"data": []}))
    monkeypatch.setattr(time, "time", fake_time)
    monkeypatch.setattr(time, "sleep", fake_sleep)

    with pytest.raises(TimeoutError, match="LiteLLM timeout for mymodel"):
        main.wait_for_llm("http://litellm:4000", "mymodel")


def test_calls_update_heartbeat_on_every_iteration(monkeypatch):
    heartbeat_calls = {"n": 0}
    monkeypatch.setattr(main, "update_heartbeat", lambda: heartbeat_calls.__setitem__("n", heartbeat_calls["n"] + 1))
    monkeypatch.setattr(requests, "get", lambda url, timeout=None: FakeResponse(200, {"data": [{"id": "ollama/m"}]}))
    monkeypatch.setattr(time, "sleep", lambda s: None)
    main.wait_for_llm("http://litellm:4000", "m")
    assert heartbeat_calls["n"] == 1
