from fastapi import APIRouter, Query
from database import AUDIT_LOGS, TENANTS, CONFIGURATIONS, ADAPTERS
from typing import Optional

router = APIRouter()

# ⚠️ Static routes FIRST, then dynamic routes
@router.get("/stats")
def get_stats():
    return {
        "total_adapters": len(ADAPTERS),
        "total_configurations": len(CONFIGURATIONS),
        "total_audit_events": len(AUDIT_LOGS),
        "active_configurations": sum(1 for c in CONFIGURATIONS.values() if c["status"] == "active"),
        "tenants": len(TENANTS),
    }


@router.get("/tenants")
def list_tenants():
    return {"tenants": [{"id": k, **v} for k, v in TENANTS.items()]}


@router.get("/")
def get_audit_logs(
    tenant_id: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    logs = AUDIT_LOGS[::-1]  # newest first
    if tenant_id:
        logs = [l for l in logs if l["tenant_id"] == tenant_id]
    if action:
        logs = [l for l in logs if l["action"] == action]
    return {"logs": logs[:limit], "total": len(logs)}
