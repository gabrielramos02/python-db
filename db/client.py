from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
import os
client = AsyncIOMotorClient(os.environ.get("BD_STRING")

db_client = AIOEngine(client=client,database="test")

