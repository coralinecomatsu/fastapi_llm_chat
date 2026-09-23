# RAG Chat — корпоративный ассистент по документам

Сквозной учебно-боевой проект: RAG-чат на FastAPI. Загрузил документы →
задал вопрос → получил ответ по ним со стримингом и цитатами.

## Что уже умеет проект

**HTTP API (FastAPI, доступно через `/docs`):**

- `GET /health` — проверка живости; `GET /echo/{text}` — дымовой эндпоинт.
- `POST /users` — создать пользователя (валидация email и возраста).
- `POST /chats` — создать диалог; `GET /chats/{id}/messages` — история
  сообщений с пагинацией; `POST /chats/{id}/messages` — отправить сообщение:
  реплика сохраняется в БД, вся история диалога подгружается и передаётся в
  LLM (многоходовой контекст), ответ модели тоже сохраняется.
- `POST /chat` и `POST /chat/stream` — одиночный вызов LLM (без истории),
  обычный и потоковый.
- Данные (пользователи, чаты, сообщения) хранятся в БД через async
  SQLAlchemy 2.x; LLM-клиент ходит в OpenAI-совместимый API (локальный Ollama).

**RAG-ядро (модули в `app/services/`, покрыты тестами; к API пока не
подключены — это следующий этап):**

- **Загрузка документов** — `.txt` / `.md` / `.pdf` → чистый текст с
  метаданными (`source`, номер страницы для цитирования).
- **Чанкинг** — нарезка по токенам с перекрытием и по абзацам; метаданные
  документа доезжают до каждого чанка.
- **Эмбеддинги** — sentence-transformers (мультиязычная e5), нормализация.
- **Поиск** — векторный (cosine через numpy), лексический (BM25), их
  **гибрид через RRF**, и **rerank** cross-encoder'ом (схема
  retrieve → rerank).

Всё RAG-ядро написано вручную, без LangChain.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # при необходимости поправь значения
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

Тесты и типы:

```bash
pytest
mypy app
```

## Структура (слои — см. [F] Модуль 6)

```
app/
  main.py            # тонкая точка входа: создаёт app, подключает роутеры
  core/config.py     # настройки через pydantic-settings
  db/session.py      # async-движок + get_db (DI-зависимость)
  models/            # SQLAlchemy-модели: User, Chat, Message, Document
  schemas/           # Pydantic-схемы (вход/выход раздельно)
  crud/              # доступ к данным (chat, message, user)
  services/          # бизнес-логика:
                     #   llm_client        — клиент к LLM
                     #   loader, indexing  — загрузка документов и чанкинг
                     #   chunker           — нарезка текста
                     #   embedder          — эмбеддинги
                     #   vector_store, bm25_store — поиск (dense / lexical)
                     #   hybrid_retriever  — гибрид с RRF
                     #   reranker          — cross-encoder rerank
  api/routers/       # эндпоинты: health, users, chat, chats
tests/               # test_chunker, test_loader, test_health
```
