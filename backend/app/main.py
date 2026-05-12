from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.documents import router as documents_router
from app.routes.query import router as query_router
from app.routes.graph import router as graph_router
from app.database.neo4j_connection import neo4j_db

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Knowledge Graph + LLM Query Engine API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://knowledge-graph-llm-query-engine.onrender.com",
        "https://knowledge-graph-llm.onrender.com",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(query_router)
app.include_router(graph_router)


@app.get("/")
def home():
    return {
        "message": "Knowledge Graph LLM Engine is running",
        "docs": "/docs",
        "health": "/health",
        "graph_health": "/api/graph/health"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Backend server is running",
        "docs": "/docs",
        "graph_health": "/api/graph/health"
    }


@app.on_event("shutdown")
def shutdown_event():
    neo4j_db.close()
