from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .manager import Manager
from .adapters import Crawl4AIAdapter, OpenAIAgentsAdapter
from .pipeline import MenuRadarPipeline

app = FastAPI(title="LocalAgentTeam", version="0.4.0")
manager = Manager()

class TaskRequest(BaseModel):
    task: str
    input_url: str | None = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LocalAgentTeam — Control Center</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#080b12;color:#e9eef8;font-family:Inter,system-ui,Segoe UI,sans-serif}
.shell{max-width:1400px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
.logo{font-size:24px;font-weight:800}.logo span{color:#63e6be}.status{padding:8px 12px;border:1px solid #263246;border-radius:999px;background:#101724;color:#8ef0c7;font-size:13px}
.grid{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}.card{background:linear-gradient(145deg,#101722,#0c111b);border:1px solid #202b3c;border-radius:18px;padding:20px;box-shadow:0 10px 35px #0005}
h2{margin:0 0 14px;font-size:17px}p{color:#8996aa}.task{min-height:130px;resize:vertical}textarea,input{width:100%;background:#080d16;color:#e9eef8;border:1px solid #273448;border-radius:12px;padding:13px;outline:none}textarea:focus,input:focus{border-color:#63e6be}
button{border:0;border-radius:11px;padding:12px 18px;background:#63e6be;color:#06100d;font-weight:800;cursor:pointer;margin-top:10px}button:disabled{opacity:.5}
#run{display:flex;gap:10px;align-items:center}.spinner{width:16px;height:16px;border:2px solid #183c32;border-top-color:#63e6be;border-radius:50%;animation:spin .8s linear infinite;display:none}@keyframes spin{to{transform:rotate(360deg)}}
.pipeline{display:flex;flex-direction:column;gap:9px}.node{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #243044;border-radius:12px;background:#0b111a;transition:.25s}.dot{width:11px;height:11px;border-radius:50%;background:#3a4658;box-shadow:0 0 0 0 #63e6be}.node.active{border-color:#63e6be;transform:translateX(5px);box-shadow:0 0 22px #63e6be22}.node.active .dot{background:#63e6be;animation:pulse 1s infinite}@keyframes pulse{50%{box-shadow:0 0 0 8px #63e6be12}}.node.done .dot{background:#65d6ff}.node small{display:block;color:#738198;margin-top:2px}
.log{height:220px;overflow:auto;background:#060a10;border:1px solid #1d2735;border-radius:12px;padding:12px;font:12px ui-monospace,monospace}.line{margin:0 0 8px;color:#91a0b5}.line b{color:#63e6be}.caps{display:flex;flex-wrap:wrap;gap:8px}.badge{padding:7px 10px;border-radius:999px;background:#121a26;border:1px solid #263348;font-size:12px}.available{border-color:#2c9d7c;color:#8ef0c7}.missing{color:#78859a}
pre{white-space:pre-wrap;color:#aebbd0}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="shell">
<div class="top"><div class="logo">Local<span>Agent</span>Team</div><div class="status">● LOCAL CONTROL CENTER</div></div>
<div class="grid">
<div>
<div class="card"><h2>Run a Task</h2><p>One GUI over the existing agents and tools. No duplicate agents.</p>
<textarea id="task" class="task" placeholder="Example: Scan this restaurant menu, extract all items, validate completeness and prepare it for MenuRadar."></textarea>
<input id="url" placeholder="Source URL (optional)">
<div id="run"><button id="btn" onclick="startTask()">▶ Start Task</button><div class="spinner" id="spin"></div><span id="state"></span></div></div>
<div class="card"><h2>Live Activity</h2><div class="log" id="log"><div class="line"><b>READY</b> — waiting for a task…</div></div></div>
<div class="card"><h2>Result</h2><pre id="out">No task has been run yet.</pre></div>
</div>
<div>
<div class="card"><h2>Agent Pipeline</h2><div class="pipeline" id="pipeline">
<div class="node" data-key="manager"><div class="dot"></div><div>Manager / Router<small>selects the existing capability</small></div></div>
<div class="node" data-key="browser"><div class="dot"></div><div>Browser Use<small>browser interaction when required</small></div></div>
<div class="node" data-key="crawler"><div class="dot"></div><div>Crawl4AI<small>web extraction</small></div></div>
<div class="node" data-key="agent"><div class="dot"></div><div>OpenAI Agents<small>reasoning / orchestration</small></div></div>
<div class="node" data-key="qa"><div class="dot"></div><div>QA / Approval<small>quality and publishing gate</small></div></div>
<div class="node" data-key="github"><div class="dot"></div><div>GitHub Publisher<small>publish only after approval</small></div></div>
</div></div>
<div class="card"><h2>Installed Capabilities</h2><div class="caps" id="caps">Loading…</div></div>
</div></div></div>
<script>
const $=id=>document.getElementById(id);
function log(msg,type="INFO"){const d=document.createElement("div");d.className="line";d.innerHTML="<b>"+type+"</b> — "+msg;$("log").appendChild(d);$("log").scrollTop=$("log").scrollHeight}
function active(key){document.querySelectorAll(".node").forEach(n=>n.classList.remove("active"));const n=document.querySelector('[data-key="'+key+'"]');if(n)n.classList.add("active")}
function done(key){const n=document.querySelector('[data-key="'+key+'"]');if(n){n.classList.remove("active");n.classList.add("done")}}
async function startTask(){
 const task=$("task").value.trim(), input_url=$("url").value.trim()||null;if(!task){log("Enter a task first","WAIT");return}
 $("btn").disabled=true;$("spin").style.display="block";$("state").textContent="Working…";document.querySelectorAll(".node").forEach(n=>n.classList.remove("active","done"));
 active("manager");log("Manager received task");await new Promise(r=>setTimeout(r,500));
 try{
  const rr=await fetch("/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const route=await rr.json();
  done("manager");log("Selected route: "+route.route);active(route.route==="crawl4ai"?"crawler":route.route==="browser-use"?"browser":"agent");
  await new Promise(r=>setTimeout(r,500));
  if(route.route==="crawl4ai"&&input_url){
    log("Crawl4AI started");const r=await fetch("/api/crawl",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const d=await r.json();done("crawler");active("qa");log("Extraction finished; QA gate reached","DONE");$("out").textContent=JSON.stringify(d,null,2);
  }else if(route.route==="openai-agents"){
    log("Existing OpenAI Agents SDK started");const r=await fetch("/api/agent",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const d=await r.json();done("agent");active("qa");log("Agent result received; QA gate reached","DONE");$("out").textContent=JSON.stringify(d,null,2);
  }else{log("No executable provider is currently installed for this route","WAIT");$("out").textContent=JSON.stringify(route,null,2)}
 }catch(e){log(e.message||String(e),"ERROR");$("out").textContent=String(e)}
 $("btn").disabled=false;$("spin").style.display="none";$("state").textContent="";active("qa");
}
async function load(){const r=await fetch("/api/capabilities");const d=await r.json();$("caps").innerHTML=d.map(x=>'<span class="badge '+(x.available?"available":"missing")+'">'+x.provider+" · "+(x.available?"READY":"NOT INSTALLED")+"</span>").join("")}load();
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
