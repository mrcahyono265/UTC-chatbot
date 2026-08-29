# UTC RAG Portfolio

Static landing page and RAG portfolio for UNIDA Technology Care (UTC).

- Frontend: HTML, CSS, and vanilla JavaScript. Backend: FastAPI and Sentence Transformers.
- Runtime knowledge source: `data/UTC-Master-Knowledge-Base.pdf`. Update its public content in `scripts/build_master_pdf.py`, then regenerate the PDF.
- Retrieval: heading-aware chunks, multilingual embeddings, hybrid semantic/lexical ranking, and `SIMILARITY_THRESHOLD` from `.env` after notebook calibration. Below threshold, do not call an LLM; direct the customer to admin.
- Provider chain: NVIDIA Build primary, then Gemini, then OpenRouter. Keep provider keys in `.env` only.
- Chat history is browser-memory only and limited to four messages. Model output defaults to 256 tokens.
- Evaluation: run `notebooks/rag_evaluation.ipynb`; set its selected threshold in `.env`. Smoke test: `uv run python scripts/check_rag.py`.
- Deployment: `docker-compose.yml` connects `utc-app` to external Docker network `proxy`. The separate `global-nginx` container proxies to `utc-app:8000`; template: `nginx/example.com.conf`.
- Do not put staff schedules, personal data, financial records, or internal operational details into the public Master PDF.
