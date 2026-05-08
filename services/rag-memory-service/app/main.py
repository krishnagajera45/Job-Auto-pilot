from __future__ import annotations

import uuid
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Autopilot RAG & Memory Service", version="0.1.0")


class MemoryIndexRequest(BaseModel):
    user_id: str
    source: str
    content: str


class MemoryQueryRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = 5


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "rag-memory-service"}


@app.post("/v1/memory/index")
async def index_memory(request: MemoryIndexRequest) -> dict:
    memory_id = str(uuid.uuid4())
    return {"memory_id": memory_id, "status": "indexed", "source": request.source}


@app.post("/v1/memory/query")
async def query_memory(request: MemoryQueryRequest) -> dict:
    return {
        "query": request.query,
        "results": [
            {"chunk": "Experience in FastAPI and LLM tooling", "score": 0.92},
            {"chunk": "Built automation for ATS workflows", "score": 0.87},
        ],
    }


@app.get("/v1/memory/sources")
async def list_sources(user_id: str) -> dict:
    return {"user_id": user_id, "sources": ["resume", "portfolio", "notes"]}
