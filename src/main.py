from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import uuid

from src.dependencies import get_task_crud
from src.schemas import TaskResponse, TaskCreate, TaskUpdate
from src.crud import TaskCRUD


app = FastAPI(
    title="Task Manager API",
    description="A simple task management API with CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    return {"message": "Task Manager API"}

@app.post("/tasks/create", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Create a new task"""
    return await task_crud.create_task(task)

@app.get("/tasks/", response_model=List[TaskResponse])
async def read_tasks(
    task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Get list of tasks"""
    tasks = await task_crud.get_tasks()
    return tasks

@app.get("/tasks/{task_uuid}", response_model=TaskResponse)
async def read_task(
    task_uuid: uuid.UUID,
    task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Get a specific task by UUID"""
    task = await task_crud.get_task(task_uuid)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.put("/tasks/{task_uuid}", response_model=TaskResponse)
async def update_task(
    task_uuid: uuid.UUID,
    task_update: TaskUpdate,
    task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Update a task"""
    task = await task_crud.update_task(task_uuid, task_update)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.delete("/tasks/{task_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_uuid: uuid.UUID,
    task_crud: TaskCRUD = Depends(get_task_crud)
):
    """Delete a task"""
    success = await task_crud.delete_task(task_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None
