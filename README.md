# ⚡ LODEX Middleware

> **Decoupled, Multi-Tenant Knowledge Indexing and Grounded Retrieval Engine for Web Applications**  
> Built with Python 3.10+, FastAPI, and Qdrant Vector Database.

---

## 🎯 Key Features

1. **Strict Multi-Tenant Isolation**: Enforces tenant boundary partitioning via API keys (`X-API-Key`) and Qdrant metadata payload filtering. Zero cross-tenant data leakage.
2. **Dual-Mode Serving**:
   - **`POST /v1/search`**: Pure semantic vector retrieval returning ranked chunks, scores, and metadata without LLM synthesis (ideal for search bars, catalogs, and carousels like `jiulibrary`).
   - **`POST /v1/ask`**: Grounded conversational synthesis providing factual answers with verifiable citations and source links (ideal for procedural assistants like `staff_portal`).
3. **Decoupled & Language-Agnostic**: Any client application written in TypeScript/Next.js, PHP/Laravel, Go, Python, or Ruby can integrate with simple JSON REST requests.
4. **Flexible Runtime**: Runs 100% locally with embedded Qdrant (zero Docker required for development) or scaled via Docker Compose.

---

## 📁 Project Structure

```
corerag/
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Optional Qdrant container config
├── .env.example                # Configuration template
├── src/
│   ├── main.py                 # FastAPI application entrypoint & docs
│   ├── config.py               # Pydantic environment settings
│   ├── core/
│   │   ├── security.py         # API key validation & tenant resolution
│   │   ├── vector_store.py     # Qdrant client & isolated tenant filtering
│   │   ├── embeddings.py       # Modular embedding provider
│   │   └── llm.py              # Grounded synthesis provider
│   ├── models/
│   │   ├── tenant.py           # Tenant context models
│   │   ├── document.py         # Ingestion schemas & chunk payloads
│   │   └── query.py            # Search & Ask request/response schemas
│   └── api/
│       ├── dependencies.py     # FastAPI dependencies (X-API-Key auth)
│       └── v1/
│           ├── router.py       # Aggregated v1 endpoints
│           ├── documents.py    # POST & DELETE /v1/documents
│           ├── search.py       # POST /v1/search
│           └── ask.py          # POST /v1/ask
└── tests/
    ├── conftest.py             # Pytest configuration & fixtures
    └── test_tenant_isolation.py# Automated multi-tenant security verification
```

---

## 🚀 Quickstart Guide

### 1. Setup Environment
```bash
cd "d:/Learning Agents/Skripsi/04-kode/corerag"

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment settings
copy .env.example .env
```

### 2. Run the Development Server
```bash
uvicorn src.main:app --reload --port 8000
```

Once running, access the interactive Swagger documentation at:  
👉 **http://localhost:8000/docs**

### 3. Run Automated Multi-Tenant Security Tests
```bash
pytest
```

---

## 🔌 API Client Integration Examples

### Example 1: `jiulibrary` (Next.js / TypeScript)
```typescript
// Call CoreRAG Semantic Search for catalog exploration
const response = await fetch('http://localhost:8000/v1/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'key_jiulibrary_secret_123',
  },
  body: JSON.stringify({
    query: 'Buku sejarah transisi politik peradaban',
    limit: 5,
  }),
});

const data = await response.json();
console.log('Found books:', data.results);
```

### Example 2: `staff_portal` (Laravel / PHP)
```php
// Call CoreRAG Grounded QA for employee SOP questions
$response = Http::withHeaders([
    'X-API-Key' => 'key_staffportal_secret_456',
])->post('http://localhost:8000/v1/ask', [
    'question' => 'Berapa hari batas maksimal cuti tahunan?',
    'limit' => 4,
]);

$answer = $response->json()['answer'];
$citations = $response->json()['citations'];
```
