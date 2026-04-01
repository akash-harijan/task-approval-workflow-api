from uuid import UUID
from fastapi import APIRouter, Depends

from models.tasks import AnyTask, ApproveRequest, RejectRequest
from controllers.task_controller import TaskController
from repositories.task_repo import task_repository

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_controller() -> TaskController:
    return TaskController(repo=task_repository)


@router.post("/", response_model=AnyTask, status_code=201)
async def create_task(
    task: AnyTask,
    controller: TaskController = Depends(get_controller),
):
    return await controller.create_task(task)


@router.get("/{task_id}", response_model=AnyTask)
async def get_task(
    task_id: UUID,
    controller: TaskController = Depends(get_controller),
):
    return await controller.get_task(task_id)


@router.patch("/{task_id}/approve", response_model=AnyTask)
async def approve_task(
    task_id: UUID,
    body: ApproveRequest,
    controller: TaskController = Depends(get_controller),
):
    return await controller.approve_task(task_id, body.approved_by)


@router.patch("/{task_id}/reject", response_model=AnyTask)
async def reject_task(
    task_id: UUID,
    body: RejectRequest,
    controller: TaskController = Depends(get_controller),
):
    return await controller.reject_task(task_id, body.rejected_by, body.reason)
