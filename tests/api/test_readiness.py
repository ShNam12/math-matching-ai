from fastapi.testclient import TestClient

from apps.api import main as api_main
from apps.api.main import app


class FakeResult:
    pass


class FakeSession:
    def __init__(self) -> None:
        self.executed = []

    async def execute(self, statement):
        self.executed.append(statement)
        return FakeResult()


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def get_collections(self):
        return []

    async def close(self) -> None:
        self.closed = True


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check_returns_dependency_status(monkeypatch) -> None:
    fake_session = FakeSession()
    fake_qdrant = FakeQdrantClient()

    async def override_db_session():
        yield fake_session

    app.dependency_overrides[api_main.get_db_session] = override_db_session
    monkeypatch.setattr(
        api_main,
        "create_qdrant_client",
        lambda: fake_qdrant,
    )

    try:
        client = TestClient(app)
        response = client.get("/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {
            "database": True,
            "qdrant": True,
        },
    }
    assert fake_session.executed
    assert fake_qdrant.closed is True