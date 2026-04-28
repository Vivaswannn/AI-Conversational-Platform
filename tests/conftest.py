import os
import pytest_asyncio
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database import Base
from app.dependencies import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.ai.chain.ChatOpenAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm_cls.return_value = mock_llm

        async def mock_astream(*args, **kwargs):
            for token in ["Hello", " there", "!"]:
                from langchain_core.messages import AIMessageChunk
                yield AIMessageChunk(content=token)

        mock_llm.astream = mock_astream

        with patch("app.ai.rag.get_rag_engine") as mock_rag_module, \
             patch("app.services.chat_service.get_rag_engine") as mock_rag_service:
            mock_rag_module.return_value.query.return_value = ["Relevant mental health info"]
            mock_rag_service.return_value.query.return_value = ["Relevant mental health info"]

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    resp = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert resp.status_code == 201
    return {"token": resp.json()["access_token"], "email": "test@example.com"}
