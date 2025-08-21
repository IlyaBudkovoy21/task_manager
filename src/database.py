import os
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass


ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/task_manager"

engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
