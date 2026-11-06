"""The start of the service is one JSON line with ``ctx`` (protocol 9.4)."""

import json
import logging

import pytest

from primer_report import JsonFormatter
from tests.conftest import RELEASE, client_for, settings

FIELDS = ["ts", "level", "service", "release", "request_id", "event", "msg"]


def test_app_started_names_its_edition_and_provides(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PRIMER_RELEASE", RELEASE)
    caplog.set_level(logging.INFO, logger="app.main")
    for _ in client_for(settings(SERVICE_KEY="")):
        pass
    [started] = [r for r in caplog.records if r.__dict__.get("event") == "app.started"]
    line = json.loads(JsonFormatter(service="primer-blank-service").format(started))
    assert list(line) == [*FIELDS, "ctx"]
    assert line["ctx"] == {
        "edition": "core",
        "provides": ["SERVICE_API_URL", "SERVICE_TOKEN"],
    }
    assert "invented-minted-token" not in json.dumps(line)  # names, never values
