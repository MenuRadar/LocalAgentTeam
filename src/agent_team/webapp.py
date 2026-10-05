from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import asyncio
from .manager import Manager
from .adapters import Crawl4AIAdapter, OpenAIAgentsAdapter, BrowserUseAdapter
from .pipeline import MenuRadarPipeline
from .runtime import runtime_manager
from .publisher import GitHubPublisher

app = FastAPI(title="LocalAgentTeam", version="0.6.0")
manager = Manager()

class TaskRequest(BaseModel):
    task: str
    input_url: str | None = None

class DecisionRequest(BaseModel):
    approved: bool

class PublishRequest(BaseModel):
    path: str
    content: str
    message: str = "publish: LocalAgentTeam approved artifact"

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LocalAgentTeam — Command Center</title>
<style>
*{box-sizing:border-box}:root{--bg:#070a10;--p:#0d141f;--p2:#101a28;--line:#223046;--text:#eaf1fb;--muted:#8190a6;--ok:#63e6be;--blue:#70bfff;--warn:#ffd166;--bad:#ff6b7a}body{margin:0;background:radial-gradient(circle at 15% 0,#102a38,#070a10 40%);color:var(--text);font-family:Inter,system-ui,sans-serif}.shell{max-width:1500px;margin:auto;padding:22px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}.brand{font-weight:900;font-size:25px}.brand span{color:var(--ok)}.live{color:var(--ok);border:1px solid #285545;background:#0b1714;border-radius:999px;padding:7px 11px;font-size:11px}.grid{display:grid;grid-template-columns:1fr 390px;gap:16px}.card{background:linear-gradient(145deg,#0e1621,#0a1018);border:1px solid var(--line);border-radius:16px;padding:17px;margin-bottom:16px;box-shadow:0 15px 45px #0007}h2{font-size:14px;margin:0 0 12px}p{font-size:12px;color:var(--muted)}textarea,input{width:100%;background:#070c14;border:1px solid #27374d;color:var(--text);border-radius:10px;padding:12px;outline:none}textarea{min-height:105px;resize:vertical}input{margin-top:8px}button{border:0;border-radius:10px;padding:11px 15px;font-weight:800;cursor:pointer;margin-top:9px;background:var(--ok);color:#06110d}button.alt{background:#172332;color:#c8d4e4;border:1px solid #293a50}button.danger{background:#321720;color:#ff9eaa;border:1px solid #5c2934}button:disabled{opacity:.45}.actions{display:flex;gap:7px;align-items:center}.bar{height:6px;background:#121d2a;border-radius:9px;overflow:hidden;margin-top:10px}.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--ok),var(--blue));transition:.35s}.log{height:210px;overflow:auto;background:#05080d;border:1px solid #1b2736;border-radius:10px;padding:10px;font:11px ui-monospace,monospace}.line{padding:5px 0;border-bottom:1px solid #101824;color:#91a1b7}.line b{color:var(--ok)}.result{min-height:100px;max-height:300px;overflow:auto;white-space:pre-wrap;background:#05080d;padding:11px;border-radius:10px;font:11px ui-monospace,monospace;color:#b7c5d8}.flow{position:relative}.flow:before{content:"";position:absolute;left:20px;top:21px;bottom:21px;width:2px;background:#243246}.node{position:relative;display:grid;grid-template-columns:42px 1fr 60px;align-items:center;gap:7px;padding:8px 0}.ico{width:31px;height:31px;border-radius:50%;display:grid;place-items:center;background:#101a27;border:1px solid #2a3b52;z-index:1}.node.active .ico{border-color:var(--ok);box-shadow:0 0 0 6px #63e6be0d,0 0 25px #63e6be55;animation:pulse 1s infinite}.node.done .ico{border-color:var(--blue);color:var(--blue)}.node.wait .ico{border-color:var(--warn);color:var(--warn)}.node b{font-size:12px}.node small{display:block;color:var(--muted);font-size:10px}.state{text-align:right;font-size:9px;color:var(--muted);text-transform:uppercase}@keyframes pulse{50%{transform:scale(1.1)}}.history{display:flex;flex-direction:column;gap:7px}.hist{padding:9px;border:1px solid #202e41;border-radius:9px;background:#0a111a;font-size:11px;cursor:pointer}.hist span{float:right;color:var(--muted)}.approval{display:none;border:1px solid #68551f;background:#18140a;padding:12px;border-radius:10px}.approval.show{display:block}.approval b{color:var(--warn)}.caps{display:flex;flex-wrap:wrap;gap:6px}.cap{font-size:10px;padding:6px 8px;border-radius:99px;border:1px solid #26364b;color:#8190a5}.cap.ok{border-color:#286b57;color:#8ef0c7}@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head><body><div class="shell">
<div class="top"><div class="brand">Local<span>Agent</span>Team</div><div class="live">● COMMAND CENTER</div></div>
<div class="grid"><main>
<div class="card"><h2>Task Command</h2><p>Existing providers only. Start a job, watch real backend state, then approve before publishing.</p>
<textarea id="task" placeholder="Scan a restaurant menu and prepare it for MenuRadar..."></textarea><input id="url" placeholder="Source URL (optional)">
<div class="actions"><button id="start" onclick="start()">▶ Start</button><button class="alt" onclick="clearAll()">Clear</button><button class="danger" id="stop" onclick="stopTask()" disabled>■ Stop</button><span id="status"></span></div><div class="bar"><i id="bar"></i></div></div>
<div class="card"><h2>Live Activity</h2><div class="log" id="log"><div class="line"><b>READY</b> — waiting for a task</div></div></div>
<div class="card"><h2>Approval Gate</h2><div id="approval" class="approval"><b>Human approval required</b><p>Review the output above. Publishing is blocked until you approve.</p><button onclick="decision(true)">✓ Approve</button><button class="danger" onclick="decision(false)">✕ Reject</button></div><div id="noapproval">No task is waiting for approval.</div></div>
<div class="card"><h2>Output / Publish</h2><div class="result" id="result">No output.</div><input id="pubpath" placeholder="GitHub path, e.g. posts/kfc-menu.html"><button id="publish" onclick="publish()" disabled>↥ Publish Approved Output</button></div>
</main><aside>
<div class="card"><h2>Live Pipeline</h2><div class="flow">
<div class="node" data-k="manager"><div class="ico">◆</div><div><b>Manager</b><small>routing</small></div><div class="state">idle</div></div><div class="node" data-k="browser"><div class="ico">◉</div><div><b>Browser Use</b><small>browser interaction</small></div><div class="state">idle</div></div><div class="node" data-k="crawler"><div class="ico">⌁</div><div><b>Crawl4AI</b><small>web extraction</small></div><div class="state">idle</div></div><div class="node" data-k="agent"><div class="ico">✦</div><div><b>Existing AI Agent</b><small>reasoning</small></div><div class="state">idle</div></div><div class="node" data-k="qa"><div class="ico">✓</div><div><b>QA / Approval</b><small>quality gate</small></div><div class="state">idle</div></div><div class="node" data-k="github"><div class="ico">↥</div><div><b>GitHub Publisher</b><small>publish after approval</small></div><div class="state">idle</div></div></div></div>
<div class="card"><h2>Task History</h2><div id="history" class="history">No tasks yet.</div></div>
<div class="card"><h2>Installed Providers</h2><div id="caps" class="caps">Loading…</div></div>
</aside></div></div>
<script>
let taskId=null,ws=null;
const $=id=>document.getElementById(id);
function log(m,t="INFO"){let d=document.createElement("div");d.className="line";d.innerHTML="<b>"+t+"</b> — "+m;$("log").appendChild(d);$("log").scrollTop=$("log").scrollHeight}
function node(k,s){let n=document.querySelector('[data-k="'+k+'"]');if(!n)return;n.classList.remove("active","done","wait");n.classList.add(s);n.querySelector(".state").textContent=s}
function reset(){document.querySelectorAll(".node").forEach(n=>{n.className="node";n.querySelector(".state").textContent="idle"})}
function render(x){taskId=x.id;$("bar").style.width=x.progress+"%";$("status").textContent=x.status+" · "+x.progress+"%";$("result").textContent=JSON.stringify(x.result||{},null,2);if(x.current)node(x.current,x.status==="waiting_approval"?"wait":x.status==="completed"?"done":"active");if(x.logs){$("log").innerHTML="";x.logs.forEach(v=>log(v.message,v.status.toUpperCase()))}if(x.status==="waiting_approval"){$("approval").className="approval show";$("noapproval").style.display="none"}else{$("approval").className="approval";$("noapproval").style.display="block"}if(["completed","failed","cancelled"].includes(x.status)){$("start").disabled=false;$("stop").disabled=true}}
function connect(id){if(ws)ws.close();ws=new WebSocket((location.protocol==="https:"?"wss://":"ws://")+location.host+"/ws/tasks/"+id);ws.onmessage=e=>render(JSON.parse(e.data));ws.onclose=()=>{}}
async function start(){let task=$("task").value.trim(),input_url=$("url").value.trim()||null;if(!task)return log("Enter a task","WAIT");reset();$("start").disabled=true;$("stop").disabled=false;$("log").innerHTML="";let r=await fetch("/api/tasks",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});let x=await r.json();render(x);connect(x.id);loadHistory()}
async function stopTask(){if(!taskId)return;await fetch("/api/tasks/"+taskId+"/cancel",{method:"POST"});log("Stop requested","CANCEL")}
async function decision(ok){if(!taskId)return;await fetch("/api/tasks/"+taskId+"/approval",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({approved:ok}));if(ok){$("publish").disabled=false}}
async function publish(){if(!taskId)return;let path=$("pubpath").value.trim(),content=$("result").textContent;if(!path)return log("Enter a GitHub path first","WAIT");let r=await fetch("/api/tasks/"+taskId+"/publish",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({path,content})});let d=await r.json();log(d.error||("Published: "+path),d.error?"ERROR":"PUBLISHED");$("result").textContent=JSON.stringify(d,null,2)}
async function loadHistory(){let r=await fetch("/api/tasks");let d=await r.json();$("history").innerHTML=d.length?d.reverse().map(x=>'<div class="hist" onclick="connect(\''+x.id+'\')">'+x.task.slice(0,48)+(x.task.length>48?'…':'')+'<span>'+x.status+'</span></div>').join(""):"No tasks yet."}
async function clearAll(){$("task").value="";$("url").value="";$("result").textContent="No output.";reset();$("bar").style.width="0%";$("log").innerHTML='<div class="line"><b>READY</b> — waiting for a task</div>'}
async function caps(){let r=await fetch("/api/capabilities"),d=await r.json();$("caps").innerHTML=d.map(x=>'<span class="cap '+(x.available?"ok":"")+'">'+x.provider+" · "+(x.available?"READY":"MISSING")+"</span>").join("")}
caps();loadHistory();
</script></body></html>""")

@app.get("/api/capabilities")
async def capabilities(): return manager.capabilities()

@app.get("/api/tasks")
async def tasks():
    return [runtime_manager.snapshot(x) for x in runtime_manager.tasks.values()]

@app.post("/api/tasks")
async def create_task(req: TaskRequest):
    item=await runtime_manager.create(req.task,req.input_url)
    asyncio.create_task(execute_task(item))
    return runtime_manager.snapshot(item)

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    item=runtime_manager.get(task_id)
    return runtime_manager.snapshot(item) if item else {"error":"task not found"}

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str): return {"ok":await runtime_manager.cancel(task_id)}

@app.post("/api/tasks/{task_id}/approval")
async def approval(task_id: str, req: DecisionRequest): return {"ok":await runtime_manager.approve(task_id,req.approved)}

@app.post("/api/tasks/{task_id}/publish")
async def publish(task_id: str, req: PublishRequest):
    item=runtime_manager.get(task_id)
    if not item: return {"error":"task not found"}
    if not item.approved: return {"error":"human approval is required before publishing"}
    try:
        result=GitHubPublisher().upsert_text(req.path, req.content, req.message)
        await runtime_manager.event(item,"GitHub publish completed","completed",100,"github")
        item.result={"publish":result}
        return result
    except Exception as exc:
        return {"error":str(exc)}

@app.websocket("/ws/tasks/{task_id}")
async def task_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    item=runtime_manager.get(task_id)
    if not item: await websocket.send_json({"error":"task not found"}); await websocket.close(); return
    last=-1
    try:
        while True:
            if len(item.logs)!=last or item.status in ("completed","failed","cancelled"):
                await websocket.send_json(runtime_manager.snapshot(item)); last=len(item.logs)
            if item.status in ("completed","failed","cancelled"): await asyncio.sleep(.3); break
            await asyncio.sleep(.25)
    except WebSocketDisconnect: pass

async def execute_task(item):
    try:
        await runtime_manager.event(item,"Manager accepted task","running",5,"manager")
        route=await manager.route(item.task,item.input_url)
        await runtime_manager.event(item,"Route selected: "+route["route"],"running",15,"manager")
        if item.cancel_event.is_set(): raise asyncio.CancelledError()
        if not route.get("available"):
            raise RuntimeError(route["reason"])
        if route["route"]=="crawl4ai":
            if not item.input_url: raise RuntimeError("input_url is required")
            await runtime_manager.event(item,"Crawl4AI started","running",30,"crawler")
            result=await Crawl4AIAdapter().run(item.input_url)
        elif route["route"]=="browser-use":
            await runtime_manager.event(item,"Browser Use started","running",30,"browser")
            result=await BrowserUseAdapter().run(item.task)
        elif route["route"]=="openai-agents":
            await runtime_manager.event(item,"Existing OpenAI Agents SDK started","running",30,"agent")
            result=await OpenAIAgentsAdapter().run(item.task)
        else: raise RuntimeError("No executable provider")
        if item.cancel_event.is_set(): raise asyncio.CancelledError()
        item.result=result
        await runtime_manager.event(item,"Provider completed; QA gate reached","waiting_approval",85,"qa")
        await asyncio.wait_for(item.approval_event.wait(),timeout=1800)
        if not item.approved: raise RuntimeError("Human rejected the task")
        await runtime_manager.event(item,"Approved. Publishing is enabled for a configured publisher.","running",92,"github")
        await runtime_manager.event(item,"Approval accepted; publisher handoff is ready","completed",100,"github")
    except asyncio.CancelledError:
        await runtime_manager.event(item,"Task cancelled","cancelled",item.progress,item.current)
    except Exception as exc:
        item.result={"error":str(exc)}
        await runtime_manager.event(item,"Task failed: "+str(exc),"failed",item.progress,item.current)

@app.post("/api/route")
async def route(req: TaskRequest): return await manager.route(req.task,req.input_url)

@app.get("/api/menuradar/plan")
async def menuradar_plan(url: str): return [x.model_dump() for x in MenuRadarPipeline().plan(url)]
