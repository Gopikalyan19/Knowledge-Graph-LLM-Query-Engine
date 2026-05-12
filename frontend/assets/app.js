const API_BASE_URL = localStorage.getItem('KG_API_URL') || 'https://knowledge-graph-llm-query-engine.onrender.com';

function setStatus(id, message, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.className = isError ? 'text-sm text-red-700 mt-3 whitespace-pre-wrap' : 'text-sm text-green-700 mt-3 whitespace-pre-wrap';
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/graph/health`);
    const data = await res.json();
    setStatus('healthStatus', `Neo4j: ${data.neo4j}\nSupabase: ${data.supabase}`);
  } catch (err) {
    setStatus('healthStatus', 'Backend is not reachable. Start FastAPI first.', true);
  }
}

async function uploadDocument(event) {
  event.preventDefault();
  const fileInput = document.getElementById('file');
  if (!fileInput.files.length) {
    setStatus('uploadStatus', 'Please select a PDF, TXT, or MD file.', true);
    return;
  }
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  setStatus('uploadStatus', 'Uploading and creating graph. Please wait...');
  try {
    const res = await fetch(`${API_BASE_URL}/api/documents/upload`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    setStatus('uploadStatus', JSON.stringify(data, null, 2));
  } catch (err) {
    setStatus('uploadStatus', err.message, true);
  }
}

async function askQuestion(event) {
  event.preventDefault();
  const question = document.getElementById('question').value.trim();
  if (!question) return;
  setStatus('queryStatus', 'Thinking...');
  document.getElementById('answerBox').textContent = '';
  document.getElementById('cypherBox').textContent = '';
  try {
    const res = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Query failed');
    document.getElementById('answerBox').textContent = data.answer;
    document.getElementById('cypherBox').textContent = data.cypher || '';
    setStatus('queryStatus', 'Answer generated successfully.');
  } catch (err) {
    setStatus('queryStatus', err.message, true);
  }
}

async function loadGraph() {
  const container = document.getElementById('cy');
  if (!container) return;
  try {
    const res = await fetch(`${API_BASE_URL}/api/graph?limit=150`);
    const data = await res.json();
    const elements = [];
    data.nodes.forEach(n => elements.push({ data: { id: n.id, label: n.label, type: n.type } }));
    data.edges.forEach((e, i) => elements.push({ data: { id: `e${i}`, source: e.source, target: e.target, label: e.label } }));
    cytoscape({
      container,
      elements,
      style: [
        { selector: 'node', style: { 'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'font-size': 10, 'width': 42, 'height': 42, 'background-color': '#2563eb', 'color': '#111827', 'text-wrap': 'wrap', 'text-max-width': 90 } },
        { selector: 'edge', style: { 'label': 'data(label)', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'font-size': 8, 'line-color': '#9ca3af', 'target-arrow-color': '#9ca3af' } }
      ],
      layout: { name: 'cose', animate: true }
    });
  } catch (err) {
    container.innerHTML = `<p class="text-red-700 p-4">${err.message}</p>`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('healthStatus')) checkHealth();
  const uploadForm = document.getElementById('uploadForm');
  if (uploadForm) uploadForm.addEventListener('submit', uploadDocument);
  const queryForm = document.getElementById('queryForm');
  if (queryForm) queryForm.addEventListener('submit', askQuestion);
  if (document.getElementById('cy')) loadGraph();
});
