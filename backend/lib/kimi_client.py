import asyncio
import os
import time
import uuid

import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client: OpenAI | None = None

_file_content_cache: dict[str, str] = {}
_base_messages_cache: dict[frozenset, list[dict]] = {}

SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "system_prompt.md")

with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

MODEL = "moonshotai/kimi-k2.6"

_LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


class TruncatedOutputError(RuntimeError):
    pass


def get_client() -> OpenAI:
    global _client
    if _client is None:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        load_dotenv(env_path, override=True)
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        print(f"[K2.5] Using API key: {api_key[:8]}...{api_key[-4:]}")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=300.0,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Better Learning Content Generator",
            },
        )
    return _client


def _extract_pdf_text(file_bytes: bytes) -> str:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n\n".join(page.get_text() for page in doc)


def _build_base_messages(local_ids: list[str]) -> list[dict]:
    file_texts = [
        _file_content_cache[lid]
        for lid in local_ids
        if lid in _file_content_cache
    ]
    base = [{"role": "system", "content": SYSTEM_PROMPT}]
    if file_texts:
        context = "[CONTEXT_PAYLOAD]\n\n" + "\n\n---\n\n".join(file_texts)
        base.append({"role": "system", "content": context})
    return base


async def upload_file(file_bytes: bytes, filename: str, mime_type: str) -> dict:
    file_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _extract_pdf_text, file_bytes)
    _file_content_cache[file_id] = text
    return {"uri": f"local://{file_id}", "mime_type": "application/pdf"}


def _dump_failed_raw(raw: str) -> None:
    try:
        os.makedirs(_LOGS_DIR, exist_ok=True)
        path = os.path.join(_LOGS_DIR, f"failed_{int(time.time())}_{uuid.uuid4().hex[:8]}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(raw)
        print(f"[K2.5] Raw output saved to {path}")
    except Exception as e:
        print(f"[K2.5] Could not save raw output: {e}")


def _stream_completion(client: OpenAI, messages: list[dict], model: str = MODEL) -> tuple[str, str | None, dict]:
    """Returns (raw_text, finish_reason, token_usage)."""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_completion_tokens=65536,
        temperature=1.0,
        stream=True,
        stream_options={"include_usage": True},
    )

    raw = ""
    finish_reason = None
    usage = None

    for chunk in stream:
        if chunk.choices:
            choice = chunk.choices[0]
            if choice.delta.content:
                raw += choice.delta.content
            if choice.finish_reason:
                finish_reason = choice.finish_reason
        if getattr(chunk, "usage", None) is not None:
            usage = chunk.usage

    if usage:
        cached = 0
        if getattr(usage, "prompt_tokens_details", None):
            cached = getattr(usage.prompt_tokens_details, "cached_tokens", 0) or 0
        print(
            f"[K2.5] in={usage.prompt_tokens} (cached={cached}) "
            f"out={usage.completion_tokens} | finish={finish_reason} | len={len(raw)}"
        )
        token_usage = {"input": usage.prompt_tokens, "cached": cached, "output": usage.completion_tokens}
    else:
        print(f"[K2.5] len={len(raw)} | finish={finish_reason} (no usage data)")
        token_usage = {"input": 0, "cached": 0, "output": 0}

    return raw, finish_reason, token_usage


async def run_worker(file_uris: list, worker_prompt: str) -> dict:
    client = get_client()
    loop = asyncio.get_event_loop()

    def _run():
        local_ids = []
        for f in file_uris:
            uri = f.uri if hasattr(f, "uri") else f["uri"]
            if uri.startswith("local://"):
                local_ids.append(uri[len("local://"):])
        cache_key = frozenset(local_ids)

        if cache_key not in _base_messages_cache:
            _base_messages_cache[cache_key] = _build_base_messages(local_ids)

        base_messages = _base_messages_cache[cache_key]
        messages = base_messages + [{"role": "user", "content": worker_prompt}]

        raw, finish_reason, token_usage = _stream_completion(client, messages)

        if finish_reason == "length":
            raise TruncatedOutputError(
                f"Worker output was truncated (finish_reason=length, {len(raw)} chars). "
                "Hit provider-side token limit before output was complete."
            )

        result = raw.strip()

        # Retry if output is empty or a fail-fast error signal
        if not result or result == "ERROR: CONSTRAINT_VIOLATION":
            _dump_failed_raw(raw)
            retry_messages = messages + [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": (
                        "Your previous reply was empty or returned a constraint violation. "
                        "Please provide the complete Markdown output now."
                    ),
                },
            ]
            retry_raw, retry_finish_reason, retry_usage = _stream_completion(client, retry_messages)
            token_usage = {
                "input": token_usage["input"] + retry_usage["input"],
                "cached": token_usage["cached"] + retry_usage["cached"],
                "output": token_usage["output"] + retry_usage["output"],
            }
            result = retry_raw.strip()

        return {"result": result, "usage": token_usage}

    return await loop.run_in_executor(None, _run)


PARSE_MODEL = "moonshotai/kimi-k2.5"

_PARSE_SYSTEM = (
    "You extract chapter lists from CBSE syllabus documents. "
    'Return only valid JSON in the form {"chapters": ["Chapter name 1", ...]}. '
    "No prose, no markdown fences."
)


async def parse_syllabus_chapters(syllabus_uri: str, class_num: str, subject: str) -> list[str]:
    client = get_client()
    loop = asyncio.get_event_loop()

    def _run() -> list[str]:
        file_id = syllabus_uri[len("local://"):]
        syllabus_text = _file_content_cache.get(file_id, "")
        if not syllabus_text.strip():
            raise ValueError("Syllabus file contains no extractable text. Try a text-based PDF.")

        messages = [
            {"role": "system", "content": _PARSE_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Extract the list of chapters for Class {class_num} {subject} "
                    f"from the syllabus below. If the document covers multiple classes, "
                    f"include only chapters belonging to Class {class_num}.\n\n"
                    f"{syllabus_text}"
                ),
            },
        ]

        raw, finish_reason, usage = _stream_completion(client, messages, model=PARSE_MODEL)
        print(
            f"[K2.5 PARSE] in={usage['input']} (cached={usage['cached']}) "
            f"out={usage['output']} | finish={finish_reason} | len={len(raw)}"
        )

        import json as _json
        try:
            text = raw.strip()
            # Strip markdown fences if the model ignores the instruction
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = _json.loads(text)
            chapters = data.get("chapters", [])
            if not isinstance(chapters, list) or not chapters:
                raise ValueError("Parsed JSON has no chapters list.")
            return [str(c) for c in chapters if str(c).strip()]
        except Exception as exc:
            _dump_failed_raw(raw)
            raise ValueError(f"Could not parse chapter list from syllabus: {exc}") from exc

    return await loop.run_in_executor(None, _run)
