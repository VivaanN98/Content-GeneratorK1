import asyncio
import base64
import concurrent.futures
import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

load_dotenv()

# Sized for 5 concurrent users × 10 parallel workers = 50 simultaneous blocking LLM calls.
# Threads sleep on network I/O so this is safe on low-CPU hosts.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)

app = FastAPI(title="Vertex AI Content Generator")

_cors_env = os.getenv("CORS_ORIGINS", "http://localhost:5173")
_cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _install_executor():
    asyncio.get_event_loop().set_default_executor(_executor)


class FileUri(BaseModel):
    uri: str
    mime_type: str
    field_name: str


class GenerateRequest(BaseModel):
    class_num: str
    subject: str
    chapter: str
    file_uris: list[FileUri]


class ParseSyllabusRequest(BaseModel):
    syllabus_uri: str
    class_num: str
    subject: str


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/api/upload")
async def upload_file_endpoint(file: UploadFile, field_name: str = Form(...)):
    from lib.kimi_client import upload_file
    file_bytes = await file.read()
    result = await upload_file(file_bytes, file.filename, file.content_type or "application/pdf")
    return {
        "uri": result["uri"],
        "mime_type": result["mime_type"],
        "field_name": field_name,
        "file_name": file.filename,
    }


@app.post("/api/parse-syllabus")
async def parse_syllabus_endpoint(request: ParseSyllabusRequest):
    from lib.kimi_client import parse_syllabus_chapters
    try:
        chapters = await parse_syllabus_chapters(request.syllabus_uri, request.class_num, request.subject)
        return {"chapters": chapters}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Syllabus parsing failed: {e}")


@app.post("/api/generate")
async def generate_content(request: GenerateRequest):
    from lib.kimi_client import run_worker
    from lib.workers import WORKERS
    from lib.document import generate_document

    async def event_stream():
        try:
            yield sse_event("progress", {"worker": 0, "status": "cache", "message": "Preparing context..."})

            for worker in WORKERS:
                yield sse_event("progress", {
                    "worker": worker.id,
                    "status": "running",
                    "message": f"Running {worker.display_name}...",
                })

            prompts = [
                worker.prompt.format(
                    class_num=request.class_num,
                    subject=request.subject,
                    chapter=request.chapter,
                )
                for worker in WORKERS
            ]

            worker_results = await asyncio.gather(
                *(run_worker(request.file_uris, prompt) for prompt in prompts),
                return_exceptions=False,
            )

            # Aggregate token usage across all workers
            total_input = sum(r["usage"]["input"] for r in worker_results)
            total_cached = sum(r["usage"]["cached"] for r in worker_results)
            total_output = sum(r["usage"]["output"] for r in worker_results)
            print(
                f"[K2.5 TOTAL] in={total_input} "
                f"(cached={total_cached}, fresh={total_input - total_cached}) "
                f"out={total_output}"
            )

            results = {}
            for worker, worker_result in zip(WORKERS, worker_results):
                results[worker.name] = worker_result["result"]
                yield sse_event("progress", {
                    "worker": worker.id,
                    "status": "complete",
                    "message": f"{worker.display_name} complete",
                })

            yield sse_event("progress", {"worker": 11, "status": "document", "message": "Generating Word document..."})
            print(f"[MAIN] Starting generate_document at {time.time()}")
            doc_bytes = await asyncio.to_thread(generate_document, results, request.class_num, request.subject, request.chapter)
            print(f"[MAIN] generate_document returned {len(doc_bytes)} bytes at {time.time()}")
            doc_base64 = base64.b64encode(doc_bytes).decode("utf-8")
            print(f"[MAIN] base64 done, {len(doc_base64)} chars, sending SSE complete")

            filename = f"{request.chapter}_{request.subject}_Class{request.class_num}.docx"
            yield sse_event("complete", {"document": doc_base64, "file_name": filename})

        except Exception as e:
            yield sse_event("error", {"message": str(e)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
