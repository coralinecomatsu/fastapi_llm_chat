"""Лексическое (BM25) хранилище (этап 4, задание 2.5).

BM25 ранжирует чанки по словам запроса: учитывает частоту слова в документе
(с насыщением), редкость слова (IDF) и длину документа. В отличие от dense,
отлично ловит точные термины — коды ошибок, артикулы, редкие слова, — где
семантический поиск «размазывает» и промахивается.

Интерфейс намеренно симметричен ``InMemoryVectorStore``, только работает с сырым
текстом: ``add`` принимает чанки (без векторов), ``search`` — строку запроса.
"""
import re
import numpy as np

from rank_bm25 import BM25Okapi

from app.services.chunker import Chunk
from app.services.vector_store import SearchResult


class BM25Store:
    """BM25-поиск поверх rank-bm25. Индекс перестраивается при каждом add."""

    def __init__(self):
        self._bm25 = None
        self._chunks = []

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Приводит текст к списку слов: нижний регистр, без пунктуации.

        Одна и та же токенизация применяется к документам и к запросу — иначе
        слова не совпадут.
        """
        clean_text = re.sub(r'[^\w\s]', '', text)
        text_by_whitespace = clean_text.lower().split()
        return text_by_whitespace

    def add(self, chunks: list[Chunk]) -> None:
        """Добавляет чанки и перестраивает BM25-индекс по всему корпусу.

        BM25Okapi не умеет дописывать инкрементально, поэтому индекс каждый раз
        строится заново по всем накопленным чанкам.

        Args:
            chunks: список чанков для индексации.
        """
        self._chunks.extend(chunks)
        self._bm25 = BM25Okapi([self._tokenize(c.text) for c in self._chunks])

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        """Ищет top_k чанков с наибольшим BM25-скором.

        Args:
            query: текст запроса.
            top_k: сколько результатов вернуть.

        Returns:
            Результаты по убыванию BM25-скора; пустое хранилище -> пустой список.
        """
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(self._tokenize(query))
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(scores[i])) for i in top_idx]
