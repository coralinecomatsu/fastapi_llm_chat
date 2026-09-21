"""Векторное хранилище в памяти (этап 4, задание 2.4).

Хранит эмбеддинги чанков в одной numpy-матрице и ищет ближайшие по смыслу
(dense-поиск). Поиск — одно матричное умножение ``matrix @ query`` вместо цикла:
так BLAS считает похожесть со всеми векторами разом. Векторы приходят уже
нормализованными (см. ``Embedder``), поэтому скалярное произведение = cosine.
"""
import numpy as np
from dataclasses import dataclass, field

from app.services.chunker import Chunk


@dataclass
class SearchResult:
    """Результат поиска: найденный чанк и его релевантность.

    Атрибуты:
        chunk: найденный кусок документа.
        score: оценка релевантности (для dense — cosine, для гибрида — RRF-скор).
        methods: какими методами найден ({"dense"}, {"bm25"} или оба); для
            обычного поиска пусто, заполняется гибридом.
    """
    chunk: Chunk
    score: float
    methods: set[str] = field(default_factory=set)


class InMemoryVectorStore:
    """Наивное векторное хранилище: список чанков + параллельная матрица векторов."""

    def __init__(self):
        self._chunks: list[Chunk] = []
        self._matrix: np.ndarray | None = None   # (N, dim)

    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Добавляет чанки вместе с их векторами.

        Чанк и его вектор выравниваются по позиции: i-й чанк <-> i-я строка
        матрицы. Новые векторы приклеиваются снизу через ``vstack``.

        Args:
            chunks: список чанков.
            embeddings: матрица (len(chunks), dim) — по вектору на чанк.

        Raises:
            ValueError: если число чанков не совпадает с числом векторов.
        """
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("Количество чанков не соответствует количеству векторов.")

        self._chunks.extend(chunks)
        if self._matrix is None:
            self._matrix = embeddings
        else:
            self._matrix = np.vstack([self._matrix, embeddings])

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[SearchResult]:
        """Ищет top_k ближайших чанков по cosine-похожести.

        Args:
            query_embedding: нормализованный вектор запроса формы (dim,).
            top_k: сколько результатов вернуть.

        Returns:
            Результаты по убыванию похожести; пустое хранилище -> пустой список.
        """
        if self._matrix is None:
            return []
        scores = self._matrix @ query_embedding
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(scores[i])) for i in top_idx]
