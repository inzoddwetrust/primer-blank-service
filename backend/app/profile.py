"""``python -m app.profile <dir>``: the ``validate`` of the product's profile.

The machine runs it in a throwaway container of the new image on the copy of
the product's ``profile/`` before the service restarts on it (protocol 4.5).
A profile is accepted when it has a file ``ok``; any other is refused with
code 3 -- the shape of a check that tells good data from bad, nothing more.
"""

import sys
from collections.abc import Sequence
from pathlib import Path

REFUSED = 3


def main(argv: Sequence[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m app.profile <dir>", file=sys.stderr)
        return 2
    marker = Path(argv[0]) / "ok"
    if not marker.is_file():
        print(f"profile refused: {marker} is not a file", file=sys.stderr)
        return REFUSED
    print(f"profile accepted: {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
