import json, time, os
from datetime import datetime, timezone
from pathlib import Path

DATA=Path(os.getenv("DATA_DIR","/data")); DATA.mkdir(parents=True,exist_ok=True)
print("Tarkiq7 executor middleware ready: isolated Docker replica", flush=True)

def persist(path, task):
    path.write_text(json.dumps(task, indent=2), encoding="utf-8")

def execute_task(task):
    """Return only after the selected execution adapter has finished."""
    mode=task.get("execution",{}).get("mode", os.getenv("EXECUTION_MODE","mock"))
    if mode != "mock":
        return {
            "status":"BLOCKED_REAL_EXECUTION",
            "result":{"verified":False,"actions":[],"message":"Real AWS execution is disabled until a reviewed adapter is configured."}
        }
    # The mock adapter represents the complete deterministic task execution.
    return {
        "status":"COMPLETED",
        "result":{"verified":True,"actions":[],"message":"Mock execution completed. Configure a reviewed adapter before real AWS mutations."}
    }

while True:
    for p in DATA.glob("*.json"):
        task=json.loads(p.read_text(encoding="utf-8"))
        # RUNNING is intentionally resumed after a restart; it is not terminal.
        if task.get("status") not in ("APPROVED_QUEUED","RUNNING"):
            continue
        if task.get("status")=="APPROVED_QUEUED":
            task["status"]="RUNNING"
            execution=task.setdefault("execution",{})
            execution["phase"]="RUNNING"
            execution["started_at"]=datetime.now(timezone.utc).isoformat()
            persist(p, task)
            continue
        outcome=execute_task(task)
        execution=task.setdefault("execution",{})
        execution["phase"]="COMPLETED" if outcome["status"]=="COMPLETED" else "BLOCKED"
        execution["completed_at"]=datetime.now(timezone.utc).isoformat()
        task["status"]=outcome["status"]
        task["result"]=outcome["result"]
        persist(p, task)
    time.sleep(2)
