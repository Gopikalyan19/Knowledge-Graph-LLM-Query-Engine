import uuid
from app.database.neo4j_connection import neo4j_db


def setup_constraints():
    queries = [
        "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
        "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.doc_id IS UNIQUE",
    ]
    for query in queries:
        neo4j_db.run_write(query)


def create_document_graph(filename: str, chunks: list[str], extracted_items: list[dict]) -> str:
    setup_constraints()
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"

    neo4j_db.run_write(
        "MERGE (d:Document {doc_id: $doc_id}) SET d.filename=$filename, d.chunk_count=$chunk_count, d.created_at=datetime()",
        {"doc_id": doc_id, "filename": filename, "chunk_count": len(chunks)},
    )

    for index, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{index}"
        neo4j_db.run_write(
            """
            MATCH (d:Document {doc_id: $doc_id})
            MERGE (c:Chunk {chunk_id: $chunk_id})
            SET c.text=$text, c.index=$index
            MERGE (d)-[:CONTAINS]->(c)
            """,
            {"doc_id": doc_id, "chunk_id": chunk_id, "text": chunk[:4000], "index": index},
        )

    for item in extracted_items:
        for entity in item.get("entities", []):
            neo4j_db.run_write(
                """
                MATCH (d:Document {doc_id: $doc_id})
                MERGE (e:Entity {name: $name})
                SET e.type = coalesce(e.type, $type), e.updated_at=datetime()
                MERGE (d)-[:MENTIONS]->(e)
                """,
                {"doc_id": doc_id, "name": entity.get("name"), "type": entity.get("type", "Entity")},
            )

        for rel in item.get("relationships", []):
            relation = rel.get("relation", "RELATED_TO") or "RELATED_TO"
            relation = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in relation.upper())[:40]
            if not rel.get("source") or not rel.get("target"):
                continue
            query = f"""
            MERGE (a:Entity {{name: $source}})
            MERGE (b:Entity {{name: $target}})
            MERGE (a)-[r:{relation}]->(b)
            SET r.updated_at=datetime()
            """
            neo4j_db.run_write(query, {"source": rel["source"], "target": rel["target"]})

    return doc_id


def get_graph(limit: int = 100):
    rows = neo4j_db.run_read(
        """
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.name AS source, coalesce(a.type,'Entity') AS source_type,
               type(r) AS relation,
               b.name AS target, coalesce(b.type,'Entity') AS target_type
        LIMIT $limit
        """,
        {"limit": limit},
    )
    nodes = {}
    edges = []
    for row in rows:
        nodes[row["source"]] = {"id": row["source"], "label": row["source"], "type": row["source_type"]}
        nodes[row["target"]] = {"id": row["target"], "label": row["target"], "type": row["target_type"]}
        edges.append({"source": row["source"], "target": row["target"], "label": row["relation"]})
    return {"nodes": list(nodes.values()), "edges": edges}
