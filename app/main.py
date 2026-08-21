import json, os, uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.getenv("DATA_DIR", str(ROOT / "data"))); DATA.mkdir(parents=True, exist_ok=True)
app=FastAPI(title="Tarkiq7 AWS Agent Control Plane")
app.mount("/ui",StaticFiles(directory=str(ROOT / "ui")),name="ui")
class Task(BaseModel):
    request:str
    environment:str="sandbox"
    account_alias:str="demo"

def persist(x):
    (DATA/f"{x['id']}.json").write_text(json.dumps(x,indent=2), encoding="utf-8")

@app.get("/")
def home(): return FileResponse(ROOT / "ui" / "index.html")
@app.get("/health")
def health(): return {"ok":True,"execution_mode":os.getenv("EXECUTION_MODE","mock"),"approval_required":os.getenv("APPROVAL_REQUIRED","true").lower()=="true"}
@app.get("/api/tasks")
def tasks(): return [json.loads(p.read_text(encoding="utf-8")) for p in DATA.glob("*.json")]
@app.post("/api/tasks")
def propose(t:Task):
    task={"id":str(uuid.uuid4()),"request":t.request,"environment":t.environment,"account_alias":t.account_alias,"status":"PROPOSED","created_at":datetime.now(timezone.utc).isoformat(),"plan":["Discover target resources read-only","Analyze dependencies and requested change","Run deterministic policy checks","Execute only in the isolated Docker replica after approval","Verify results and produce an audit report"],"policy":{"source_mutations":"DENY","production_mutations":"APPROVAL_REQUIRED","secrets":"NEVER_RETURN_VALUES","execution":"DOCKER_REPLICA"}}
    persist(task); return task
@app.post("/api/tasks/{task_id}/approve")
def approve(task_id:str):
    p=DATA/f"{task_id}.json"
    if not p.exists(): raise HTTPException(404,"task not found")
    task=json.loads(p.read_text(encoding="utf-8"))
    if task["status"]!="PROPOSED": raise HTTPException(409,"task is not awaiting approval")
    task["status"]="APPROVED_QUEUED"; task["execution"]={"middleware":"docker-replica","mode":os.getenv("EXECUTION_MODE","mock"),"note":"Queued for isolated executor; real AWS actions remain disabled in mock mode."}; persist(task)
    return task
