from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CustomerWorkorderModel(BaseModel):
    orderNo: int
    isActive: bool = True
    isCanceled: bool
    isDeleted: bool
    isDone: bool
    isOnHold: bool
    isPending: bool
    isSynced: bool = False
    summary: str
    creationDate: datetime
    lastUpdateDate: datetime
    deletedDate: Optional[datetime] = None
