import json
from openai import OpenAI
from app.config import get_settings
from app.database.neo4j_connection import neo4j_db
from app.services.supabase_service import save_query_history

settings = get_settings()

SAFE_SCHEMA = """
Graph schema:
(:Document {doc_id, filename})-[:MENTIONS]->(:Entity {name, type})
(:Document)-[:CONTAINS]->(:Chunk {chunk_id, text, index})
(:Entity)-[:RELATED_TO|CREATED|FOUNDED|WORKS_AT|AUTHORED|MENTIONS|LEADS]->(:Entity)
"""


def simple_cypher(question: str):
    words = [w.strip("?.,!':;\"()").lower() for w in question.split() if len(w.strip("?.,!':;\"()")) > 2]
    keyword = words[-1] if words else ""
    return """
    MATCH (a:Entity)-[r]-(b:Entity)
    WHERE toLower(a.name) CONTAINS $keyword
       OR toLower(b.name) CONTAINS $keyword
       OR toLower(type(r)) CONTAINS $keyword
    RETURN a.name AS source, type(r) AS relation, b.name AS target
    LIMIT 25
    """, {"keyword": keyword}


def generate_cypher(question: str):
    if not settings.OPENAI_API_KEY:
        return simple_cypher(question)

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
You are a Neo4j Cypher expert. Convert the question into a safe read-only Cypher query.
Rules:
- Use only MATCH, OPTIONAL MATCH, WHERE, RETURN, ORDER BY, LIMIT.
- Never use CREATE, MERGE, DELETE, SET, CALL, LOAD CSV, APOC, DROP.
- Return columns named source, relation, target when possible.
- Always include LIMIT 25 or less.
{SAFE_SCHEMA}
Question: {question}
Return only valid JSON: {{"cypher":"...", "params":{{}}}}
"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(content)
        cypher = data.get("cypher", "")
        upper = cypher.upper()
        blocked = ["CREATE", "MERGE", "DELETE", " SET ", "CALL", "LOAD CSV", "DROP", "REMOVE"]
        if not cypher or any(bad in upper for bad in blocked):
            return simple_cypher(question)
        return cypher, data.get("params", {}) or {}
    except Exception:
        return simple_cypher(question)


def _fallback_answer(results: list[dict]) -> str:
    if not results:
        return "I could not find matching relationships in the knowledge graph yet. Upload a small TXT/PDF first, then ask about the entities in that document."
    lines = []
    for r in results[:10]:
        if {"source", "relation", "target"}.issubset(set(r.keys())):
            lines.append(f"{r.get('source')} --{r.get('relation')}--> {r.get('target')}")
        else:
            lines.append(json.dumps(r, ensure_ascii=False))
    return "I found these graph facts:\n" + "\n".join(lines)


def answer_question(question: str):
    cypher, params = generate_cypher(question)
    try:
        results = neo4j_db.run_read(cypher, params)
    except Exception as exc:
        # Retry once with the safe local query.
        try:
            cypher, params = simple_cypher(question)
            results = neo4j_db.run_read(cypher, params)
        except Exception as final_exc:
            return {
                "answer": "Backend reached, but Neo4j query failed. Check NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in backend/.env, then restart uvicorn.",
                "cypher": cypher,
                "graph_results": [],
                "error": str(final_exc),
            }

    answer = _fallback_answer(results)
    if settings.OPENAI_API_KEY and results:
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""
Answer the user using only these graph results. If results are weak, say what graph facts were found and avoid guessing.
Question: {question}
Graph results: {json.dumps(results, ensure_ascii=False)}
"""
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            answer = response.choices[0].message.content or answer
        except Exception:
            answer = _fallback_answer(results)

    save_query_history(question, cypher, answer)
    return {"answer": answer, "cypher": cypher, "graph_results": results}
