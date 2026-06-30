from datetime import timedelta

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import auth as auth_endpoint
from apps.api.v1.services import auth as auth_service
from infra.db.models import User
from infra.db.session import get_db_session


def test_password_hash_verification() -> None:
    password_hash = auth_service.hash_password("Admin@123")

    assert password_hash != "Admin@123"
    assert auth_service.verify_password("Admin@123", password_hash) is True
    assert auth_service.verify_password("wrong-password", password_hash) is False


def test_access_token_roundtrip() -> None:
    token = auth_service.create_access_token(
        subject="admin",
        role="admin",
        expires_delta=timedelta(minutes=5),
    )

    payload = auth_service.decode_access_token(token)

    assert payload["sub"] == "admin"
    assert payload["role"] == "admin"


def test_login_returns_access_token(monkeypatch) -> None:
    user = User(
        username="admin",
        password_hash=auth_service.hash_password("Admin@123"),
        full_name="Administrator",
        role="admin",
        is_active=True,
    )

    async def fake_authenticate_user(*, session, username: str, password: str):
        assert username == "admin"
        assert password == "Admin@123"
        return user

    async def fake_db_session():
        yield object()

    monkeypatch.setattr(
        auth_endpoint,
        "authenticate_user",
        fake_authenticate_user,
    )
    app.dependency_overrides[get_db_session] = fake_db_session

    try:
        client = TestClient(app)
        response = client.post(
            "/auth/login",
            json={
                "username": "admin",
                "password": "Admin@123",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"] == {
        "username": "admin",
        "full_name": "Administrator",
        "role": "admin",
        "is_active": True,
    }


def test_me_returns_current_user() -> None:
    user = User(
        username="user1",
        password_hash=auth_service.hash_password("User@123"),
        full_name="Demo User 1",
        role="user",
        is_active=True,
    )

    async def fake_current_user():
        return user

    app.dependency_overrides[auth_endpoint.get_current_user] = fake_current_user

    try:
        client = TestClient(app)
        response = client.get("/auth/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "username": "user1",
        "full_name": "Demo User 1",
        "role": "user",
        "is_active": True,
    }

