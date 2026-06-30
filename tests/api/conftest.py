import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.services.auth import get_current_user, require_admin, hash_password
from infra.db.models import User


@pytest.fixture(autouse=True)
def authenticated_api_user():
    user = User(
        username="admin",
        password_hash=hash_password("Admin@123"),
        full_name="Administrator",
        role="admin",
        is_active=True,
    )

    async def fake_current_user():
        return user

    async def fake_admin_user():
        return user

    app.dependency_overrides[get_current_user] = fake_current_user
    app.dependency_overrides[require_admin] = fake_admin_user

    yield

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
