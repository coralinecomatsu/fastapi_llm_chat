"""Кастомные исключения для моего проектика"""

class RAGChatError(Exception):
    """Базовое исключение приложения."""


class LLMError(RAGChatError):
    """Ошибка при обращении к LLM."""


class ChunkingError(RAGChatError):
    """Проблемы нарезки документов."""


class EmbeddingError(RAGChatError):
    """Проблемы эмбеддингов."""