from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.services.auth import get_current_user, hash_password
from infra.db.models import User


def test_admin_endpoint_requires_authentication() -> None:
    app.dependency_overrides.clear()

    try:
        client = TestClient(app)
        response = client.get("/analytics/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_user_cannot_access_admin_endpoint() -> None:
    user = User(
        username="user1",
        password_hash=hash_password("User@123"),
        full_name="Demo User 1",
        role="user",
        is_active=True,
    )

    async def fake_current_user():
        return user

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = fake_current_user

    try:
        client = TestClient(app)
        response = client.get("/analytics/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_authenticated_user_can_access_taxonomy() -> None:
    user = User(
        username="user1",
        password_hash=hash_password("User@123"),
        full_name="Demo User 1",
        role="user",
        is_active=True,
    )

    async def fake_current_user():
        return user

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = fake_current_user

    try:
        client = TestClient(app)
        response = client.get("/taxonomy")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
