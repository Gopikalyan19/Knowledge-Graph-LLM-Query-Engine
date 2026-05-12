import json
import re
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


def _clean_relation(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_ ]", "", text).strip().upper().replace(" ", "_")
    return text[:40] or "RELATED_TO"


def rule_based_extract(text: str) -> dict:
    # Simple fallback: finds capitalized phrases and links nearby entities.
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){0,3}\b", text)
    stop = {"The", "This", "That", "These", "Those", "A", "An", "In", "On", "For", "And", "But", "With"}
    entities = []
    seen = set()
    for item in candidates:
        name = item.strip()
        if len(name) < 3 or name in stop or name.lower() in seen:
            continue
        seen.add(name.lower())
        entities.append({"name": name, "type": "Entity"})
        if len(entities) >= 15:
            break

    relationships = []
    for idx in range(len(entities) - 1):
        relationships.append({
            "source": entities[idx]["name"],
            "relation": "RELATED_TO",
            "target": entities[idx + 1]["name"],
        })
    return {"entities": entities, "relationships": relationships}


def llm_extract(text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return rule_based_extract(text)

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = f"""
Extract important entities and relationships from the text.
Return only valid JSON with this exact structure:
{{
  "entities": [{{"name": "...", "type": "Person|Organization|Concept|Product|Place|Document|Entity"}}],
  "relationships": [{{"source": "...", "relation": "...", "target": "..."}}]
}}
Text:
{text[:6000]}
"""
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(content)
        data["relationships"] = [
            {**rel, "relation": _clean_relation(rel.get("relation", "RELATED_TO"))}
            for rel in data.get("relationships", [])
        ]
        return data
    except Exception:
        return rule_based_extract(text)
