from fastapi import APIRouter, HTTPException
from database import ADAPTERS, CONFIGURATIONS, add_audit_log
from services.groq_service import generate_mock_response
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/run")
async def run_simulation(payload: dict):
    config_id = payload.get("config_id")
    adapter_id = payload.get("adapter_id")
    endpoint_index = payload.get("endpoint_index", 0)
    tenant_id = payload.get("tenant_id", "tenant-001")

    # Resolve adapter
    if config_id:
        cfg = CONFIGURATIONS.get(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="Configuration not found")
        adapter_id = cfg["adapter_id"]
        tenant_id = cfg["tenant_id"]

    adapter = ADAPTERS.get(adapter_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Adapter '{adapter_id}' not found.")

    endpoints = adapter.get("endpoints", [])
    if endpoint_index >= len(endpoints):
        raise HTTPException(status_code=400, detail=f"Endpoint index {endpoint_index} out of range.")

    endpoint = endpoints[endpoint_index]
    mock_response = generate_mock_response(adapter, endpoint)

    sim_id = str(uuid.uuid4())
    result = {
        "simulation_id": sim_id,
        "adapter_id": adapter_id,
        "adapter_name": adapter["name"],
        "tenant_id": tenant_id,
        "endpoint": endpoint,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "result": mock_response,
        "sla_target_ms": adapter.get("sla_ms", 1000),
        "sla_breached": mock_response.get("response_time_ms", 0) > adapter.get("sla_ms", 1000),
    }

    add_audit_log(
        action="SIMULATION_RUN",
        entity="simulation",
        entity_id=sim_id,
        tenant_id=tenant_id,
        details={"adapter_id": adapter_id, "endpoint": endpoint["path"]},
    )

    return result


@router.post("/batch")
async def run_batch_simulation(payload: dict):
    """Simulate all endpoints of an adapter at once."""
    adapter_id = payload.get("adapter_id")
    tenant_id = payload.get("tenant_id", "tenant-001")

    adapter = ADAPTERS.get(adapter_id)
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    results = []
    for i, endpoint in enumerate(adapter.get("endpoints", [])):
        mock = generate_mock_response(adapter, endpoint)
        results.append({
            "endpoint": endpoint,
            "result": mock,
            "sla_breached": mock.get("response_time_ms", 0) > adapter.get("sla_ms", 1000),
        })

    add_audit_log("BATCH_SIMULATION", "simulation", str(uuid.uuid4()), tenant_id,
                  {"adapter_id": adapter_id, "endpoints_tested": len(results)})

    return {
        "adapter_id": adapter_id,
        "adapter_name": adapter["name"],
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_endpoints": len(results),
        "results": results,
    }
