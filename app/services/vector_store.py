import numpy as np
from dataclasses import dataclass

from app.services.chunker import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float

class InMemoryVectorStore:
    def __init__(self):
        self._chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None   # (N, dim)

    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Количество чанков не соответствует количеству векторов.")

        self._chunks.extend(chunks)
        if self._matrix is None:
            self._matrix = embeddings
        else:
            self._matrix = np.vstack([self._matrix, embeddings])

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[SearchResult]:
        if self._matrix is None:
            return []
        scores = self._matrix @ query_embedding
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(scores[i])) for i in top_idx]