from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite+aiosqlite:///main.db"

engine = create_async_engine(DB_URL, echo=True)

SessionLocal = sessionmaker(engine,
                            class_=AsyncSession,
                            expire_on_commit=False)


Base = declarative_base()
async def get_db():
    async with SessionLocal() as session:
        yield session
