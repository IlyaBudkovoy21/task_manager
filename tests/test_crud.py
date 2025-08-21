import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import TaskCreate, TaskUpdate
from src.models import Task
from src.crud import TaskCRUD


@pytest.fixture
def async_session():
    """Фикстура для мока AsyncSession"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def task_crud(async_session):
    """Фикстура для TaskCRUD"""
    return TaskCRUD(async_session)


@pytest.fixture
def sample_task_data():
    """Фикстура с тестовыми данными для создания задачи"""
    return TaskCreate(
        title="Test Task",
        description="Test Description",
        status="new"
    )


@pytest.fixture
def sample_task():
    """Фикстура с готовой задачей"""
    return Task(
        uuid=uuid.uuid4(),
        title="Existing Task",
        description="Existing Description",
        status="in_progress",
        created_at="2023-01-01T00:00:00"
    )


@pytest.mark.asyncio
async def test_create_task(task_crud, async_session, sample_task_data):
    """Тест создания задачи"""
    # Arrange
    mock_task = MagicMock()
    async_session.add.return_value = None
    async_session.commit.return_value = None
    async_session.refresh.return_value = None

    # Mock возвращаемой задачи после refresh
    task_crud.session.refresh = AsyncMock()
    task_crud.session.refresh.side_effect = lambda task: setattr(task, 'uuid', uuid.uuid4())

    # Act
    result = await task_crud.create_task(sample_task_data)

    # Assert
    async_session.add.assert_called_once()
    async_session.commit.assert_awaited_once()
    async_session.refresh.assert_awaited_once()
    assert result.title == sample_task_data.title
    assert result.description == sample_task_data.description
    assert result.status == sample_task_data.status


@pytest.mark.asyncio
async def test_get_task_found(task_crud, async_session, sample_task):
    """Тест получения существующей задачи"""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.get_task(sample_task.uuid)

    # Assert
    async_session.execute.assert_awaited_once()
    assert result == sample_task
    assert result.uuid == sample_task.uuid
    assert result.title == sample_task.title


@pytest.mark.asyncio
async def test_get_task_not_found(task_crud, async_session):
    """Тест получения несуществующей задачи"""
    # Arrange
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    async_session.execute.return_value = mock_result
    non_existent_uuid = uuid.uuid4()

    # Act
    result = await task_crud.get_task(non_existent_uuid)

    # Assert
    async_session.execute.assert_awaited_once()
    assert result is None


@pytest.mark.asyncio
async def test_get_tasks(task_crud, async_session, sample_task):
    """Тест получения всех задач"""
    # Arrange
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_task]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.get_tasks()

    # Assert
    async_session.execute.assert_awaited_once()
    assert len(result) == 1
    assert result[0] == sample_task


@pytest.mark.asyncio
async def test_update_task_full_update(task_crud, async_session, sample_task):
    """Тест полного обновления задачи"""
    # Arrange
    update_data = TaskUpdate(
        title="Updated Title",
        description="Updated Description",
        status="completed"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.update_task(sample_task.uuid, update_data)

    # Assert
    async_session.execute.assert_awaited_once()
    async_session.commit.assert_awaited_once()
    assert result == sample_task


@pytest.mark.asyncio
async def test_update_task_partial_update(task_crud, async_session, sample_task):
    """Тест частичного обновления задачи"""
    # Arrange
    update_data = TaskUpdate(status="completed")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.update_task(sample_task.uuid, update_data)

    # Assert
    async_session.execute.assert_awaited_once()
    async_session.commit.assert_awaited_once()
    assert result == sample_task


@pytest.mark.asyncio
async def test_update_task_no_changes(task_crud, async_session, sample_task):
    """Тест обновления задачи без изменений"""
    # Arrange
    update_data = TaskUpdate()

    # Mock get_task для возврата sample_task
    task_crud.get_task = AsyncMock(return_value=sample_task)

    # Act
    result = await task_crud.update_task(sample_task.uuid, update_data)

    # Assert
    task_crud.get_task.assert_awaited_with(sample_task.uuid)
    async_session.execute.assert_not_called()
    async_session.commit.assert_not_called()
    assert result == sample_task


@pytest.mark.asyncio
async def test_update_task_not_found(task_crud, async_session):
    """Тест обновления несуществующей задачи"""
    # Arrange
    update_data = TaskUpdate(title="Updated")
    non_existent_uuid = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.update_task(non_existent_uuid, update_data)

    # Assert
    async_session.execute.assert_awaited_once()
    async_session.commit.assert_awaited_once()
    assert result is None


@pytest.mark.asyncio
async def test_delete_task_success(task_crud, async_session):
    """Тест успешного удаления задачи"""
    # Arrange
    task_uuid = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.returns_rows = True
    async_session.execute.return_value = mock_result

    # Act
    result = await task_crud.delete_task(task_uuid)

    # Assert
    async_session.execute.assert_awaited_once()
    async_session.commit.assert_awaited_once()
    assert result is True


@pytest.mark.asyncio
async def test_delete_task_failure(task_crud, async_session):
    """Тест неудачного удаления задачи"""
    task_uuid = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.returns_rows = False
    async_session.execute.return_value = mock_result

    result = await task_crud.delete_task(task_uuid)

    async_session.execute.assert_awaited_once()
    async_session.commit.assert_awaited_once()
    assert result is False

