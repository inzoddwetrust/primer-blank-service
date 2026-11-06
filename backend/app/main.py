"""The ASGI application: ``uvicorn --factory app.main:create_app``.

A service of protocol 4 without a database: ``alembic_head`` is ``null``
(protocol 9.1). Its seams are reported as they are -- ``seams.provides``
names the provides whose values came, ``requires_satisfied`` says whether the
product's webhook came -- and its one check, ``config``, is measured from
memory: every value came and ``SERVICE_KEY`` is the key of ``SERVICE_TOKEN``.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import Settings
from app.derive import service_key
from primer_report import Limits, PrimerReport, Seams

SERVICE = "primer-blank-service"

# The provides of primer.yaml and the variable that carries each.
PROVIDES = {
    "SERVICE_API_URL": "api_url",
    "SERVICE_TOKEN": "token",
    "SERVICE_KEY": "key",
}

# The largest request body the service accepts, reported in /health.limits.
MAX_UPLOAD_MB = 1

logger = logging.getLogger(__name__)


def provided(settings: Settings) -> list[str]:
    """The provides whose values the service has, in primer.yaml's order."""
    return [name for name, field in PROVIDES.items() if getattr(settings, field)]


def consistent(settings: Settings) -> bool:
    """Every value came, and the derived key is the token's."""
    return (
        len(provided(settings)) == len(PROVIDES)
        and bool(settings.webhook)
        and settings.key == service_key(settings.token)
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the app; settings default to the environment."""
    settings = settings or Settings()
    names = provided(settings)
    profile = bool(settings.profile_dir) and Path(settings.profile_dir).is_dir()
    healthy = consistent(settings)

    async def config() -> bool:
        return healthy

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "edition %s, %d of %d provides",
            settings.edition,
            len(names),
            len(PROVIDES),
            extra={
                "event": "app.started",
                "ctx": {"edition": settings.edition, "provides": list(names)},
            },
        )
        yield

    app = FastAPI(title=SERVICE, lifespan=lifespan)
    report = PrimerReport(
        service=SERVICE,
        release=settings.release,
        commit=settings.commit,
        edition=settings.edition,
        modules=[],
        limits=Limits(max_upload_mb=MAX_UPLOAD_MB),
        seams=Seams(provides=names, requires_satisfied=bool(settings.webhook)),
        checks={"config": config},
        details=lambda: {"provides": len(names), "profile": profile},
    )
    report.install(app)
    return app
