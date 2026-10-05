from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING="pending"; RUNNING="running"; WAITING_APPROVAL="waiting_approval"
    COMPLETED="completed"; FAILED="failed"; CANCELLED="cancelled"

class Task(BaseModel):
    id: str
    name: str
    description: str
    task_type: str
    input: dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str | None = None
    output: dict[str, Any] = Field(default_factory=dict)
    parent_id: str | None = None
    retries: int = 0

class Handoff(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    next_action: str | None = None
    errors: list[str] = Field(default_factory=list)

class AgentCapability(BaseModel):
    name: str
    provider: str
    capabilities: list[str]
    available: bool
    reason: str | None = None
