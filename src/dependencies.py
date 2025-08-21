from fastapi import Depends

from . import crud, database

async def get_task_crud(db: database.AsyncSession = Depends(database.get_db)):
    return crud.TaskCRUD(db)