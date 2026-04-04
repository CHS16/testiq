from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME

# Create global motor client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def get_database():
    """Returns the database instance."""
    return db

def get_interactions_collection():
    """Returns the interactions collection."""
    return db["call_logs"]
