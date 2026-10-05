import psutil
class ResourceGuard:
    def __init__(self,cpu_limit=85,ram_limit=80): self.cpu_limit=cpu_limit; self.ram_limit=ram_limit
    def snapshot(self): return {"cpu_percent":psutil.cpu_percent(interval=.1),"ram_percent":psutil.virtual_memory().percent}
    def can_start(self):
        s=self.snapshot(); return s["cpu_percent"]<self.cpu_limit and s["ram_percent"]<self.ram_limit
