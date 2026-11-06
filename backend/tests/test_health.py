"""``/health`` and ``/ready`` of a service without a database (protocol 9)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import PROVIDES
from primer_report import Health
from tests.conftest import COMMIT, RELEASE, client_for, settings

# Protocol 9.1, written out here and not taken from the model.
FIELDS_11 = {
    "service",
    "release",
    "commit",
    "alembic_head",
    "uptime_s",
    "status",
    "checks",
    "seams",
    "limits",
    "edition",
    "modules",
}
# primer.yaml's provides, written out: a name the code loses must fail here.
NAMES = ["SERVICE_API_URL", "SERVICE_TOKEN", "SERVICE_KEY"]


def test_health_of_a_service_with_every_seam(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body) - {"details"} == FIELDS_11
    Health.model_validate(body)
    assert (body["service"], body["release"], body["commit"]) == (
        "primer-blank-service",
        RELEASE,
        COMMIT,
    )
    assert body["alembic_head"] is None  # no database: protocol 9.1
    assert body["checks"] == {"config": "ok"} and body["status"] == "ok"
    assert body["seams"] == {"provides": NAMES, "requires_satisfied": True}
    assert body["details"] == {"provides": 3, "profile": False}
    assert list(PROVIDES) == NAMES
    assert client.get("/ready").json() == {"status": "ready", "failing": []}


def test_requires_satisfied_follows_the_products_webhook() -> None:
    """Twin LACK: no webhook from the product -- not satisfied, degraded."""
    for client in client_for(settings(PRODUCT_WEBHOOK_URL="")):
        body = client.get("/health").json()
        assert body["seams"]["requires_satisfied"] is False
        assert body["checks"] == {"config": "error"}
        assert body["status"] == "degraded"
        ready = client.get("/ready")
        assert (ready.status_code, ready.json()["failing"]) == (503, ["config"])


@pytest.mark.parametrize("missing", NAMES)
def test_provides_names_only_the_values_that_came(missing: str) -> None:
    """Twin EMPTY: a provide without its value is not reported as provided."""
    for client in client_for(settings(**{missing: ""})):
        body = client.get("/health").json()
        assert body["seams"]["provides"] == [n for n in NAMES if n != missing]
        assert body["status"] == "degraded"


def test_a_key_that_is_not_the_tokens_is_a_red_config() -> None:
    """The derived key is checked against the token it is derived from."""
    for client in client_for(settings(SERVICE_KEY="sk_" + "0" * 40)):
        body = client.get("/health").json()
        assert body["checks"] == {"config": "error"}
        assert body["seams"]["provides"] == NAMES  # it came; it is wrong


def test_details_say_whether_the_profile_is_mounted(tmp_path: Path) -> None:
    for client in client_for(settings(PROFILE_DIR=str(tmp_path))):
        assert client.get("/health").json()["details"]["profile"] is True
