from fastapi import APIRouter, HTTPException, Query
from database import ADAPTERS
from typing import Optional

router = APIRouter()

@router.get("/")
def list_adapters(category: Optional[str] = Query(default=None)):
    adapters = list(ADAPTERS.values())
    if category:
        adapters = [a for a in adapters if a["category"].lower() == category.lower()]
    return {"adapters": adapters, "total": len(adapters)}


@router.get("/categories")
def list_categories():
    cats = list(set(a["category"] for a in ADAPTERS.values()))
    return {"categories": sorted(cats)}


# ⚠️ /{adapter_id}/versions MUST come before /{adapter_id}
# otherwise FastAPI matches "cibil-v3/versions" as adapter_id
@router.get("/{adapter_id}/versions")
def get_versions(adapter_id: str):
    adapter = ADAPTERS.get(adapter_id)
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return {
        "adapter_id": adapter_id,
        "name": adapter["name"],
        "current_version": adapter["version"],
        "available_versions": adapter["versions"],
    }


@router.get("/{adapter_id}")
def get_adapter(adapter_id: str):
    adapter = ADAPTERS.get(adapter_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Adapter '{adapter_id}' not found.")
    return adapter
