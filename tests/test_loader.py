"""Тесты на загрузку доков"""
import pytest
import pathlib

from reportlab.pdfgen import canvas
from app.services import loader
from app.services.chunker import Chunker
from app.services.indexing import chunk_documents


def make_pdf(path, pages: list[str]):
    c = canvas.Canvas(str(path))
    for text in pages:
        c.drawString(100, 700, text)
        c.showPage()          # завершить страницу — КЛЮЧЕВОЕ: одна showPage = одна страница
    c.save()


def test_load_txt_cleans_text(tmp_path: pathlib.Path):
    f = tmp_path / "doc.txt"
    f.write_text("Первый   абзац.\n\n\n\nВторой абзац.", encoding="utf-8")
    docs = loader.load(str(f))
    assert len(docs) == 1
    assert docs[0].metadata["source"] == "doc.txt"
    assert docs[0].text == "Первый абзац.\n\nВторой абзац."


def test_load_pdf_keeps_page_numbers(tmp_path: pathlib.Path):
    pdf = tmp_path / "doc.pdf"
    make_pdf(pdf, ["This is page one.", "This is page two."])
    docs = loader.load(str(pdf))
    assert len(docs) == 2
    assert docs[0].metadata["page"] == 1
    assert docs[1].metadata["page"] == 2
    assert "page one" in docs[0].text
    assert "page two" in docs[1].text


def test_load_unknown_format_raises():
    with pytest.raises(ValueError):
        loader.load("file.docx")


def test_chunk_documents_propagates_metadata(tmp_path):
    pdf = tmp_path / "doc.pdf"
    make_pdf(pdf, ["First page text here.", "Second page text here."])
    docs = loader.load(str(pdf))
    chunks = chunk_documents(docs, Chunker(), max_tokens=50)
    assert all("source" in c.metadata and "page" in c.metadata for c in chunks)
    pages = {c.metadata["page"] for c in chunks}
    assert pages == {1, 2}