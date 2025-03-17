import os

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.environ.get("DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@postgres:5432/fundus"

engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))


async def init_db():
    pass


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
