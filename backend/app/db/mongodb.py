"""
MongoDB connection manager using Motor (async driver).
Connect to local MongoDB instance — visible via MongoDB Compass.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Initialize MongoDB connection on app startup."""
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]

    # Test connection
    try:
        await mongodb.client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise

    # Create indexes
    await create_indexes()


async def close_mongo_connection():
    """Close MongoDB connection on app shutdown."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed.")


async def create_indexes():
    """Create database indexes for performance."""
    try:
        # Products
        await mongodb.db.products.create_index("slug", unique=True)
        await mongodb.db.products.create_index("brand_id")
        await mongodb.db.products.create_index("category")
        await mongodb.db.products.create_index([("name", "text"), ("description_raw", "text")])

        # Ingredients
        await mongodb.db.ingredients.create_index("name", unique=True)
        await mongodb.db.ingredients.create_index("type")

        # Users
        await mongodb.db.users.create_index("email", unique=True)

        # Brands
        await mongodb.db.brands.create_index("slug", unique=True)

        # Chat history
        await mongodb.db.chat_history.create_index("user_id")
        await mongodb.db.chat_history.create_index("session_id")

        logger.info("✅ Database indexes created.")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance for use in routes."""
    return mongodb.db
