"""``python -m app.derive``: one value on stdout, of the machine's form."""

import os
import re
import subprocess
import sys

from app.derive import service_key
from tests.conftest import MINTED

FORM = re.compile(r"^[A-Za-z0-9_-]{16,}$")


def derive(
    *argv: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    given = {"PATH": os.environ["PATH"], **(env or {})}
    return subprocess.run(
        [sys.executable, "-m", "app.derive", *argv],
        capture_output=True,
        text=True,
        env=given,
        check=False,
    )


def test_service_key_is_one_line_of_the_machines_form() -> None:
    done = derive("service-key", env={"SERVICE_TOKEN": MINTED})
    assert done.returncode == 0, done.stderr
    lines = done.stdout.splitlines()
    assert lines == [service_key(MINTED)]
    assert FORM.match(lines[0]) and len(lines[0]) >= 16


def test_the_same_token_gives_the_same_key() -> None:
    """Twin REPEAT: a rerun derives nothing new; another token, another key."""
    first = derive("service-key", env={"SERVICE_TOKEN": MINTED}).stdout
    again = derive("service-key", env={"SERVICE_TOKEN": MINTED}).stdout
    other = derive("service-key", env={"SERVICE_TOKEN": MINTED + "x"}).stdout
    assert first == again != other


def test_no_token_or_an_unknown_name_is_an_error_with_empty_stdout() -> None:
    """Twin LACK: the machine sees a non-zero exit and nothing to take."""
    for done in (
        derive("service-key"),
        derive("bot-url", env={"SERVICE_TOKEN": MINTED}),
    ):
        assert done.returncode == 2 and done.stdout == ""
        assert done.stderr
    assert MINTED not in derive("bot-url", env={"SERVICE_TOKEN": MINTED}).stderr
