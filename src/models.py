from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from src.database import Base


class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    __tablename__ = "Tasks"

    uuid: Mapped[UUID] = mapped_column(unique=True, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(String, default=TaskStatus.CREATED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"Task(uuid={self.uuid}, title={self.title}, status={self.status})"