"""Settings of a service as the machine starts it, and its app."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.derive import service_key
from app.main import create_app

RELEASE = "v1.0.0"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
# invented, of the form of a minted value: [A-Za-z0-9_-], 32 and more
MINTED = "invented-minted-token-0000000000000001"


def settings(**change: str) -> Settings:
    """What the machine renders for the service, with ``change`` over it."""
    values = {
        "EDITION": "core",
        "PRIMER_RELEASE": RELEASE,
        "PRIMER_COMMIT": COMMIT,
        "SERVICE_API_URL": "http://primer-blank-service-app:8000",
        "SERVICE_TOKEN": MINTED,
        "SERVICE_KEY": service_key(MINTED),
        "PRODUCT_WEBHOOK_URL": "https://api.example.test/internal/service/webhook",
        **change,
    }
    return Settings.model_validate(values)


def client_for(given: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(given)) as client:
        yield client


@pytest.fixture
def client() -> Iterator[TestClient]:
    yield from client_for(settings())
