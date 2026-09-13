from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db import engine

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
