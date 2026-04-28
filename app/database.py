from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_AsyncSessionLocal = None


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, creating the engine exactly once."""
    global _engine, _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        _AsyncSessionLocal = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency-injection-friendly session generator."""
    factory = _get_session_factory()
    async with factory() as session:
        yield session


# Backwards-compatible name used by dependencies.py
class AsyncSessionLocal:
    """Proxy that delegates __call__ to the lazily created session factory."""
    def __new__(cls):  # type: ignore[override]
        return _get_session_factory()()

    def __class_getitem__(cls, item):  # support `async with AsyncSessionLocal() as s:`
        return _get_session_factory()().__class_getitem__(item)

