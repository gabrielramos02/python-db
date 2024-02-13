from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017/")

db_client = AIOEngine(client=client,database="test")

