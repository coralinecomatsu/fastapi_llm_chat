import tiktoken
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int
    start_token: int
    end_token: int


class Chunker:
    def __init__(self, encoding_name="cl100k_base"):
        self._tokenizer = tiktoken.get_encoding(encoding_name)

    def chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[Chunk]:
        """функция режет текст по размеру с перекрытием"""
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
        def close_buf_to_chunk(buffer: list, running:int, index: int):
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