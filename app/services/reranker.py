"""Переранжирование кандидатов cross-encoder'ом (этап 4, задание 2.7).

Второй, точный этап отбора в схеме two-stage retrieval:
``retrieve (дёшево) top-50 → rerank (дорого, но точно) top-5``.

Bi-encoder (Embedder) кодирует запрос и документ по отдельности в векторы —
быстро, можно искать по всей базе, но грубо. Cross-encoder берёт пару
(запрос, документ) вместе и выдаёт точный скор релевантности — гораздо точнее,
но медленно (нужен прогон модели на каждую пару), поэтому применяется только к
небольшому числу кандидатов после первичного поиска, а не ко всей базе.
"""
from operator import itemgetter
from sentence_transformers import CrossEncoder

from app.services.vector_store import SearchResult


class Reranker:
    """Переупорядочивает кандидатов по релевантности через cross-encoder."""

    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Args:
            model_name: id cross-encoder модели на HuggingFace. ms-marco-MiniLM
                обучена на английском; для русского берут мультиязычную
                (например BAAI/bge-reranker-v2-m3, но она тяжёлая).
        """
        self.model = CrossEncoder(model_name)   # тяжёлое — грузим один раз

    def rerank(self, query: str, candidates: list[SearchResult], top_k: int) -> list[SearchResult]:
        """Переранжирует кандидатов первичного поиска и возвращает top_k.

        Каждый кандидат оценивается парой (query, текст чанка); порядок задаётся
        cross-encoder-скором, chunk и methods исходных результатов сохраняются.

        Args:
            query: текст запроса.
            candidates: результаты первичного поиска (например, из HybridRetriever).
            top_k: сколько лучших вернуть после переранжирования.

        Returns:
            Список SearchResult по убыванию cross-encoder-скора (score заменён на
            него); пустой вход -> пустой список.
        """
        if not candidates:
            return []

        pairs = [[query, candidate.chunk.text] for candidate in candidates]
        scores = self.model.predict(pairs)  # numpy-массив, по скору на пару

        # 1. спарить каждого кандидата с его новым cross-encoder-скором
        scored_candidates = zip(candidates, scores)

        # 2. отсортировать по убыванию скора и взять top_k
        ranked = sorted(scored_candidates, key=itemgetter(1), reverse=True)[:top_k]

        # 3. собрать результаты, подставив свежий скор (chunk и methods сохраняем)
        return [
            SearchResult(chunk=candidate.chunk, score=float(score), methods=candidate.methods)
            for candidate, score in ranked
        ]
