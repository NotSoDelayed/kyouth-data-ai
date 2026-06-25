FROM python:3.14.4-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync

COPY src ./src

CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
