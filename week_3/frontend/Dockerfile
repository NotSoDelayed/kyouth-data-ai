FROM python:3.14.4-bookworm

WORKDIR /app

COPY src ./src
COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
