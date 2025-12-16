from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Self

from src.models.tracOS_models import TracOSWorkorderModel

T = TypeVar("T")  # Generic type for models


class WorkOrderRepository(ABC, Generic[T]):
    @abstractmethod
    async def connect_with_retries(self, max_retries: int = 5, delay: int = 2) -> Self:
        ...

    @abstractmethod
    async def find_by_field(
        self, field: str, value: str
    ) -> Optional[TracOSWorkorderModel]:
        ...

    @abstractmethod
    async def insert(self, entity: TracOSWorkorderModel) -> TracOSWorkorderModel:
        ...

    @abstractmethod
    async def update(
        self, number: int, entity: TracOSWorkorderModel
    ) -> Optional[TracOSWorkorderModel]:
        ...

    @abstractmethod
    async def find_is_synced_workorders(
        self, is_synced: bool
    ) -> list[TracOSWorkorderModel]:
        ...
