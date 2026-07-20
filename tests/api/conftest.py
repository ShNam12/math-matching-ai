import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from apps.api.main import app
from apps.api.v1.services.auth import get_current_user, require_admin, hash_password
from core.config.settings import settings
from infra.db.models import Document, User


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


@pytest.fixture
def uploaded_document_ids() -> list[str]:
    document_ids: list[str] = []

    yield document_ids

    async def cleanup() -> None:
        if not document_ids:
            return

        engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
        )
        session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        try:
            async with session_factory() as session:
                await session.execute(
                    delete(Document).where(Document.id.in_(document_ids))
                )
                await session.commit()
        finally:
            await engine.dispose()

    asyncio.run(cleanup())
