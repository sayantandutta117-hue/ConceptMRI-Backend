# ConceptMRI Backend

Production-ready FastAPI backend for the ConceptMRI AI-powered conceptual learning assessment platform.

## Milestone Status

| Milestone | Description | Status |
| --------- | ----------- | ------ |
| 0 | Project foundation | ✅ Complete |
| 1 | Database & domain models | ✅ Complete |
| 2 | Core infrastructure | ⏳ |
| 3 | Authentication & users | ⏳ |
| 4 | Topics & rubrics | ⏳ |
| 5 | Assessment & AI pipeline | ⏳ |
| 6 | Dashboard & analytics | ⏳ |

## Quick Start

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env   # edit values as needed

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

## Run Tests

```bash
pytest
```

## Documentation

- [Milestone 0 Decisions](docs/MILESTONE_0_DECISIONS.md)
- [API Alignment (Frontend contracts)](docs/API_ALIGNMENT.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [AI Engine Spec](docs/AI_ENGINE_SPEC.md)

## Milestone 1 — Database & Domain Models (Complete)

### Implemented
- Async database session and engine setup (`app/db/session.py`)
- SQLAlchemy 2.0 async models for all entities:
  - `User`, `Student`, `Teacher`, `Class`
  - `Topic`, `Rubric`, `Assessment`, `Evaluation`
  - `MRIReport`, `Recommendation`
  - `KnowledgeGraphNode`, `KnowledgeGraphEdge`
- Domain enums (`app/db/models/enums.py`)
- Repository layer with CRUD and specialized query methods
- Alembic async migration setup (`migrations/`)
- Seed data module (`app/db/seed.py`)
- Unit tests for models and repositories (`tests/unit/test_db_models.py`)

## Architecture

```text
Client → FastAPI Router → Service → Repository → PostgreSQL
                              ↓
                         OpenAI API (Milestone 5+)
```

Business logic lives in **services**. Routers stay thin. All API responses use the standardized envelope defined in `app/schemas/common.py`.

## Environment Variables

See [.env.example](.env.example).

## Spec Sources

Implementation follows `Backend-specs/` with Frontend-spec treated as the API integration contract. See `docs/API_ALIGNMENT.md` for the full endpoint map.
