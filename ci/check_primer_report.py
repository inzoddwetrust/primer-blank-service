"""``backend/primer_report`` is the blank's, byte for byte.

    python ci/check_primer_report.py <primer-blank checkout>
    python ci/check_primer_report.py <primer-blank checkout> --selftest

``primer_report`` lives in one place: ``primer-blank/backend/primer_report``
(protocol 9.1, its ready model). The service carries a copy; this check
compares every file of the copy with the blank's at the commit CI checks out
(``PRIMER_BLANK_COMMIT``), so the copy cannot drift without a red CI.

``--selftest`` first requires the copy to pass, then plants defects in
copies of it -- a changed line, a file gone, a file added -- each of which
must be refused.
"""

import argparse
import shutil
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = Path("backend/primer_report")


def files(directory: Path) -> dict[str, bytes]:
    """Every file of ``directory`` by its relative path; caches left out."""
    return {
        str(path.relative_to(directory)): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def differences(copy: Path, blank: Path) -> list[str]:
    """What tells the copy from the blank's package, one line each."""
    ours, theirs = files(copy), files(blank)
    if not theirs:
        return [f"{blank}: no files -- nothing to compare with"]
    out = [f"{name}: not in the copy" for name in sorted(set(theirs) - set(ours))]
    out += [f"{name}: not in the blank" for name in sorted(set(ours) - set(theirs))]
    out += [
        f"{name}: differs from the blank's"
        for name in sorted(set(ours) & set(theirs))
        if ours[name] != theirs[name]
    ]
    return out


def check(blank_root: Path) -> int:
    found = differences(ROOT / PACKAGE, blank_root / PACKAGE)
    for line in found:
        print(line, file=sys.stderr)
    if not found:
        count = len(files(ROOT / PACKAGE))
        print(f"{PACKAGE}: {count} files, each the blank's")
    return 1 if found else 0


def _changed(copy: Path) -> None:
    health = copy / "health.py"
    health.write_text(health.read_text(encoding="utf-8") + "# drift\n")


def _gone(copy: Path) -> None:
    (copy / "logs.py").unlink()


def _added(copy: Path) -> None:
    (copy / "extra.py").write_text("X = 1\n", encoding="utf-8")


DEFECTS: dict[str, Callable[[Path], None]] = {
    "a changed line": _changed,
    "a file gone": _gone,
    "a file added": _added,
}


def selftest(blank_root: Path) -> int:
    """The copy must pass; each planted defect, in a copy of it, must not."""
    if check(blank_root) != 0:
        print("selftest: the copy itself does not pass", file=sys.stderr)
        return 1
    passed: list[str] = []
    for name, plant in DEFECTS.items():
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "primer_report"
            shutil.copytree(ROOT / PACKAGE, copy)
            plant(copy)
            found = differences(copy, blank_root / PACKAGE)
        if found:
            print(f"selftest: {name!r} refused: {found[0]}")
        else:
            passed.append(name)
    for name in passed:
        print(f"selftest: planted defect {name!r} passed", file=sys.stderr)
    return 1 if passed else 0


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(prog="python ci/check_primer_report.py")
    parser.add_argument("blank", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    blank: Path = args.blank
    return selftest(blank) if args.selftest else check(blank)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
