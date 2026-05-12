import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.text_extraction import extract_text_from_file, chunk_text
from app.services.extraction_service import llm_extract
from app.services.graph_service import create_document_graph
from app.services.supabase_service import save_document_metadata, list_documents

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    temp_path = None
    allowed = [".pdf", ".txt", ".md"]
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=415, detail="Only PDF, TXT, and MD files are supported")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
            content = await file.read()
            temp.write(content)
            temp_path = temp.name

        text = extract_text_from_file(temp_path)
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="No readable text found in the uploaded document")

        extracted_items = [llm_extract(chunk) for chunk in chunks[:8]]
        entity_count = sum(len(item.get("entities", [])) for item in extracted_items)
        doc_id = create_document_graph(file.filename or "uploaded_document", chunks, extracted_items)
        save_document_metadata(doc_id, file.filename or "uploaded_document", "completed", len(chunks), entity_count)

        return {
            "message": "Document uploaded and graph created successfully",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunk_count": len(chunks),
            "entity_count": entity_count,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass

@router.get("")
def get_documents():
    return {"items": list_documents()}
