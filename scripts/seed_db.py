import asyncio
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Import the core engine and base metadata
from app.core.database import engine, AsyncSessionLocal
from app.models.base import Base

# Import the ORM models
from app.models.tenant import Factory, User
from app.models.inventory import SparePart

# Configure professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """
    Forces the creation of all tables based on our SQLAlchemy models.
    In a true production environment, you would use Alembic migrations.
    For local bootstrapping, this ensures the database is immediately ready.
    """
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables verified.")

async def seed_data():
    """
    Injects a test factory, a test worker, and a realistic catalog of spare parts.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Create the Factory
            factory_id = uuid.uuid4()
            apex_factory = Factory(
                id=factory_id,
                name="Apex Industrial Manufacturing",
                location="Detroit, MI"
            )
            session.add(apex_factory)
            
            # 2. Create the Test User
            user_id = uuid.uuid4()
            test_worker = User(
                id=user_id,
                factory_id=factory_id,
                email="maintenance@apex.com",
                role="worker"
            )
            session.add(test_worker)

            # We purposely set some items to zero stock to test the Procurement Agent
            parts_catalog = [
                SparePart(
                    factory_id=factory_id,
                    sku="SKU-1001",
                    name="Omron Servo Motor G-Series",
                    description="High precision servo motor for robotic arms.",
                    category="Motors",
                    current_stock=2,
                    minimum_threshold=5,
                    location_bin="Aisle 4, Shelf B"
                ),
                SparePart(
                    factory_id=factory_id,
                    sku="SKU-1002",
                    name="Heavy Duty Flange 30mm",
                    description="Standard steel flange for pipe fitting.",
                    category="Mechanical",
                    current_stock=45,
                    minimum_threshold=10,
                    location_bin="Aisle 1, Bin 12"
                ),
                SparePart(
                    factory_id=factory_id,
                    sku="SKU-1003",
                    name="Siemens PLC Controller S7",
                    description="Main logic controller for the primary conveyor.",
                    category="Electronics",
                    current_stock=0, # This will trigger the Procurement Agent
                    minimum_threshold=2,
                    location_bin="Secure Lockbox 3"
                ),
                SparePart(
                    factory_id=factory_id,
                    sku="SKU-1004",
                    name="Polyurethane Conveyor Belt 5m",
                    description="Replacement belt material.",
                    category="Conveyors",
                    current_stock=12,
                    minimum_threshold=5,
                    location_bin="Warehouse Bay 2"
                ),
                SparePart(
                    factory_id=factory_id,
                    sku="SKU-1005",
                    name="High-Temp Industrial Bearing",
                    description="Ceramic bearing for high friction zones.",
                    category="Mechanical",
                    current_stock=8,
                    minimum_threshold=15, # This will also trigger Procurement
                    location_bin="Aisle 4, Shelf A"
                )
            ]
            
            session.add_all(parts_catalog)
            
            await session.commit()
            logger.info(f"Successfully seeded database!")
            logger.info(f"Test Factory ID: {factory_id}")
            logger.info(f"Test User ID: {user_id}")
            logger.info("Please copy these IDs to use in your API requests.")

        except IntegrityError:
            await session.rollback()
            logger.warning("Data already exists in the database. Seeding skipped.")
        except Exception as e:
            await session.rollback()
            logger.error(f"An error occurred during seeding: {str(e)}")

async def main():
    await init_db()
    await seed_data()

if __name__ == "__main__":
    # Execute the async loop
    asyncio.run(main())