# Knowledge Graph + LLM Query Engine MVP

A working MVP with:

- FastAPI backend
- Neo4j / AuraDB graph storage
- Supabase metadata + query history storage
- OpenAI optional extraction and answering
- Static HTML + Tailwind + JavaScript frontend served by Vite

If `OPENAI_API_KEY` is empty, the backend still works with simple rule-based extraction.

---

## 1. Backend setup

```powershell
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`.

For Neo4j AuraDB, use:

```env
NEO4J_URI=neo4j+s://your-database-id.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

For Supabase:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

Then run:

```powershell
uvicorn app.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/docs
```

Health check:

```txt
http://127.0.0.1:8000/api/graph/health
```

---

## 2. Supabase setup

Open Supabase SQL Editor and run:

```txt
backend/supabase_schema.sql
```

This creates:

- `documents`
- `query_history`

The project still works if Supabase is not ready, but document metadata/history will not be saved.

---

## 3. Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Open:

```txt
http://localhost:5173
```

Pages:

- `/index.html` home
- `/upload.html` upload document
- `/query.html` ask question
- `/graph.html` visualize graph

---

## 4. First test document

Create `test.txt` with:

```txt
OpenAI created ChatGPT. Sam Altman leads OpenAI. Apple created iPhone.
```

Upload it using the Upload page.

Then ask:

```txt
Who created ChatGPT?
```

---

## 5. Common fixes

### Frontend works but query fails

Open backend logs. Also open:

```txt
http://127.0.0.1:8000/api/graph/health
```

### Neo4j fails

Check `.env`:

```env
NEO4J_USERNAME=neo4j
```

AuraDB usually uses `neo4j` as username.

### Supabase fails

Run `backend/supabase_schema.sql` in Supabase SQL Editor.

### Pydantic install fails

Use Python 3.12:

```powershell
py -3.12 -m venv venv
```

---

## 6. Important security note

Never upload or share your real `.env` file. Keep API keys private.
"# Knowledge-Graph-LLM-Query-Engine" 
