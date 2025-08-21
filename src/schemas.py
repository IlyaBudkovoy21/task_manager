import uuid
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .models import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.CREATED


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskInDB(TaskBase):
    uuid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskResponse(TaskInDB):
    pass