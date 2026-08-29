import os
import re
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

KNOWLEDGE_BASE = Path(__file__).resolve().parents[1] / "data" / "UTC-Master-Knowledge-Base.pdf"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
CHUNK_SIZE = 140
CHUNK_OVERLAP = 25
CHAPTER_PATTERN = re.compile(r"^BAB\s+\d+\.\s+(.+)$", re.IGNORECASE)
SECTION_PATTERN = re.compile(r"^\d+\.\d+\s+(.+)$")
QUERY_ALIASES = {"hp": "handphone", "pc": "komputer", "benerin": "perbaikan", "benarin": "perbaikan", "servis": "service", "harga": "biaya", "tarif": "biaya", "nggak": "tidak", "nggk": "tidak", "gak": "tidak"}
STOP_WORDS = {"ada", "apakah", "bisa", "dan", "dengan", "ini", "itu", "kalau", "saya", "tidak", "untuk", "yang"}


def chunk_text(text: str) -> list[str]:
    words = text.split()
    if len(words) <= CHUNK_SIZE:
        return [text]
    return [" ".join(words[start : start + CHUNK_SIZE]) for start in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP)]


def extract_chunks() -> list[dict]:
    if not KNOWLEDGE_BASE.exists():
        raise FileNotFoundError(f"Knowledge base PDF not found: {KNOWLEDGE_BASE}")

    documents = []
    chapter = "Informasi UTC"
    section = "Informasi umum"
    page_number = 1
    lines = []

    def save_section():
        text = " ".join(lines).strip()
        if not text:
            return
        for index, chunk in enumerate(chunk_text(text), start=1):
            title = f"{chapter} - {section}"
            documents.append({"id": f"page-{page_number}-{len(documents) + 1}", "title": title, "source": f"UTC Master Knowledge Base, halaman {page_number}", "text": chunk, "chunk": index})

    for current_page, page in enumerate(PdfReader(str(KNOWLEDGE_BASE)).pages, start=1):
        for raw_line in (page.extract_text() or "").splitlines():
            line = " ".join(raw_line.split())
            if not line or line.startswith("UTC Master Knowledge Base | Halaman"):
                continue
            chapter_match = CHAPTER_PATTERN.match(line)
            section_match = SECTION_PATTERN.match(line)
            if chapter_match or section_match:
                save_section()
                lines.clear()
                page_number = current_page
                if chapter_match:
                    chapter = line
                    section = "Informasi umum"
                else:
                    section = line
                continue
            lines.append(line)
    save_section()
    return documents


@lru_cache
def load_retriever():
    documents = extract_chunks()
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode([f"{item['title']}\n{item['text']}" for item in documents], normalize_embeddings=True)
    return model, documents, embeddings


def normalize_query(question: str) -> str:
    return " ".join(QUERY_ALIASES.get(word) or word for word in re.findall(r"[\w]+", question.lower()))


def keywords(text: str) -> set[str]:
    return {word for word in re.findall(r"[\w]+", text.lower()) if word not in STOP_WORDS}


def retrieve(question: str, limit: int = 3) -> list[dict]:
    model, documents, embeddings = load_retriever()
    normalized_question = normalize_query(question)
    query_embedding = model.encode(normalized_question, normalize_embeddings=True)
    semantic_scores = embeddings @ query_embedding
    query_keywords = keywords(normalized_question)
    ranked = []
    for index, semantic_score in enumerate(semantic_scores):
        lexical_score = len(query_keywords & keywords(f"{documents[index]['title']} {documents[index]['text']}")) / max(len(query_keywords), 1)
        ranked.append((index, float(semantic_score), lexical_score))
    ranked.sort(key=lambda item: item[1] + 0.35 * item[2], reverse=True)
    return [{**documents[index], "semantic_score": round(semantic_score, 3), "lexical_score": round(lexical_score, 3), "score": round(semantic_score + 0.35 * lexical_score, 3)} for index, semantic_score, lexical_score in ranked[:limit]]


def similarity_threshold() -> float:
    value = os.getenv("SIMILARITY_THRESHOLD")
    if value is None:
        raise RuntimeError("SIMILARITY_THRESHOLD must be set from RAG calibration")
    try:
        threshold = float(value)
    except ValueError as error:
        raise RuntimeError("SIMILARITY_THRESHOLD must be a number") from error
    if threshold <= 0:
        raise RuntimeError("SIMILARITY_THRESHOLD must be greater than zero")
    return threshold


def retrieve_relevant(question: str, limit: int = 2) -> list[dict]:
    threshold = similarity_threshold()
    return [match for match in retrieve(question, limit=limit) if match["score"] >= threshold]


def context_from(matches: list[dict]) -> str:
    return "\n\n".join(f"[{item['title']}]\n{item['text']}" for item in matches)
