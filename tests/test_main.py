import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.crud import TaskCRUD




class TestRootEndpoint:
    def test_root_endpoint(self, client):
        """Test that root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Task Manager API"}


class TestCreateTask:
    def test_create_task_validation_error(self, client, override_dependency):
        """Test task creation with invalid data"""
        invalid_data = {"title": ""}  # Missing required fields

        response = client.post("/tasks/create", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestReadTasks:
    def test_read_tasks_success(
            self, client, mock_task_crud, override_dependency, sample_task_response
    ):
        """Test successful retrieval of tasks"""
        mock_task_crud.get_tasks.return_value = [sample_task_response]

        response = client.get("/tasks/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [sample_task_response]
        mock_task_crud.get_tasks.assert_called_once()

    def test_read_tasks_empty(self, client, mock_task_crud, override_dependency):
        """Test retrieval of empty tasks list"""
        mock_task_crud.get_tasks.return_value = []

        response = client.get("/tasks/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        mock_task_crud.get_tasks.assert_called_once()


class TestReadTask:
    def test_read_task_not_found(
        self, client, mock_task_crud, override_dependency
    ):
        """Test retrieval of non-existent task"""
        task_uuid = uuid.uuid4()
        mock_task_crud.get_task.return_value = None

        response = client.get(f"/tasks/{task_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"
        mock_task_crud.get_task.assert_called_once_with(task_uuid)

    def test_read_task_invalid_uuid(self, client, override_dependency):
        """Test retrieval with invalid UUID format"""
        response = client.get("/tasks/invalid-uuid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateTask:
    def test_update_task_success(
            self, client, mock_task_crud, override_dependency, sample_task_response
    ):
        """Test successful task update"""
        task_uuid = sample_task_response["uuid"]
        update_data = {"title": "Updated Task", "status": "completed"}

        # Создаем mock-объект с нужными атрибутами
        mock_updated_task = MagicMock()
        mock_updated_task.uuid = task_uuid
        mock_updated_task.title = "Updated Task"
        mock_updated_task.description = "Test Description"
        mock_updated_task.status = "completed"

        mock_task_crud.update_task.return_value = mock_updated_task

        response = client.put(f"/tasks/{task_uuid}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Task"
        assert response.json()["status"] == "completed"
        mock_task_crud.update_task.assert_called_once()
        called_uuid, called_update = mock_task_crud.update_task.call_args[0]
        assert called_uuid == task_uuid
        assert isinstance(called_update, TaskUpdate)

    def test_update_task_not_found(
            self, client, mock_task_crud, override_dependency
    ):
        """Test update of non-existent task"""
        task_uuid = uuid.uuid4()
        update_data = {"title": "Updated Task"}
        mock_task_crud.update_task.return_value = None

        response = client.put(f"/tasks/{task_uuid}", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"
        mock_task_crud.update_task.assert_called_once()

    def test_update_task_partial_data(
            self, client, mock_task_crud, override_dependency
    ):
        """Test task update with partial data"""
        task_uuid = uuid.uuid4()
        update_data = {"status": "completed"}  # Only update status

        # Создаем mock-объект для частичного обновления
        mock_updated_task = MagicMock()
        mock_updated_task.uuid = task_uuid
        mock_updated_task.title = "Test Task"  # Оригинальное значение
        mock_updated_task.description = "Test Description"  # Оригинальное значение
        mock_updated_task.status = "completed"  # Обновленное значение

        mock_task_crud.update_task.return_value = mock_updated_task

        response = client.put(f"/tasks/{task_uuid}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "completed"
        assert response.json()["title"] == "Test Task"  # Должно остаться неизменным
        mock_task_crud.update_task.assert_called_once()



class TestDeleteTask:
    def test_delete_task_success(
            self, client, mock_task_crud, override_dependency
    ):
        """Test successful task deletion"""
        task_uuid = uuid.uuid4()
        mock_task_crud.delete_task.return_value = True

        response = client.delete(f"/tasks/{task_uuid}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        mock_task_crud.delete_task.assert_called_once_with(task_uuid)

    def test_delete_task_not_found(
            self, client, mock_task_crud, override_dependency
    ):
        """Test deletion of non-existent task"""
        task_uuid = uuid.uuid4()
        mock_task_crud.delete_task.return_value = False

        response = client.delete(f"/tasks/{task_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"
        mock_task_crud.delete_task.assert_called_once_with(task_uuid)