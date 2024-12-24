FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /api

COPY . .

RUN uv sync --frozen --no-cache

CMD ["/api/.venv/bin/fastapi", "run", "/api/main.py"]
