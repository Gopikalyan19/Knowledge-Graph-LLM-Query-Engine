from app.database.supabase_connection import supabase_db


def is_supabase_enabled() -> bool:
    try:
        return supabase_db.connect() is not None
    except Exception:
        return False


def save_document_metadata(doc_id: str, filename: str, status: str, chunk_count: int, entity_count: int = 0):
    try:
        client = supabase_db.connect()
        if client is None:
            return None
        data = {
            "doc_id": doc_id,
            "filename": filename,
            "status": status,
            "chunk_count": chunk_count,
            "entity_count": entity_count,
        }
        return client.table("documents").insert(data).execute().data
    except Exception:
        # Supabase is optional for MVP. Do not break graph creation if tables/keys are not ready.
        return None


def update_document_status(doc_id: str, status: str, entity_count: int = 0):
    try:
        client = supabase_db.connect()
        if client is None:
            return None
        return client.table("documents").update({"status": status, "entity_count": entity_count}).eq("doc_id", doc_id).execute().data
    except Exception:
        return None


def list_documents():
    try:
        client = supabase_db.connect()
        if client is None:
            return []
        return client.table("documents").select("*").order("created_at", desc=True).execute().data
    except Exception:
        return []


def save_query_history(question: str, cypher_query: str, answer: str):
    try:
        client = supabase_db.connect()
        if client is None:
            return None
        return client.table("query_history").insert({
            "question": question,
            "cypher_query": cypher_query,
            "answer": answer,
        }).execute().data
    except Exception:
        return None


def list_query_history():
    try:
        client = supabase_db.connect()
        if client is None:
            return []
        return client.table("query_history").select("*").order("created_at", desc=True).limit(50).execute().data
    except Exception:
        return []
