import pytest
from httpx import AsyncClient,ASGITransport

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

@pytest.fixture(scope="function")
async def db_session():
    async with test_async_engine.begin() as conn: #type: ignore
       await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_async_engine.begin() as conn: #type: ignore
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    async def _get_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
