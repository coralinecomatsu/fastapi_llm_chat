"""Гибридный поиск с RRF (этап 4, задание 2.6).

Объединяет dense-поиск (``InMemoryVectorStore``, смысл) и лексический
(``BM25Store``, точные слова) — лучшее из двух миров. Результаты сливаются через
Reciprocal Rank Fusion: складываем не «сырые» скоры (у dense и BM25 они в разных
шкалах), а вклады по позициям — score(d) = Σ 1 / (k + rank_i(d)) по каждому
поисковику, где документ встретился. Документ, найденный обоими методами,
получает сумму вкладов и всплывает наверх.
"""
from collections import defaultdict

from app.services.chunker import Chunk
from app.services.vector_store import SearchResult, InMemoryVectorStore
from app.services.bm25_store import BM25Store
from app.services.embedder import Embedder


class HybridRetriever:
    """Оборачивает векторный и BM25 сторы, сливает их выдачи через RRF."""

    def __init__(self,
                 vector_store: InMemoryVectorStore,
                 bm25_store: BM25Store,
                 embedder: Embedder,
                 k: int = 60,):
        """Args:
            vector_store: хранилище для dense-поиска.
            bm25_store: хранилище для лексического поиска.
            embedder: кодировщик запроса в вектор (та же модель, что при индексации).
            k: константа RRF; больше k — позиции в топе ближе по весу (обычно 60).

        Raises:
            ValueError: если какая-то из зависимостей не передана.
        """
        if vector_store is None or bm25_store is None or embedder is None:
            raise ValueError("vector_store, bm25_store и embedder обязательны")
        self._vector_store = vector_store
        self._bm25 = bm25_store
        self._embedder = embedder
        self._k = k

    def _fuse(
            self,
            results: list[SearchResult],
            method_name: str,
            rrf: dict[int, float],
            methods: dict[int, set[str]],
            chunk_by_id: dict[int, Chunk],
    ) -> None:
        """Добавляет RRF-вклад одного списка результатов в общие накопители.

        Словари изменяются на месте (передаются по ссылке), поэтому оба вызова
        _fuse пишут в одни и те же rrf/methods/chunk_by_id — накопление идёт само.

        Args:
            results: выдача одного поисковика (уже отсортирована по релевантности).
            method_name: метка источника ("dense" или "bm25").
            rrf: накопитель RRF-скоров по ключу id(chunk).
            methods: накопитель множеств меток-источников по тому же ключу.
            chunk_by_id: карта id(chunk) -> сам чанк, чтобы достать его в конце.
        """
        for rank, result in enumerate(results, start=1):
            key = id(result.chunk)
            rrf[key] += 1 / (self._k + rank)
            methods[key].add(method_name)
            chunk_by_id[key] = result.chunk

    def search(self, query: str, top_k: int) -> list[SearchResult]:
        """Запускает оба поиска и сливает их через RRF.

        Из каждого поисковика берём пул кандидатов больше top_k, чтобы документ,
        стоящий у одного метода чуть ниже, не потерялся до слияния.

        Args:
            query: текст запроса.
            top_k: сколько результатов вернуть после слияния.

        Returns:
            Результаты по убыванию RRF-скора; в поле ``methods`` — каким методом
            (методами) найден каждый чанк.
        """
        pool = top_k * 3
        dense_results = self._vector_store.search(self._embedder.embed_query(query), pool)
        bm25_results = self._bm25.search(query, pool)
        rrf = defaultdict(float)
        methods = defaultdict(set)
        chunk_by_id = {}
        self._fuse(dense_results, "dense", rrf, methods, chunk_by_id)
        self._fuse(bm25_results, "bm25", rrf, methods, chunk_by_id)

        sorted_keys = sorted(rrf, key=lambda key: rrf[key], reverse=True)[:top_k]
        return [
            SearchResult(
                chunk=chunk_by_id[key],
                score=rrf[key],
                methods=methods[key],
            )
            for key in sorted_keys
        ]
