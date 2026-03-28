from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from utils.extractor import extract_text
from services.groq_service import parse_document_with_ai
from database import add_audit_log
import uuid

router = APIRouter()

@router.post("/document")
async def parse_document(
    file: UploadFile = File(...),
    tenant_id: str = Form(default="tenant-001"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    allowed = {".pdf", ".docx", ".txt"}
    ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Use PDF, DOCX, or TXT.")

    text = await extract_text(file)
    if len(text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Document appears empty or unreadable.")

    result = parse_document_with_ai(text)

    session_id = str(uuid.uuid4())
    result["session_id"] = session_id
    result["tenant_id"] = tenant_id
    result["file_name"] = file.filename
    result["char_count"] = len(text)

    add_audit_log(
        action="DOCUMENT_PARSED",
        entity="document",
        entity_id=session_id,
        tenant_id=tenant_id,
        details={"file": file.filename, "services_found": len(result.get("detected_services", []))},
    )

    return result


@router.post("/text")
async def parse_text(payload: dict):
    """Parse raw text directly (useful for demo/testing)."""
    text = payload.get("text", "")
    tenant_id = payload.get("tenant_id", "tenant-001")
    if len(text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Text too short.")

    result = parse_document_with_ai(text)
    result["session_id"] = str(uuid.uuid4())
    result["tenant_id"] = tenant_id
    result["char_count"] = len(text)
    return result
