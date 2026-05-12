from fastapi import APIRouter
from app.services.graph_service import get_graph, setup_constraints
from app.database.neo4j_connection import neo4j_db
from app.services.supabase_service import is_supabase_enabled

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("")
def graph_data(limit: int = 100):
    return get_graph(limit)

@router.get("/health")
def database_health():
    neo4j_status = "down"
    try:
        neo4j_db.connect()
        setup_constraints()
        neo4j_status = "connected"
    except Exception as exc:
        neo4j_status = f"error: {str(exc)}"
    return {
        "neo4j": neo4j_status,
        "supabase": "connected" if is_supabase_enabled() else "not configured",
    }
