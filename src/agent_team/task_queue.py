import sqlite3
from pathlib import Path
from .models import Task,TaskStatus
class TaskQueue:
    def __init__(self,db_path="data/agent_state.db"):
        Path(db_path).parent.mkdir(parents=True,exist_ok=True); self.db_path=db_path
        with sqlite3.connect(db_path) as db: db.execute("CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,payload TEXT NOT NULL,status TEXT NOT NULL)")
    def enqueue(self,task):
        with sqlite3.connect(self.db_path) as db: db.execute("INSERT OR REPLACE INTO tasks VALUES(?,?,?)",(task.id,task.model_dump_json(),task.status.value))
    def get(self,task_id):
        with sqlite3.connect(self.db_path) as db: row=db.execute("SELECT payload FROM tasks WHERE id=?",(task_id,)).fetchone()
        return Task.model_validate_json(row[0]) if row else None
    def set_status(self,task_id,status):
        task=self.get(task_id)
        if task: task.status=status; self.enqueue(task)
