from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .manager import Manager
from .adapters import Crawl4AIAdapter, OpenAIAgentsAdapter
from .pipeline import MenuRadarPipeline

app = FastAPI(title="LocalAgentTeam", version="0.3.0")
manager = Manager()

class TaskRequest(BaseModel):
    task: str
    input_url: str | None = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!doctype html><html><head><meta charset="utf-8"><title>LocalAgentTeam</title>
<style>body{font-family:system-ui;max-width:1100px;margin:40px auto;padding:0 20px;background:#f6f7fb}.card{background:#fff;border:1px solid #ddd;border-radius:14px;padding:20px;margin:16px 0}textarea,input{width:100%;box-sizing:border-box;padding:12px;border:1px solid #ccc;border-radius:9px}button{padding:11px 18px;border:0;border-radius:9px;cursor:pointer;margin-top:10px}pre{white-space:pre-wrap;background:#111;color:#eee;padding:14px;border-radius:9px}.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#eee;margin:3px}</style>
</head><body><h1>LocalAgentTeam</h1><p>One interface over existing agents/tools. No duplicate agents are created.</p>
<div class="card"><h2>Task Router</h2><textarea id="task" rows="4" placeholder="Example: scan this restaurant menu source and prepare structured data"></textarea>
<input id="url" placeholder="Optional source URL"><button onclick="routeTask()">Route task</button><pre id="out"></pre></div>
<div class="card"><h2>Installed capabilities</h2><div id="caps">Loading…</div></div>
<script>
async function routeTask(){const r=await fetch('/api/route',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task:document.getElementById('task').value,input_url:document.getElementById('url').value||null})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}
async function load(){const r=await fetch('/api/capabilities');const d=await r.json();document.getElementById('caps').innerHTML=d.map(x=>'<span class="badge">'+x.provider+': '+(x.available?'AVAILABLE':'NOT INSTALLED')+'</span>').join('')}load();
</script></body></html>""")

@app.get("/api/capabilities")
async def capabilities():
    return manager.capabilities()

@app.post("/api/route")
async def route(req: TaskRequest):
    return await manager.route(req.task, req.input_url)

@app.post("/api/crawl")
async def crawl(req: TaskRequest):
    if not req.input_url: return {"error":"input_url is required"}
    return await Crawl4AIAdapter().run(req.input_url)

@app.post("/api/agent")
async def agent(req: TaskRequest):
    return await OpenAIAgentsAdapter().run(req.task)

@app.get("/api/menuradar/plan")
async def menuradar_plan(url: str):
    return [x.model_dump() for x in MenuRadarPipeline().plan(url)]
