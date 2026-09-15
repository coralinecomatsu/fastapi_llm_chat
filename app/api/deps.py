from fastapi import Request
from app.services.llm_client import LLMClient

def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client