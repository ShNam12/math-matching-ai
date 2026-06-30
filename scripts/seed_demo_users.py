import asyncio
import sys
from pathlib import Path
from typing import TypedDict

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.v1.services.auth import hash_password
from infra.db.base import Base
from infra.db.models import User
from infra.db.session import AsyncSessionLocal, engine


class DemoUserSpec(TypedDict):
    username: str
    password: str
    full_name: str
    role: str


DEMO_USERS: tuple[DemoUserSpec, ...] = (
    {
        "username": "admin",
        "password": "Admin@123",
        "full_name": "Administrator",
        "role": "admin",
    },
    {
        "username": "user1",
        "password": "User@123",
        "full_name": "Demo User 1",
        "role": "user",
    },
    {
        "username": "user2",
        "password": "User@123",
        "full_name": "Demo User 2",
        "role": "user",
    },
    {
        "username": "user3",
        "password": "User@123",
        "full_name": "Demo User 3",
        "role": "user",
    },
)


async def ensure_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_demo_users() -> None:
    async with AsyncSessionLocal() as session:
        for spec in DEMO_USERS:
            result = await session.execute(
                select(User).where(User.username == spec["username"])
            )
            user = result.scalar_one_or_none()

            if user is None:
                session.add(
                    User(
                        username=spec["username"],
                        password_hash=hash_password(spec["password"]),
                        full_name=spec["full_name"],
                        role=spec["role"],
                        is_active=True,
                    )
                )
                print(f"Created user: {spec['username']}")
                continue

            user.password_hash = hash_password(spec["password"])
            user.full_name = spec["full_name"]
            user.role = spec["role"]
            user.is_active = True
            print(f"Updated user: {spec['username']}")

        await session.commit()


async def main() -> None:
    await ensure_tables()
    await seed_demo_users()
    await engine.dispose()
    print("Seed demo users completed.")


if __name__ == "__main__":
    asyncio.run(main())

