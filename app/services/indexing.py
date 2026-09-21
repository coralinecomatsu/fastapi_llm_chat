"""Разбиение документа на чанки с сохранением метаданных"""
from app.services.chunker import Chunker, Chunk
from app.services.loader import Document


def chunk_documents(documents: list[Document], chunker: Chunker, max_tokens: int) -> list[Chunk]:
    """Разбиение документа на чанки с сохранением метаданных"""
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_by_paragraphs(doc.text, max_tokens)
        for chunk in chunks:
            chunk.metadata = dict(doc.metadata)
        all_chunks.extend(chunks)
    return all_chunks