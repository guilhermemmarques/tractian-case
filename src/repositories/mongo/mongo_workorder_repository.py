import asyncio
import logging
from typing import Optional, Self
from motor.motor_asyncio import AsyncIOMotorClient

from src.models.tracOS_models import TracOSWorkorderModel
from src.repositories.workorder_repository import WorkOrderRepository

log = logging.getLogger(__name__)


class MongoWorkOrderRepository(WorkOrderRepository):
    def __init__(
        self,
        collection_name: str,
        database_url: str = "mongodb://localhost:27017",
        database_name: str = "tractian",
    ):
        self.client = AsyncIOMotorClient(database_url)
        self.collection = self.client[database_name][collection_name]

    async def connect_with_retries(
        self, max_retries: int = 5, delay: int = 2
    ) -> Optional[Self]:
        """Attempt to connect to the MongoDB database with retries."""

        for attempt in range(max_retries):
            try:
                await self.client.admin.command("ping")
                log.info("Successfully connected to MongoDB.")
                return self
            except Exception as e:
                log.warning(
                    f"Failed to connect to MongoDB (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    log.info(f"Retrying connection in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    log.error("Exceeded maximum connection attempts to MongoDB.")
                    raise ConnectionError(
                        "Could not connect to MongoDB after multiple attempts."
                    ) from e

    async def find_by_field(
        self, field: str, value: str
    ) -> Optional[TracOSWorkorderModel]:
        document = await self.collection.find_one({field: value})
        return TracOSWorkorderModel.model_validate(document) if document else None

    async def insert(self, entity: TracOSWorkorderModel) -> TracOSWorkorderModel:
        data = entity.model_dump()

        await self.collection.insert_one(data)
        return entity

    async def update(
        self, number: int, entity: TracOSWorkorderModel
    ) -> Optional[TracOSWorkorderModel]:
        data = entity.model_dump()
        result = await self.collection.update_one({"number": number}, {"$set": data})
        return entity if result.modified_count > 0 else None

    async def find_is_synced_workorders(
        self, is_synced: bool = True
    ) -> list[TracOSWorkorderModel]:
        cursor = self.collection.find({"isSynced": is_synced})
        workorders = []
        async for document in cursor:
            workorders.append(TracOSWorkorderModel.model_validate(document))
        return workorders
