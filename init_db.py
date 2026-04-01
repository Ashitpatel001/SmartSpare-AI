import asyncio
from app.core.database import engine
from app.models.base import Base
from app.core.config import settings

from app.models.tenant import Factory, User
from app.models.inventory import SparePart, InventoryTransaction

async def create_tables():
    print(f"Connecting to PostgreSQL at {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}...")
    try:
        async with engine.begin() as conn:
            print("Dropping old tables and creating new ones...")
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"\nCRITICAL CONNECTION FAILURE: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())