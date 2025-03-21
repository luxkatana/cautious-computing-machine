from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ
from dotenv import load_dotenv

load_dotenv()

DB_URL = environ['MYSQL_URI']

engine: AsyncEngine = create_async_engine(DB_URL, echo=True)

SessionLocal = sessionmaker(engine,
                            class_=AsyncSession,
                            expire_on_commit=False)


Base = declarative_base()
try:
    from standardlib import models # noqa
except Exception:
    import models # noqa

async def get_db():
    async with SessionLocal() as session:
        yield session

async def close_engine() -> None:
    await engine.dispose()
