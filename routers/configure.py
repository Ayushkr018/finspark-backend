from fastapi import APIRouter, HTTPException
from database import ADAPTERS, CONFIGURATIONS, add_audit_log
from services.groq_service import generate_config_with_ai
from datetime import datetime
import uuid, copy

router = APIRouter()

@router.post("/generate")
async def generate_config(payload: dict):
    adapter_id = payload.get("adapter_id")
    requirements = payload.get("requirements", {})
    tenant_id = payload.get("tenant_id", "tenant-001")
    version = payload.get("version")

    if not adapter_id:
        raise HTTPException(status_code=400, detail="adapter_id is required")

    adapter = ADAPTERS.get(adapter_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Adapter '{adapter_id}' not found.")

    if version and version not in adapter["versions"]:
        raise HTTPException(
            status_code=400,
            detail=f"Version '{version}' not available. Choose from: {adapter['versions']}"
        )

    config = generate_config_with_ai(adapter, requirements, tenant_id)

    config_id = str(uuid.uuid4())
    config_record = {
        "id": config_id,
        "adapter_id": adapter_id,
        "adapter_name": adapter["name"],
        "tenant_id": tenant_id,
        "version": version or adapter["version"],
        "config": config,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    CONFIGURATIONS[config_id] = config_record

    add_audit_log(
        action="CONFIG_GENERATED",
        entity="configuration",
        entity_id=config_id,
        tenant_id=tenant_id,
        details={"adapter_id": adapter_id, "version": version or adapter["version"]},
    )

    return config_record


# ⚠️ IMPORTANT: /diff and /tenant/{tenant_id} MUST come before /{config_id}
# otherwise FastAPI will match "diff" and "tenant" as config_id values

@router.post("/diff")
def compare_configs(payload: dict):
    """Compare two configurations side by side."""
    id_a = payload.get("config_id_a")
    id_b = payload.get("config_id_b")
    cfg_a = CONFIGURATIONS.get(id_a)
    cfg_b = CONFIGURATIONS.get(id_b)
    if not cfg_a or not cfg_b:
        raise HTTPException(status_code=404, detail="One or both configurations not found")
    return {
        "config_a": {"id": id_a, "version": cfg_a["version"], "config": cfg_a["config"]},
        "config_b": {"id": id_b, "version": cfg_b["version"], "config": cfg_b["config"]},
    }


@router.get("/tenant/{tenant_id}")
def list_tenant_configs(tenant_id: str):
    configs = [c for c in CONFIGURATIONS.values() if c["tenant_id"] == tenant_id]
    return {"configurations": configs, "total": len(configs)}


@router.get("/{config_id}")
def get_config(config_id: str):
    cfg = CONFIGURATIONS.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return cfg


@router.post("/{config_id}/activate")
def activate_config(config_id: str):
    cfg = CONFIGURATIONS.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")
    cfg["status"] = "active"
    cfg["updated_at"] = datetime.utcnow().isoformat() + "Z"
    add_audit_log("CONFIG_ACTIVATED", "configuration", config_id, cfg["tenant_id"])
    return {"message": "Configuration activated", "config_id": config_id}


@router.post("/{config_id}/rollback")
def rollback_config(config_id: str):
    cfg = CONFIGURATIONS.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuration not found")
    cfg["status"] = "rolled_back"
    cfg["updated_at"] = datetime.utcnow().isoformat() + "Z"
    add_audit_log("CONFIG_ROLLED_BACK", "configuration", config_id, cfg["tenant_id"])
    return {"message": "Configuration rolled back", "config_id": config_id}
