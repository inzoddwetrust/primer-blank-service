"""``python -m app.profile <dir>``: the product's profile, accepted or refused."""

import subprocess
import sys
from pathlib import Path


def validate(directory: Path) -> int:
    return subprocess.run(
        [sys.executable, "-m", "app.profile", str(directory)],
        capture_output=True,
        check=False,
    ).returncode


def test_a_profile_with_ok_is_accepted(tmp_path: Path) -> None:
    (tmp_path / "ok").write_text("ok\n")
    assert validate(tmp_path) == 0


def test_a_profile_without_ok_or_no_directory_is_refused(tmp_path: Path) -> None:
    """Twin EMPTY and LACK: an empty profile, a profile that is not there."""
    assert validate(tmp_path) == 3
    assert validate(tmp_path / "gone") == 3
    (tmp_path / "ok").mkdir()  # a directory named ok is not the file
    assert validate(tmp_path) == 3
