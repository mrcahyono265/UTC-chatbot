# UTC RAG Portfolio

Web portfolio Retrieval-Augmented Generation (RAG) untuk UNIDA Technology Care (UTC).

## Features

- Landing page responsive dengan chatbot UTC yang dapat dibuka dari tombol mengambang.
- FastAPI chat endpoint.
- Ekstraksi Master PDF, chunking berbasis Bab/Subbab, dan embedding multilingual menggunakan Sentence Transformers.
- Semantic retrieval dengan metadata Bab, Subbab, dan halaman sumber.
- Provider chain: NVIDIA Build, Gemini 3.6 Flash, lalu OpenRouter Free Router.
- Fallback retrieval ketika semua provider tidak tersedia.
- Riwayat percakapan sementara: empat pesan terakhir hanya disimpan di memori halaman dan hilang saat halaman dimuat ulang.

## Tech Stack

- Python, FastAPI, Uvicorn
- Sentence Transformers
- Gemini Developer API
- pypdf, ReportLab
- HTML, CSS, JavaScript
- Docker Compose

## Project Structure

```text
app/                     FastAPI application and retrieval logic
data/UTC-Master-Knowledge-Base.pdf Curated public knowledge source
scripts/build_master_pdf.py PDF generation script
static/                  Frontend files
server.py                Local and container entry point
Dockerfile               Container image definition
docker-compose.yml       Container orchestration
```

## Requirements

- Python 3.11+
- Docker and Docker Compose (only for container deployment)
- Gemini API key (optional for local retrieval demo)

## Local Development

Install project dependencies:

```powershell
uv sync
Copy-Item .env.example .env
```

Set one or more provider API keys in `.env`. The default NVIDIA Build model is `openai/gpt-oss-120b`, Gemini is `gemini-3.6-flash`, and OpenRouter uses the free instruction model `google/gemma-4-26b-a4b-it:free`. `MAX_OUTPUT_TOKENS` defaults to `256` and `LLM_TIMEOUT_SECONDS` to `45`. Do not put secrets in `.env.example`.

Start the application:

```powershell
uv run server.py
```

Open `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

## Docker

The UTC container joins the existing external Docker network named `proxy`. Ensure the global Nginx container is also connected to that network:

```bash
docker network inspect proxy
```

Create `.env` from the example and add your provider API keys. Deploy the container:

```bash
docker compose up -d --build
```

Copy `nginx/example.com.conf` to `~/infra/reverse-proxy/conf.d/example.com.conf` on EC2, then reload the existing Nginx container:

```bash
docker exec global-nginx nginx -s reload
```

Open `http://example.com`. Replace `example.com` in the Nginx config and `.env` when the real domain is available. HTTPS remains managed by the existing global Nginx setup.

Stop the containers:

```bash
docker compose down
```

## API

### `POST /api/chat`

```json
{ "message": "Apakah UTC menerima servis printer?" }
```

The response contains the answer, retrieved source titles, and the active mode: `gemini` or `retrieval-demo`.

## Knowledge Base

`data/UTC-Master-Knowledge-Base.pdf` is the only runtime knowledge source. The application extracts pages, splits content by Bab/Subbab into chunks, embeds those chunks, and retrieves the most relevant chunks for Gemini.

To update the public content, edit `scripts/build_master_pdf.py` and regenerate the PDF:

```powershell
uv run python scripts/build_master_pdf.py
```

Do not include staff schedules, personal data, financial records, or internal operational details. Customer-facing operating information must be confirmed with UTC before publication.

Verify the PDF retrieval after changing the source:

```powershell
uv run python scripts/check_rag.py
```
