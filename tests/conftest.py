# Force the app to use the test database BEFORE importing anything else
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_database.db"

# Global imports
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from unittest.mock import patch

# Local imports
from app.core.database import get_db
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from app.core.database import Base
from sqlalchemy import select

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"

test_async_engine: AsyncEngine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# Shared session-wide database schema setup
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Seed the database with the rooms and users the tests expect
@pytest_asyncio.fixture(scope="session", autouse=True)
async def seed_test_data(setup_database):
    async with TestAsyncSessionLocal() as session:
        # Import models inside the fixture to avoid circular imports
        from app.modules.users.user_model import User
        from app.modules.rooms.room_model import Room
        
        # Check if users already exist
        res = await session.execute(select(User).where(User.user_id == 1))
        if not res.scalar_one_or_none():
            session.add(User(user_id=1, username="user1", email="u1@test.com", hashed_password="hash", is_active=True))
            session.add(User(user_id=2, username="user2", email="u2@test.com", hashed_password="hash", is_active=True))
            session.add(Room(room_id=42, room_name="Room 42", creator_id=1))
            session.add(Room(room_id=99, room_name="Room 99", creator_id=2))
            await session.commit()
    yield

# Database session fixture - aligned to session scope
@pytest_asyncio.fixture(scope="session")
async def db_session(setup_database):
    async with TestAsyncSessionLocal() as session:
        yield session

# HTTP AsyncClient fixture - aligned to session scope
@pytest_asyncio.fixture(scope="session")
async def client(db_session):
    async def _get_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

# Automatically flushes the Redis cache before every single test execution
@pytest_asyncio.fixture(autouse=True, scope="session")
async def clear_redis():
    from app.api.dependencies import redis_client
    await redis_client.flushdb()
    yield


# This stops the app from actually trying to connect to Gmail during tests
@pytest_asyncio.fixture(autouse=True)
def mock_email_sending():
    with patch("app.modules.users.user_router.send_email_notification") as mock:
        yield mock