import json,time
from pathlib import Path
DATA=Path("/data"); DATA.mkdir(exist_ok=True)
print("Tarkiq7 executor middleware ready: isolated Docker replica")
while True:
    for p in DATA.glob("*.json"):
        t=json.loads(p.read_text())
        if t.get("status")=="APPROVED_QUEUED":
            t["status"]="COMPLETED" if t.get("execution",{}).get("mode")=="mock" else "BLOCKED_REAL_EXECUTION"
            t["result"]={"verified":t["status"]=="COMPLETED","actions":[],"message":"Mock execution completed. Configure a reviewed adapter before real AWS mutations."}
            p.write_text(json.dumps(t,indent=2))
    time.sleep(2)
