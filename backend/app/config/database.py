"""
Database connection and management for MongoDB.
Using Motor for async operations with MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config import get_settings


class Database:
    """MongoDB database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_db(cls):
        """Establish database connection."""
        settings = get_settings()
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.db = cls.client[settings.mongodb_db_name]
        print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
    
    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            print("❌ Closed MongoDB connection")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.db


# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to inject database."""
    return Database.get_db()