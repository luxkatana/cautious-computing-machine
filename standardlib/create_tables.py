import asyncio
from database import engine, Base, get_db
from models import Helper


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Yes")

asyncio.run(init_models())
