# RAG Chat — корпоративный ассистент по документам

Сквозной учебно-боевой проект: RAG-чат на FastAPI. Загрузил документы →
задал вопрос → получил ответ по ним со стримингом и цитатами.

Проект растёт по этапам из `unified_roadmap.md` (в корне). Каждый этап —
работающий инкремент.

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
  models/            # SQLAlchemy-модели (наполняются на этапе 3)
  schemas/           # Pydantic-схемы (вход/выход раздельно)
  crud/              # доступ к данным (этап 3+)
  services/          # бизнес-логика: LLM-клиент, RAG-пайплайн
  api/routers/       # эндпоинты по доменам
tests/
```
