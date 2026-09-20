from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name="multilingual-e5-small", batch_size=32):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)  # тяжёлое — грузим один раз
        self.batch_size = batch_size

    def _with_prefix(self, text: str, prefix: str) -> str:
        if "e5" in self.model_name.lower():
            return prefix + ": " + text
        return text

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            raise ValueError("Texts is required!")
        prepared_texts = [self._with_prefix(text.strip(), "passage") for text in texts]
        embeddings = self.model.encode(prepared_texts,
                                       batch_size=self.batch_size,
                                       normalize_embeddings=True,
                                       convert_to_numpy=True)
        return embeddings

    def embed_query(self, text: str) -> np.ndarray:
        if not text:
            raise ValueError("text is required!")
        prepared_text = self._with_prefix(text.strip(), "query")
        embeddings = self.model.encode(prepared_text, normalize_embeddings=True, convert_to_numpy=True)
        return embeddings