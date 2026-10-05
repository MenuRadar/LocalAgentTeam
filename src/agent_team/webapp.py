from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .manager import Manager
from .adapters import Crawl4AIAdapter, OpenAIAgentsAdapter
from .pipeline import MenuRadarPipeline

app = FastAPI(title="LocalAgentTeam", version="0.5.0")
manager = Manager()

class TaskRequest(BaseModel):
    task: str
    input_url: str | None = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LocalAgentTeam — Agent Command Center</title>
<style>
:root{--bg:#070a10;--panel:#0d131e;--panel2:#101824;--line:#202c3d;--text:#eaf1fb;--muted:#7f8da3;--ok:#63e6be;--blue:#67b7ff;--warn:#ffd166;--bad:#ff6b7a}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 20% 0%,#102331 0,#070a10 38%);color:var(--text);font-family:Inter,system-ui,Segoe UI,sans-serif}.shell{max-width:1500px;margin:auto;padding:22px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.brand{font-size:25px;font-weight:850;letter-spacing:-.7px}.brand i{font-style:normal;color:var(--ok)}.live{font-size:12px;color:var(--ok);border:1px solid #285545;background:#0c1816;padding:7px 11px;border-radius:999px}
.grid{display:grid;grid-template-columns:minmax(0,1.4fr) 390px;gap:16px}.card{background:linear-gradient(145deg,#0e1520,#0a1018);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 14px 40px #0007;margin-bottom:16px}h2{font-size:15px;margin:0 0 13px}p{color:var(--muted);font-size:13px}
textarea,input{width:100%;border:1px solid #263448;background:#080d15;color:var(--text);padding:13px;border-radius:10px;outline:none}textarea{min-height:115px;resize:vertical}input{margin-top:9px}textarea:focus,input:focus{border-color:var(--ok)}
.actions{display:flex;gap:8px;align-items:center;margin-top:10px}button{border:0;border-radius:10px;padding:11px 16px;font-weight:800;cursor:pointer;background:var(--ok);color:#06110d}button.secondary{background:#182332;color:#cbd7e7;border:1px solid #2a394e}button:disabled{opacity:.45;cursor:not-allowed}
.flow{position:relative;padding:8px 0 4px}.flow:before{content:"";position:absolute;left:23px;top:23px;bottom:23px;width:2px;background:#223044}.agent{position:relative;display:grid;grid-template-columns:47px 1fr 80px;align-items:center;gap:9px;padding:8px 0}.icon{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#111b28;border:1px solid #2b3a50;z-index:1;font-size:15px}.agent .name{font-weight:750;font-size:13px}.agent small{display:block;color:var(--muted);font-size:11px;margin-top:2px}.state{font-size:10px;text-align:right;color:var(--muted);text-transform:uppercase}.agent.active .icon{border-color:var(--ok);box-shadow:0 0 0 5px #63e6be12,0 0 25px #63e6be33;animation:glow 1.2s infinite}.agent.active .name{color:var(--ok)}.agent.done .icon{border-color:var(--blue);color:var(--blue)}.agent.done .state{color:var(--blue)}.agent.wait .icon{border-color:var(--warn)}@keyframes glow{50%{transform:scale(1.08);box-shadow:0 0 0 9px #63e6be08,0 0 30px #63e6be55}}
.log{height:205px;overflow:auto;background:#06090e;border:1px solid #1b2635;border-radius:10px;padding:11px;font:11px ui-monospace,SFMono-Regular,Consolas,monospace}.entry{padding:5px 0;border-bottom:1px solid #111925;color:#91a0b4}.entry b{color:var(--ok)}.caps{display:flex;flex-wrap:wrap;gap:7px}.cap{font-size:11px;padding:7px 9px;border-radius:999px;background:#111a27;border:1px solid #26364c;color:#8d9bb0}.cap.ok{border-color:#286b57;color:#8ef0c7}.cap.no{opacity:.55}
.progress{height:6px;background:#111b27;border-radius:9px;overflow:hidden;margin:8px 0 2px}.bar{height:100%;width:0;background:linear-gradient(90deg,var(--ok),var(--blue));transition:width .4s}
.result{max-height:300px;overflow:auto;background:#05080d;border-radius:10px;padding:12px;color:#b7c4d6;font:11px ui-monospace,monospace;white-space:pre-wrap}
@media(max-width:900px){.grid{grid-template-columns:1fr}.agent{grid-template-columns:43px 1fr 65px}}
</style></head>
<body><div class="shell">
<header><div class="brand">Local<i>Agent</i>Team</div><div class="live">● LOCAL • READY</div></header>
<div class="grid"><main>
<div class="card"><h2>Task Command</h2><p>Describe what you want. The manager routes the work to installed existing providers.</p>
<textarea id="task" placeholder="Scan this restaurant menu, extract every item, verify completeness, prepare SEO content and stop for approval before publishing."></textarea>
<input id="url" placeholder="Source URL (optional)">
<div class="actions"><button id="start" onclick="runTask()">▶ Start Task</button><button class="secondary" id="clear" onclick="clearUI()">Clear</button><span id="state" style="font-size:12px;color:var(--muted)"></span></div>
<div class="progress"><div class="bar" id="bar"></div></div></div>
<div class="card"><h2>Live Agent Activity</h2><div class="log" id="log"><div class="entry"><b>READY</b> — awaiting task</div></div></div>
<div class="card"><h2>Output</h2><div class="result" id="result">No task output yet.</div></div>
</main>
<aside>
<div class="card"><h2>Execution Pipeline</h2><div class="flow" id="flow">
<div class="agent" data-k="manager"><div class="icon">◆</div><div><div class="name">Manager</div><small>task routing</small></div><div class="state">idle</div></div>
<div class="agent" data-k="browser"><div class="icon">◉</div><div><div class="name">Browser Use</div><small>browser interaction</small></div><div class="state">idle</div></div>
<div class="agent" data-k="crawler"><div class="icon">⌁</div><div><div class="name">Crawl4AI</div><small>web extraction</small></div><div class="state">idle</div></div>
<div class="agent" data-k="agent"><div class="icon">✦</div><div><div class="name">Existing AI Agent</div><small>reasoning / orchestration</small></div><div class="state">idle</div></div>
<div class="agent" data-k="qa"><div class="icon">✓</div><div><div class="name">QA + Approval</div><small>quality gate</small></div><div class="state">idle</div></div>
<div class="agent" data-k="github"><div class="icon">↥</div><div><div class="name">GitHub Publisher</div><small>publish after approval</small></div><div class="state">idle</div></div>
</div></div>
<div class="card"><h2>Installed Providers</h2><div class="caps" id="caps">Loading…</div></div>
</aside></div></div>
<script>
const $=x=>document.getElementById(x),sleep=ms=>new Promise(r=>setTimeout(r,ms));
function add(msg,type="INFO"){let d=document.createElement("div");d.className="entry";d.innerHTML="<b>"+type+"</b> — "+msg;$("log").appendChild(d);$("log").scrollTop=$("log").scrollHeight}
function node(k,state){let n=document.querySelector('[data-k="'+k+'"]');if(!n)return;n.classList.remove("active","done","wait");n.classList.add(state);n.querySelector(".state").textContent=state}
function resetNodes(){document.querySelectorAll(".agent").forEach(n=>{n.classList.remove("active","done","wait");n.querySelector(".state").textContent="idle"})}
function clearUI(){$("task").value="";$("url").value="";$("result").textContent="No task output yet.";$("bar").style.width="0%";$("log").innerHTML='<div class="entry"><b>READY</b> — awaiting task</div>';resetNodes()}
async function runTask(){
 const task=$("task").value.trim(),input_url=$("url").value.trim()||null;if(!task){add("Please enter a task","WAIT");return}
 $("start").disabled=true;$("state").textContent="Running…";resetNodes();node("manager","active");$("bar").style.width="10%";add("Manager accepted the task");await sleep(450);
 try{
  const rr=await fetch("/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const route=await rr.json();
  node("manager","done");add("Route selected: "+route.route,"ROUTE");$("bar").style.width="20%";
  let key=route.route==="crawl4ai"?"crawler":route.route==="browser-use"?"browser":"agent";node(key,"active");
  if(key==="crawler"&&input_url){
   add("Crawl4AI started");$("bar").style.width="35%";const r=await fetch("/api/crawl",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const d=await r.json();node("crawler",d.error?"wait":"done");$("bar").style.width="70%";add(d.error||"Crawl/extraction completed","DONE");$("result").textContent=JSON.stringify(d,null,2);
  }else if(key==="agent"){
   add("Existing agent provider started");$("bar").style.width="35%";const r=await fetch("/api/agent",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,input_url})});const d=await r.json();node("agent",d.error?"wait":"done");$("bar").style.width="70%";add(d.error||"Agent completed","DONE");$("result").textContent=JSON.stringify(d,null,2);
  }else{add("This route needs an installed provider","WAIT");$("result").textContent=JSON.stringify(route,null,2)}
  node("qa","active");$("bar").style.width="82%";add("QA / approval gate reached","QA");await sleep(350);node("qa","wait");add("Publishing remains blocked until human approval","HOLD");$("bar").style.width="88%";
 }catch(e){add(e.message||String(e),"ERROR");$("result").textContent=String(e);node("qa","wait")}
 $("start").disabled=false;$("state").textContent="Waiting for approval"; 
}
async function load(){const r=await fetch("/api/capabilities");const d=await r.json();$("caps").innerHTML=d.map(x=>'<span class="cap '+(x.available?"ok":"no")+'">'+x.provider+" · "+(x.available?"READY":"MISSING")+"</span>").join("")}load();
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
