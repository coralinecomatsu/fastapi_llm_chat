from fastapi import Request, Query
from dataclasses import dataclass

from app.services.llm_client import LLMClient

def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client

@dataclass
class Pagination:
    limit: int
    offset: int

def pagination(limit: int = Query(20, le=100), offset: int = Query(0, ge=0)) -> Pagination:
    return Pagination(limit=limit, offset=offset)