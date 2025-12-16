from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TracOSWorkOrderStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class TracOSWorkorderModel(BaseModel):
    number: int
    status: TracOSWorkOrderStatusEnum = Field(default=TracOSWorkOrderStatusEnum.PENDING)
    title: str
    description: str
    createdAt: datetime
    updatedAt: datetime
    deleted: bool = Field(default=False)
    isSynced: bool = Field(default=False)
    syncedAt: Optional[datetime] = None
    deletedAt: Optional[datetime] = None
