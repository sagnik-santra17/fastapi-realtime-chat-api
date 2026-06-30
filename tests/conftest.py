# Global imports
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Local imports
from app.core.database import get_db
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from app.core.database import Base

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