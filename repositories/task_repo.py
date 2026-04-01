from uuid import UUID
from models.tasks import TaskBase, AnyTask


class TaskRepository:
    """In-memory async repository. Swap the dict for a DB session in production."""

    def __init__(self) -> None:
        self._store: dict[UUID, TaskBase] = {}

    async def save(self, task: TaskBase) -> TaskBase:
        self._store[task.id] = task
        return task

    async def get(self, task_id: UUID) -> TaskBase | None:
        return self._store.get(task_id)

    async def list_all(self) -> list[TaskBase]:
        return list(self._store.values())

    async def update(self, task: TaskBase) -> TaskBase:
        self._store[task.id] = task
        return task


# Singleton — one instance for the whole app lifetime
task_repository = TaskRepository()