# Better Learning Content Generator

CBSE study-pack generator (Classes 9–12). Uploads PDFs, runs 5 parallel LLM workers, outputs a `.docx` file.

## Stack

- **Backend:** Python + FastAPI — `backend/` — `uvicorn main:app --reload` on port 8000
- **Frontend:** Vite + React + TypeScript — `frontend/` — `npm run dev` on port 5173
- **LLM:** `moonshotai/kimi-k2.5` via OpenRouter (OpenAI-compatible SDK)
- **PDF extraction:** PyMuPDF (`fitz`) — local, no remote file API
- **Output:** `python-docx` → `.docx` download

## Key files

| File | Purpose |
|------|---------|
| `backend/lib/kimi_client.py` | LLM client, PDF extraction, caching, token logging |
| `backend/lib/workers.py` | 5 `WorkerDefinition` objects (Core Learning → Tests) |
| `backend/lib/document.py` | Builds the Word document from worker results |
| `backend/main.py` | FastAPI endpoints; parallel worker orchestration via `asyncio.gather` |
| `system_prompt.md` | Master system prompt injected into every worker call |

## Environment

`backend/.env` needs one variable:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

## Generation pipeline

1. User uploads up to 4 PDFs (`syllabus`, `chapter`, `answers`, `all_chapters`) — frontend accepts `.pdf` only
2. `POST /api/upload` → `upload_file()` extracts text with PyMuPDF → cached by UUID → returns `local://<uuid>` URI
3. `POST /api/generate` → 5 workers fire **in parallel** via `asyncio.gather`
4. Each worker: system prompt + PDF context + worker prompt → streams JSON from `moonshotai/kimi-k2.5`
5. Results merged → `generate_document()` → `.docx` base64-encoded in SSE `complete` event

## Token logging

Per worker: `[K2.5] in=N (cached=N) out=N | len=N`  
Per generation: `[K2.5 TOTAL] in=N (cached=N, fresh=N) out=N`

Prompt caching is automatic on OpenRouter's Kimi provider — no extra headers needed. Cache primes on the first parallel worker; subsequent workers benefit on the stable prefix (system prompt + PDF context).

## Pending / deferred

- DOCX input support — `python-docx` is installed (used for output); just needs a read path + frontend `accept` change
- Committed `.env` file — rotate the OpenRouter key and add `.env` to `.gitignore`
