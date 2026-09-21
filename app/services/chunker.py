"""Нарезка документов на чанки (этап 4, задание 2.1).

Перед индексацией длинный текст режется на небольшие куски (чанки): так поиск
точнее, а в контекст модели попадает только релевантное. Размер считаем
**в токенах** (а не символах), потому что модель мыслит токенами — для этого
используем токенизатор tiktoken.

Две стратегии:
- ``chunk_text`` — фиксированный размер с перекрытием (overlap);
- ``chunk_by_paragraphs`` — по абзацам, с дорезкой слишком больших.
"""
import tiktoken
from dataclasses import dataclass


@dataclass
class Chunk:
    """Один кусок документа плюс его позиция в исходном тексте.

    Атрибуты:
        text: сам текст чанка.
        index: порядковый номер чанка в выдаче (0, 1, 2, ...).
        start_token: позиция первого токена чанка в потоке токенов документа.
        end_token: позиция за последним токеном (start_token + длина в токенах).
    """
    text: str
    index: int
    start_token: int
    end_token: int


class Chunker:
    """Режет текст на чанки. Токенизатор создаётся один раз и переиспользуется."""

    def __init__(self, encoding_name="cl100k_base"):
        """Args:
            encoding_name: имя кодировки tiktoken (cl100k_base — та же, что у
                современных OpenAI-моделей; годится как универсальный счётчик токенов).
        """
        self._tokenizer = tiktoken.get_encoding(encoding_name)

    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[Chunk]:
        """Режет текст на чанки фиксированного размера с перекрытием.

        Скользящее окно по токенам: каждое окно шириной ``chunk_size`` токенов,
        шаг вперёд ``chunk_size - overlap``. За счёт шага последние ``overlap``
        токенов чанка i совпадают с первыми ``overlap`` токенами чанка i+1 —
        это спасает факты, оказавшиеся на границе.

        Args:
            text: исходный текст.
            chunk_size: максимальный размер чанка в токенах.
            overlap: сколько токенов соседние чанки делят между собой.

        Returns:
            Список чанков по порядку. Пустой текст -> пустой список.

        Raises:
            ValueError: если overlap >= chunk_size (окно не сдвигалось бы вперёд).
        """
        if overlap >= chunk_size:
            raise ValueError("Atatata overlap >= chunk_size!")

        tokens = self._tokenizer.encode(text)
        tokens_size = len(tokens)
        results = []
        start = 0
        index = 0
        while start < tokens_size:
            end = min(start + chunk_size, tokens_size)
            current_chunk = tokens[start:end]
            decoded_str = self._tokenizer.decode(current_chunk)
            results.append(Chunk(
                text=decoded_str,
                index=index,
                start_token=start,
                end_token=end,
            ))
            start += chunk_size - overlap
            index += 1
            if end == tokens_size:
                break

        return results

    def chunk_by_paragraphs(self, text: str, max_tokens: int) -> list[Chunk]:
        """Режет текст по абзацам, уважая их границы.

        Копит целые абзацы (разделитель ``\\n\\n``) в буфер, пока их суммарный
        размер не превышает ``max_tokens``; при превышении — закрывает буфер в
        чанк и начинает новый. Абзац, который сам больше лимита, дорезается
        через ``chunk_text``.

        Args:
            text: исходный текст.
            max_tokens: максимальный размер чанка в токенах.

        Returns:
            Список чанков по порядку; позиции стыкуются встык (перекрытия нет).
        """
        def close_buf_to_chunk(buffer: list, running: int, index: int):
            """Склеивает накопленные абзацы в один Chunk и двигает курсор running.

            Returns:
                (chunk, running) — готовый чанк и позиция за его концом.
            """
            chunk_text = const_end_paragraph.join(buffer)
            chunk_token_len = len(self._tokenizer.encode(chunk_text))
            start_token = running
            end_token = running + chunk_token_len
            running = end_token  # следующий чанк стартует отсюда
            chunk = Chunk(
                text=chunk_text,
                index=index,
                start_token=start_token,
                end_token=end_token,
            )
            return chunk, running
        const_end_paragraph = "\n\n"
        paragraphs = text.split(const_end_paragraph)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        buffer = []
        buffer_tokens = 0
        results = []
        index = 0
        running = 0
        for paragraph in paragraphs:
            paragraph_tokens = len(self._tokenizer.encode(paragraph))
            if paragraph_tokens > max_tokens:
                if buffer:
                    chunk, running = close_buf_to_chunk(buffer, running, index)
                    results.append(chunk)
                    index += 1
                    buffer = []
                    buffer_tokens = 0
                base = running
                for sub in self.chunk_text(paragraph, max_tokens, 0):
                    sub.index = index
                    sub.start_token += base
                    sub.end_token += base
                    results.append(sub)
                    index += 1
                running += paragraph_tokens
                continue

            if buffer_tokens + paragraph_tokens > max_tokens and buffer:
                chunk, running = close_buf_to_chunk(buffer, running, index)
                results.append(chunk)
                index += 1
                buffer = [paragraph]  # ← начать новый буфер С НЕГО
                buffer_tokens = paragraph_tokens
            else:
                buffer.append(paragraph)
                buffer_tokens += paragraph_tokens

        if buffer:
            chunk, running = close_buf_to_chunk(buffer, running, index)
            results.append(chunk)
        return results
