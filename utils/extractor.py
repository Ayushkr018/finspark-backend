import io
from fastapi import UploadFile

async def extract_text(file: UploadFile) -> str:
    content = await file.read()
    fname = file.filename.lower()

    if fname.endswith(".pdf"):
        return _extract_pdf(content)
    elif fname.endswith(".docx"):
        return _extract_docx(content)
    elif fname.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    else:
        return content.decode("utf-8", errors="ignore")


def _extract_pdf(content: bytes) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def _extract_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"[DOCX extraction error: {e}]"
