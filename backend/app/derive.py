"""``python -m app.derive <name>``: a derived value, printed on one line.

The machine runs it in a throwaway container of this image with the stack's
other values in the environment (contract 3 section 3, ``derived``) and takes
stdout as the value. ``service-key`` is a function of ``SERVICE_TOKEN`` alone:
the same token gives the same key, so a run with nothing changed derives
nothing new. Errors go to stderr with a non-zero exit; stdout then is empty.
"""

import hashlib
import hmac
import os
import sys
from collections.abc import Callable, Sequence

PREFIX = "sk_"
LABEL = b"primer-blank-service/service-key"


def service_key(token: str) -> str:
    """``sk_`` and 40 hex digits of an HMAC of ``token``: ``[A-Za-z0-9_-]``."""
    digest = hmac.new(token.encode("utf-8"), LABEL, hashlib.sha256).hexdigest()
    return PREFIX + digest[:40]


DERIVED: dict[str, tuple[str, Callable[[str], str]]] = {
    "service-key": ("SERVICE_TOKEN", service_key),
}


def main(argv: Sequence[str]) -> int:
    if len(argv) != 1 or argv[0] not in DERIVED:
        print(f"usage: python -m app.derive {{{'|'.join(DERIVED)}}}", file=sys.stderr)
        return 2
    variable, derive = DERIVED[argv[0]]
    given = os.environ.get(variable, "")
    if not given:
        print(f"{variable} is not set: nothing to derive from", file=sys.stderr)
        return 2
    print(derive(given))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
