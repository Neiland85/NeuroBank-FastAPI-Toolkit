from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from .config import get_settings

Base = declarative_base()


def get_database_url() -> str:
    settings = get_settings()
    return settings.database_url


engine = create_async_engine(get_database_url(), echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        # Importación diferida para evitar ciclos
        from . import models  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan_state():
    await init_db()
    try:
        yield
    finally:
        # Lugar para limpiezas futuras (conexiones, pools, etc.)
        await engine.dispose()


import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()


# DATABASE_URL examples:
# - AsyncPG (prod): postgresql+asyncpg://user:pass@host:5432/dbname
# - SQLite (dev): sqlite+aiosqlite:///./app.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")


engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    """Crea las tablas si no existen (útil para desarrollo y tests)."""
    # Importación tardía para registrar modelos antes de create_all
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
