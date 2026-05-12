from fastapi import APIRouter
from app.models.schemas import QueryRequest
from app.services.query_service import answer_question
from app.services.supabase_service import list_query_history

router = APIRouter(tags=["Query Engine"])

@router.post("/api/query")
def query_graph(payload: QueryRequest):
    return answer_question(payload.question)

# Alias kept for the simple test frontend and manual Postman tests.
@router.post("/query")
def query_graph_alias(payload: QueryRequest):
    return answer_question(payload.question)

@router.get("/api/query/history")
def query_history():
    return {"items": list_query_history()}
