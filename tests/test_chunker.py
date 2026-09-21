"""Тесты чанкера (задание 2.1): chunk_text и chunk_by_paragraphs.

Проверяем инварианты, а не конкретные строки (текст зависит от токенизатора):
- ни один чанк не длиннее лимита по токенам;
- overlap реально работает (совпадение токенов на стыке);
- позиции/индексы монотонны и стыкуются;
- граничные случаи (пустой текст, текст короче чанка).
"""
import pytest

from app.services.chunker import Chunk, Chunker


@pytest.fixture(scope="module")
def chunker() -> Chunker:
    # токенизатор тяжёлый — создаём один раз на модуль
    return Chunker()


def n_tokens(chunker: Chunker, text: str) -> int:
    return len(chunker._tokenizer.encode(text))


# --------------------------- chunk_text ---------------------------

def test_chunk_text_respects_size(chunker: Chunker) -> None:
    text = "слово " * 200
    chunks = chunker.chunk_text(text, chunk_size=30, overlap=5)
    assert chunks, "должен вернуть хотя бы один чанк"
    for c in chunks:
        assert n_tokens(chunker, c.text) <= 30


def test_chunk_text_overlap_is_real(chunker: Chunker) -> None:
    # последние `overlap` токенов чанка i == первые `overlap` токенов чанка i+1
    text = "один два три четыре пять шесть семь восемь девять десять " * 4
    chunk_size, overlap = 20, 5
    chunks = chunker.chunk_text(text, chunk_size, overlap)
    assert len(chunks) >= 2, "нужен текст, дающий несколько чанков"
    for a, b in zip(chunks, chunks[1:]):
        tail = chunker._tokenizer.encode(a.text)[-overlap:]
        head = chunker._tokenizer.encode(b.text)[:overlap]
        assert tail == head


def test_chunk_text_index_and_positions_are_monotonic(chunker: Chunker) -> None:
    text = "слово " * 100
    chunks = chunker.chunk_text(text, chunk_size=25, overlap=5)
    # index идёт по порядку 0,1,2,...
    assert [c.index for c in chunks] == list(range(len(chunks)))
    # start_token двигается вперёд шагом (chunk_size - overlap)
    for a, b in zip(chunks, chunks[1:]):
        assert b.start_token - a.start_token == 25 - 5


def test_chunk_text_no_trailing_sliver(chunker: Chunker) -> None:
    # break при end == len(tokens): последний чанк не должен быть огрызком из overlap
    text = "слово " * 100
    chunk_size, overlap = 20, 5
    chunks = chunker.chunk_text(text, chunk_size, overlap)
    # ни один чанк не короче или равен overlap (кроме единственного случая всего одного чанка)
    if len(chunks) > 1:
        assert all(c.end_token - c.start_token > overlap for c in chunks)


def test_chunk_text_empty(chunker: Chunker) -> None:
    assert chunker.chunk_text("", chunk_size=20, overlap=5) == []


def test_chunk_text_shorter_than_chunk(chunker: Chunker) -> None:
    chunks = chunker.chunk_text("привет мир", chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].start_token == 0


def test_chunk_text_overlap_ge_size_raises(chunker: Chunker) -> None:
    with pytest.raises(ValueError):
        chunker.chunk_text("любой текст", chunk_size=10, overlap=10)
    with pytest.raises(ValueError):
        chunker.chunk_text("любой текст", chunk_size=10, overlap=15)


# ----------------------- chunk_by_paragraphs -----------------------

def _paragraphs_text() -> str:
    return (
        "Первый маленький абзац.\n\n"
        "Второй абзац, средний по размеру, с парой деталей внутри.\n\n"
        "Третий.\n\n"
        "Четвёртый абзац, тоже небольшой."
    )


def test_by_paragraphs_respects_max_tokens(chunker: Chunker) -> None:
    chunks = chunker.chunk_by_paragraphs(_paragraphs_text(), max_tokens=15)
    assert chunks
    for c in chunks:
        assert n_tokens(chunker, c.text) <= 15


def test_by_paragraphs_positions_stitch(chunker: Chunker) -> None:
    # чанки не перекрываются: конец одного = начало следующего
    chunks = chunker.chunk_by_paragraphs(_paragraphs_text(), max_tokens=15)
    for a, b in zip(chunks, chunks[1:]):
        assert a.end_token == b.start_token
    assert chunks[0].start_token == 0


def test_by_paragraphs_index_is_sequential(chunker: Chunker) -> None:
    chunks = chunker.chunk_by_paragraphs(_paragraphs_text(), max_tokens=15)
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_by_paragraphs_splits_oversized_paragraph(chunker: Chunker) -> None:
    # один абзац заведомо больше лимита -> должен разрезаться на несколько чанков
    big = "очень длинное предложение с большим количеством слов " * 10
    text = f"Короткий.\n\n{big}\n\nЕщё короткий."
    chunks = chunker.chunk_by_paragraphs(text, max_tokens=12)
    assert len(chunks) > 3  # короткие + несколько под-чанков большого
    for c in chunks:
        assert n_tokens(chunker, c.text) <= 12
    # индексы всё равно непрерывны, несмотря на под-чанки
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_by_paragraphs_empty(chunker: Chunker) -> None:
    assert chunker.chunk_by_paragraphs("", max_tokens=15) == []


def test_by_paragraphs_single_short(chunker: Chunker) -> None:
    chunks = chunker.chunk_by_paragraphs("короткий текст", max_tokens=50)
    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].start_token == 0


def test_by_paragraphs_returns_chunk_objects(chunker: Chunker) -> None:
    chunks = chunker.chunk_by_paragraphs(_paragraphs_text(), max_tokens=15)
    assert all(isinstance(c, Chunk) for c in chunks)
