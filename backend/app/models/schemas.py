from pydantic import BaseModel, Field
from typing import Any

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2)

class QueryResponse(BaseModel):
    answer: str
    cypher: str | None = None
    graph_results: list[dict[str, Any]] = []

class GraphNode(BaseModel):
    id: str
    label: str
    type: str = "Entity"

class GraphEdge(BaseModel):
    source: str
    target: str
    label: str
