import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import datetime

from src.main import app
from src.schemas import TaskResponse, TaskCreate, TaskUpdate
from src.crud import TaskCRUD

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def database_engine():
    """Фикстура для тестовой базы данных"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(database_engine):
    """Фикстура для асинхронной сессии"""
    async with database_engine.begin() as conn:
        from src.models import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        database_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from src.main import app
from src.crud import TaskCRUD


@pytest.fixture(scope="session")
def test_client():
    """Test client fixture"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_task_crud():
    """Mock TaskCRUD fixture"""
    return AsyncMock(spec=TaskCRUD)


@pytest.fixture(autouse=True)
def override_dependencies(mock_task_crud):
    """Override dependencies for testing"""
    from src.main import app
    from src.dependencies import get_task_crud

    async def override_get_task_crud():
        return mock_task_crud

    app.dependency_overrides[get_task_crud] = override_get_task_crud
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_task_object(sample_task_response):
    """Create a mock Task object with proper attributes"""
    from unittest.mock import MagicMock

    mock_task = MagicMock()
    mock_task.uuid = sample_task_response["uuid"]
    mock_task.title = sample_task_response["title"]
    mock_task.description = sample_task_response["description"]
    mock_task.status = sample_task_response["status"]
    return mock_task


@pytest.fixture
def sample_task_response():
    """Sample task response data"""
    task_uuid = uuid.uuid4()
    return {
        "uuid": task_uuid,
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending"
    }

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_task_crud():
    return AsyncMock(spec=TaskCRUD)


@pytest.fixture
def override_dependency(mock_task_crud):
    async def override_get_task_crud():
        return mock_task_crud

    app.dependency_overrides[app.dependency_overrides.get('get_task_crud')] = override_get_task_crud
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data():
    return {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending"
    }


@pytest.fixture
def sample_task_response():
    task_uuid = uuid.uuid4()
    return {
        "uuid": task_uuid,
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending"
    }

