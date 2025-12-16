from .mongo.mongo_workorder_repository import MongoWorkOrderRepository
import logging

log = logging.getLogger(__name__)


class RepositoryFactory:
    """Factory class to create and return repository instances."""

    @staticmethod
    async def get_workorder_repository() -> MongoWorkOrderRepository:
        """Creates and returns a connected MongoWorkOrderRepository instance."""
        try:
            repository = MongoWorkOrderRepository(
                collection_name="workorders",
                database_url="mongodb://localhost:27017",
                database_name="tractian",
            )
            await repository.connect_with_retries()
            return repository
        except Exception as e:
            log.error(f"Failed to create MongoWorkOrderRepository: {e}")
            raise
