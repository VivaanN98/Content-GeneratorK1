# Better Learning — Content Generator

CBSE study-pack generator for Classes 9–12. Upload chapter PDFs and get a fully structured `.docx` study pack in seconds, powered by **Bodhii** — an AI academic mentor tuned for Tier 2/3 Indian students.

## What it generates

A single `.docx` file containing all of the following, produced in parallel:

| Worker | Output |
|--------|--------|
| Core Learning | Chapter summary + deep-dive concepts (with foundational logic) |
| Memory | 35–50 flashcards, 10–20 key terms, 10–15 fun facts |
| Objective | 25 MCQs, 25 Very Short answers, 25 Short answers |
| Analytical | 25 Medium, 20 Long, 15 Assertion–Reason, 10 Case Studies |
| Tests | 2 full mock tests (25 marks each) |

## Stack

- **Backend:** Python + FastAPI (`backend/`) — port 8000
- **Frontend:** Vite + React + TypeScript (`frontend/`) — port 5173
- **LLM:** `moonshotai/kimi-k2.5` via OpenRouter
- **PDF extraction:** PyMuPDF (local, no remote file API)
- **Output:** `python-docx` → `.docx` download

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

Start the server:
```bash
uvicorn main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Usage

1. Upload up to 4 PDFs: **Syllabus**, **Chapter**, **Answers**, **All Chapters**
2. Enter subject, class, chapter name, and topic
3. Click **Generate** — all 5 workers run in parallel (~2–3 min)
4. Download the `.docx` when complete

## Project structure

```
backend/
  main.py           # FastAPI endpoints + asyncio.gather orchestration
  lib/
    kimi_client.py  # LLM client, PDF extraction, token logging
    workers.py      # 5 WorkerDefinition objects
    document.py     # Builds the Word document from worker results
  requirements.txt

frontend/
  src/
    App.tsx
    components/
      FileUpload.tsx
      GenerateForm.tsx
      ProgressTracker.tsx
    lib/api.ts

system_prompt.md    # Master system prompt (Bodhii vFINAL)
```

## Token logging

Each worker logs: `[K2.5] in=N (cached=N) out=N | len=N`  
After all workers: `[K2.5 TOTAL] in=N (cached=N, fresh=N) out=N`

Prompt caching is automatic on OpenRouter's Kimi provider — the stable prefix (system prompt + PDF context) is reused across all 5 parallel workers.
