FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY data/UTC-Master-Knowledge-Base.pdf ./data/UTC-Master-Knowledge-Base.pdf
COPY static ./static
COPY server.py .

EXPOSE 8000

CMD [".venv/bin/python", "server.py"]
