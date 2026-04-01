from __future__ import annotations
from enum import Enum
from typing import Annotated, Union
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TaskType(str, Enum):
    DATA_ACCESS = "data_access"
    RESOURCE_PROVISION = "resource_provision"
    CONFIG_CHANGE = "config_change"


# Shared fields common to all Task models


class TaskBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=3, max_length=200)
    requested_by: str = Field(..., min_length=1)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None
    rejection_reason: str | None = None


# Concrete task classes are defined below, each one containing fields and validation logic specific to the task type.

class DataAccessTask(TaskBase):
    task_type: TaskType = Field(TaskType.DATA_ACCESS, alias="task_type")
    type: str = Field("data_access", pattern="^data_access$")  # discriminator field
    dataset_name: str = Field(..., min_length=1)
    access_level: str = Field(..., pattern="^(read|write|admin)$")
    data_classification: str = Field(..., pattern="^(public|internal|confidential|restricted)$")

    @model_validator(mode="after")
    def admin_requires_restricted(self):
        if self.access_level == "admin" and self.data_classification != "restricted":
            raise ValueError("Admin access level requires data_classification='restricted'.")
        return self


class ResourceProvisionTask(TaskBase):
    type: str = Field("resource_provision", pattern="^resource_provision$")
    resource_type: str = Field(..., pattern="^(vm|storage|database|network)$")
    environment: str = Field(..., pattern="^(dev|staging|prod)$")
    estimated_cost_eur: float = Field(..., gt=0)

    @field_validator("estimated_cost_eur")
    @classmethod
    def prod_cost_limit(cls, v, info):
        return v  # cross-env rule enforced in controller


class ConfigChangeTask(TaskBase):
    type: str = Field("config_change", pattern="^config_change$")
    service_name: str = Field(..., min_length=1)
    change_description: str = Field(..., min_length=20, max_length=1000)
    requires_downtime: bool = False
    rollback_plan: str | None = None

    @model_validator(mode="after")
    def downtime_needs_rollback(self):
        if self.requires_downtime and not self.rollback_plan:
            raise ValueError("rollback_plan is required when requires_downtime is True")
        return self


# This is a discriminated union, letting Pydantic choose the correct model based on the "type" field.

AnyTask = Annotated[
    Union[DataAccessTask, ResourceProvisionTask, ConfigChangeTask],
    Field(discriminator="type")
]


# Request and response wrappers for task operations are defined below.

class TaskCreateRequest(BaseModel):
    task: AnyTask  # The correct task subtype will automatically be selected based on the "type" field


class ApproveRequest(BaseModel):
    approved_by: str = Field(..., min_length=1)


class RejectRequest(BaseModel):
    rejected_by: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=5)