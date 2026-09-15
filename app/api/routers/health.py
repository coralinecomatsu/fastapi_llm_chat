"""Health-роутер — самый первый живой эндпоинт ([F] 1.1)."""
from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/echo/{text}")
async def echo(text: str) -> dict[str, str]:
    # [F] 1.1 — вернуть текст в верхнем регистре
    return {"text": text.upper()}
