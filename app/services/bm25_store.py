import re
import numpy as np

from rank_bm25 import BM25Okapi

from app.services.chunker import Chunk
from app.services.vector_store import SearchResult


class BM25Store:
    def __init__(self):
        self._bm25 = None
        self._chunks = []

    @staticmethod
    def _tokenize(text) -> list[str]:
        clean_text = re.sub(r'[^\w\s]', '', text)
        text_by_whitespace = clean_text.lower().split()
        return text_by_whitespace

    def add(self, chunks: list[Chunk]) -> None:
        self._chunks.extend(chunks)
        self._bm25 = BM25Okapi([self._tokenize(c.text) for c in self._chunks])

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(self._tokenize(query))
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(scores[i])) for i in top_idx]