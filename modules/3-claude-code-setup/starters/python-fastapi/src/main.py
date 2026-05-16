"""FastAPI Hello World для Module 3 starter.

Запуск локально:
    uvicorn src.main:app --reload --port ${PORT:-8000}
"""

import os
import time

from fastapi import FastAPI

app = FastAPI(title="agentic-engineering-course python-fastapi starter")

_start_time = time.monotonic()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello from agentic-engineering-course python-fastapi starter"}


@app.get("/health")
def health() -> dict[str, float | str]:
    return {"status": "ok", "uptime": time.monotonic() - _start_time}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
