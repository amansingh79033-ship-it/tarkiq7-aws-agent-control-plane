# Tarkiq7 AWS Agent Control Plane

A safety-first AWS operations agent: every task is planned, policy-checked, proposed for review, and only executed after explicit approval. Approved work runs in an isolated Docker replica middleware.

## Quick start

```powershell
Copy-Item .env.example .env
# set ANTHROPIC_API_KEY and optionally COMPOSIO_API_KEY
docker compose up --build
Start-Process http://localhost:8080
```

This repository is an extensible control-plane starter. AWS mutations are intentionally disabled by default. Set `EXECUTION_MODE=mock` for safe demos. Add an audited Composio/AWS adapter before enabling real AWS execution.
