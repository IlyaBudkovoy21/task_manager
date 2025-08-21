from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID
from typing import Optional

from src.schemas import TaskCreate, TaskUpdate
from src.models import Task


class TaskCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task_data: TaskCreate) -> Task:
        new_task = Task(title=task_data.title,
                        description=task_data.description,
                        status=task_data.status)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task

    async def get_task(self, task_uuid: UUID) -> Optional[Task]:
        result = await self.session.execute(
            select(Task).where(Task.uuid == task_uuid)
        )
        return result.scalar_one_or_none()

    async def get_tasks(self) -> list[Task]:
        query = select(Task)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def update_task(
            self,
            task_uuid: UUID,
            task_update: TaskUpdate
    ) -> Optional[Task]:
        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_task(task_uuid)

        stmt = (
            update(Task)
            .where(Task.uuid == task_uuid)
            .values(**update_data)
            .returning(Task)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete_task(self, task_uuid: UUID) -> bool:
        stmt = delete(Task).where(Task.uuid == task_uuid)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.returns_rows
