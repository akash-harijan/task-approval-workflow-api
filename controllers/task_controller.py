from uuid import UUID
from datetime import datetime, UTC
from fastapi import HTTPException

from models.tasks import TaskBase, TaskStatus, DataAccessTask, ResourceProvisionTask
from repositories.task_repo import TaskRepository


class TaskController:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    async def create_task(self, task: TaskBase) -> TaskBase:
        if isinstance(task, ResourceProvisionTask):
            if task.environment == "prod" and task.estimated_cost_eur > 5000:
                raise HTTPException(
                    status_code=422,
                    detail="Production resources over EUR 5000 require manual pre-approval.",
                )

        if isinstance(task, DataAccessTask):
            if task.access_level == "admin" and task.data_classification != "restricted":
                raise HTTPException(
                    status_code=422,
                    detail="Admin access level requires data_classification='restricted'.",
                )

        return await self._repo.save(task)

    async def get_task(self, task_id: UUID) -> TaskBase:
        task = await self._repo.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
        return task

    async def approve_task(self, task_id: UUID, approved_by: str) -> TaskBase:
        task = await self.get_task(task_id)
        self._assert_pending(task)

        task.status = TaskStatus.APPROVED
        task.resolved_at = datetime.now(UTC)
        return await self._repo.update(task)

    async def reject_task(self, task_id: UUID, rejected_by: str, reason: str) -> TaskBase:
        task = await self.get_task(task_id)
        self._assert_pending(task)

        task.status = TaskStatus.REJECTED
        task.resolved_at = datetime.now(UTC)
        task.rejection_reason = reason
        return await self._repo.update(task)

    @staticmethod
    def _assert_pending(task: TaskBase) -> None:
        if task.status != TaskStatus.PENDING:
            raise HTTPException(
                status_code=409,
                detail=f"Task is already {task.status.value}. Only PENDING tasks can be actioned.",
            )
