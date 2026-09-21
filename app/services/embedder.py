"""Эмбеддинги: текст -> вектор (этап 4, задание 2.3).

Эмбеддинг — вектор фиксированной длины, где семантически близкие тексты дают
близкие векторы. На нём строится dense-поиск (см. ``vector_store``).

Важные детали:
- одна и та же модель для индексации и запроса (векторы разных моделей
  несопоставимы);
- модели семейства e5 требуют префиксов ``passage:`` / ``query:``;
- векторы нормализуем, чтобы cosine превратился в простое скалярное произведение.
"""
from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    """Обёртка над sentence-transformers. Модель грузится один раз в __init__."""

    def __init__(self, model_name: str = "intfloat/multilingual-e5-small", batch_size: int = 32):
        """Args:
            model_name: id модели на HuggingFace (по умолчанию мультиязычная
                e5-small, понимает русский).
            batch_size: размер пачки при кодировании документов.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)  # тяжёлое — грузим один раз
        self.batch_size = batch_size

    def _with_prefix(self, text: str, prefix: str) -> str:
        """Добавляет префикс (``passage``/``query``) только для e5-моделей.

        Для не-e5 моделей (например MiniLM) возвращает текст как есть.
        """
        if "e5" in self.model_name.lower():
            return prefix + ": " + text
        return text

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Кодирует список документов в матрицу нормализованных векторов.

        Args:
            texts: тексты чанков для индексации.

        Returns:
            Массив формы (N, dim) — по строке-вектору на каждый текст.

        Raises:
            ValueError: если список пустой.
        """
        if not texts:
            raise ValueError("Texts is required!")
        prepared_texts = [self._with_prefix(text.strip(), "passage") for text in texts]
        embeddings = self.model.encode(prepared_texts,
                                       batch_size=self.batch_size,
                                       normalize_embeddings=True,
                                       convert_to_numpy=True)
        return embeddings

    def embed_query(self, text: str) -> np.ndarray:
        """Кодирует один запрос в нормализованный вектор.

        Args:
            text: текст запроса.

        Returns:
            Одномерный вектор формы (dim,) — годится для ``matrix @ query``.

        Raises:
            ValueError: если текст пустой.
        """
        if not text:
            raise ValueError("text is required!")
        prepared_text = self._with_prefix(text.strip(), "query")
        embeddings = self.model.encode(prepared_text, normalize_embeddings=True, convert_to_numpy=True)
        return embeddings
