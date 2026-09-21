"""Загрузчик документов разных типов для задания 2.2"""
import re
from dataclasses import dataclass
from pypdf import PdfReader
from pathlib import Path


@dataclass
class Document:
    text: str
    metadata: dict   # {"source": "faq.pdf", "page": 3, ...}


def load(path: str) -> list[Document]:
    """
    Загрузка документов типов md, txt, pdf
    Args:
        path: путь до документа
    """
    ext = Path(path).suffix.lower()
    if ext in {".txt", ".md"}:
        return _load_text(path)
    if ext == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Неподдерживаемый формат: {ext}")

def _load_text(path: str) -> list[Document]:
    """
        Загрузка документов типов txt
        Args:
            path: путь до документа
    """
    text = Path(path).read_text(encoding="utf-8")
    return [Document(text=_clean(text), metadata={"source": Path(path).name})]


def _load_pdf(path: str) -> list[Document]:
    """
        Загрузка документов типов pdf
        Args:
            path: путь до документа
    """
    reader = PdfReader(path)
    docs = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""       # бывает None на пустой странице
        docs.append(Document(text=_clean(text),
                             metadata={"source": Path(path).name, "page": page_num}))
    return docs


def _clean(text: str) -> str:
    """
        Очищаем текст от пробелов вокруг, замена табов и последовательности пробелов на один пробел
        Args:
            text: текст
    """
    # убрать пробелы
    cleaned_text = "\n".join(line.strip() for line in text.split("\n"))
    # заменить последовательности пробелов/табов на один пробел
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    # схлопнуть 3+ переносов в двойной чтобы разделители абзацев остались, а "дыры" ушли
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text