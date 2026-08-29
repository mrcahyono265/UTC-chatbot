import os
import time
import json
import logging
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal
from urllib.error import HTTPError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.rag import context_from, load_retriever, retrieve_relevant, similarity_threshold

load_dotenv()
REQUESTS: dict[str, deque[float]] = defaultdict(deque)
PROVIDER_COOLDOWNS: dict[str, tuple[float, int | None]] = {}
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "12"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "256"))
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:4173").split(",")]
LOGGER = logging.getLogger(__name__)
REASONING_MARKERS = ("the user is asking", "let me check", "looking at the context", "the answer should", "need to respond", "context provided", "konteks yang diberikan", "proses berpikir")


@asynccontextmanager
async def lifespan(_: FastAPI):
    similarity_threshold()
    load_retriever()
    yield


app = FastAPI(title="UTC RAG API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)
    history: list["ChatTurn"] = Field(default_factory=list, max_length=4)


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    message: str = Field(min_length=1, max_length=500)


class Source(BaseModel):
    title: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    mode: str
    contact_admin: bool = False


def allow_request(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    attempts = REQUESTS[client]
    while attempts and now - attempts[0] > 60:
        attempts.popleft()
    if len(attempts) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Terlalu banyak permintaan. Coba lagi dalam satu menit.")
    attempts.append(now)


def unavailable_answer(mode: str) -> str:
    if mode == "unavailable-busy":
        return "Maaf, asisten sedang ramai. Untuk bantuan cepat, silakan hubungi admin UTC."
    return "Maaf, asisten sementara tidak tersedia. Silakan hubungi admin UTC untuk bantuan lebih lanjut."


def no_match_answer() -> str:
    return "Maaf, saya belum memiliki informasi yang cukup untuk pertanyaan tersebut. Silakan hubungi admin UTC untuk bantuan lebih lanjut."


def system_instruction(context: str) -> str:
    return f"""Anda adalah asisten chat UNIDA Technology Care (UTC).
Jawab Bahasa Indonesia, maksimal tiga kalimat pendek, hanya dari konteks ini.
Jangan membuat diagnosis, harga, durasi, janji layanan, analisis, atau instruksi internal.

KONTEKS:
{context}"""


def generate_with_gemini(question: str, context: str, history: list[ChatTurn]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = f"{system_instruction(context)}\n\nPERTANYAAN: {question}"
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        contents=[
            *[types.Content(role="model" if turn.role == "assistant" else "user", parts=[types.Part.from_text(text=turn.message)]) for turn in history],
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
        ],
        config=types.GenerateContentConfig(max_output_tokens=MAX_OUTPUT_TOKENS, temperature=0.2),
    )
    return response.text.strip() if response.text else ""


def generate_with_openai_compatible(url: str, api_key: str, model: str, question: str, context: str, history: list[ChatTurn]) -> str:
    messages = [
        {"role": "system", "content": system_instruction(context)},
        *[{"role": turn.role, "content": turn.message} for turn in history],
        {"role": "user", "content": question},
    ]
    request = UrlRequest(url, data=json.dumps({"model": model, "messages": messages, "max_tokens": MAX_OUTPUT_TOKENS, "temperature": 0.2}).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
        body = json.load(response)
    choice = body["choices"][0]
    if choice.get("finish_reason") == "length":
        raise ValueError("LLM response truncated")
    return choice["message"]["content"].strip()


def is_user_facing_answer(answer: str) -> bool:
    normalized = answer.lower()
    return bool(answer) and len(answer) <= 1000 and not any(marker in normalized for marker in REASONING_MARKERS)


def provider_status(error: Exception) -> int | None:
    return getattr(error, "code", None) or getattr(error, "status_code", None)


def unavailable_mode(failures: list[int | None]) -> str:
    return "unavailable-busy" if 429 in failures else "unavailable"


def generate_answer(question: str, context: str, history: list[ChatTurn]) -> tuple[str, str]:
    providers = []
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    if nvidia_api_key:
        providers.append(("nvidia", lambda: generate_with_openai_compatible(os.getenv("NVIDIA_CHAT_URL", "https://integrate.api.nvidia.com/v1/chat/completions"), nvidia_api_key, os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"), question, context, history)))
    if os.getenv("GEMINI_API_KEY"):
        providers.append(("gemini", lambda: generate_with_gemini(question, context, history)))
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        providers.append(("openrouter", lambda: generate_with_openai_compatible("https://openrouter.ai/api/v1/chat/completions", openrouter_api_key, os.getenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it:free"), question, context, history)))
    failures = []
    now = time.monotonic()
    for provider, generate in providers:
        if cooldown := PROVIDER_COOLDOWNS.get(provider):
            if cooldown[0] > now:
                failures.append(cooldown[1])
                continue
            del PROVIDER_COOLDOWNS[provider]
        try:
            if answer := generate():
                if not is_user_facing_answer(answer):
                    LOGGER.warning("LLM provider response rejected: %s", provider)
                    continue
                return answer, provider
        except HTTPError as error:
            failures.append(error.code)
            if error.code in (403, 429):
                PROVIDER_COOLDOWNS[provider] = (now + (300 if error.code == 403 else 60), error.code)
            LOGGER.warning("LLM provider unavailable: %s (HTTP %s)", provider, error.code)
        except Exception as error:
            status = provider_status(error)
            failures.append(status)
            if status in (403, 429):
                PROVIDER_COOLDOWNS[provider] = (now + (300 if status == 403 else 60), status)
            LOGGER.warning("LLM provider unavailable: %s (%s)", provider, type(error).__name__)
    return "", unavailable_mode(failures) if providers else "unavailable"


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("NVIDIA_API_KEY") or os.getenv("OPENROUTER_API_KEY"))}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    allow_request(request)
    retrieval_query = " ".join([turn.message for turn in payload.history if turn.role == "user"][-1:] + [payload.message])
    matches = retrieve_relevant(retrieval_query)
    if not matches:
        return ChatResponse(answer=no_match_answer(), sources=[], mode="not-found", contact_admin=True)
    answer, mode = generate_answer(payload.message, context_from(matches), payload.history)
    return ChatResponse(
        answer=answer or unavailable_answer(mode),
        sources=[Source(title=item["title"], source=item["source"]) for item in matches],
        mode=mode,
        contact_admin=not bool(answer),
    )
