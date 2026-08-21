import json,time,os
from pathlib import Path
DATA=Path(os.getenv("DATA_DIR","/data")); DATA.mkdir(parents=True,exist_ok=True)
print("Tarkiq7 executor middleware ready: isolated Docker replica", flush=True)
while True:
    for p in DATA.glob("*.json"):
        t=json.loads(p.read_text(encoding="utf-8"))
        if t.get("status")=="APPROVED_QUEUED":
            t["status"]="COMPLETED" if t.get("execution",{}).get("mode")=="mock" else "BLOCKED_REAL_EXECUTION"
            t["result"]={"verified":t["status"]=="COMPLETED","actions":[],"message":"Mock execution completed. Configure a reviewed adapter before real AWS mutations."}
            p.write_text(json.dumps(t,indent=2), encoding="utf-8")
    time.sleep(2)
