import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

@dataclass
class TaskRuntime:
    id: str
    task: str
    input_url: str | None = None
    status: str = "queued"
    progress: int = 0
    current: str = "manager"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    result: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    approval_event: asyncio.Event = field(default_factory=asyncio.Event)
    approved: bool = False

class RuntimeManager:
    def __init__(self):
        self.tasks: dict[str, TaskRuntime] = {}
        self._lock = asyncio.Lock()

    async def create(self, task: str, input_url: str | None = None) -> TaskRuntime:
        async with self._lock:
            item = TaskRuntime(str(uuid.uuid4()), task, input_url)
            self.tasks[item.id] = item
            return item

    def get(self, task_id: str):
        return self.tasks.get(task_id)

    def snapshot(self, item: TaskRuntime):
        return {"id":item.id,"task":item.task,"input_url":item.input_url,"status":item.status,
                "progress":item.progress,"current":item.current,"created_at":item.created_at,
                "updated_at":item.updated_at,"result":item.result,"logs":item.logs,
                "approval_required":item.status=="waiting_approval"}

    async def event(self, item: TaskRuntime, message: str, status=None, progress=None, current=None):
        if status: item.status=status
        if progress is not None: item.progress=progress
        if current: item.current=current
        item.updated_at=time.time()
        item.logs.append({"time":item.updated_at,"message":message,"status":item.status,
                          "progress":item.progress,"current":item.current})

    async def cancel(self, task_id: str):
        item=self.get(task_id)
        if not item: return False
        item.cancel_event.set()
        await self.event(item,"Cancellation requested","cancelling",item.progress,item.current)
        return True

    async def approve(self, task_id: str, approved: bool):
        item=self.get(task_id)
        if not item: return False
        item.approved=approved
        item.approval_event.set()
        await self.event(item, "Human approval granted" if approved else "Human approval rejected")
        return True

runtime_manager = RuntimeManager()
