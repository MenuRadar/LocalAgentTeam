from pathlib import Path
import json,shutil
class WorkspaceManager:
    def __init__(self,root="workspaces"): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def create(self,task_id):
        p=self.root/task_id
        for n in ("input","output","artifacts","logs"): (p/n).mkdir(parents=True,exist_ok=True)
        (p/"manifest.json").write_text(json.dumps({"task_id":task_id},indent=2),encoding="utf-8"); return p
    def cleanup(self,task_id):
        p=self.root/task_id
        if p.exists(): shutil.rmtree(p)
