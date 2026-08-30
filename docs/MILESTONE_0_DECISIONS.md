# Milestone 0 — Backend Foundation Decisions

> **Project:** ConceptMRI  
> **Scope:** Backend only (FastAPI)  
> **Status:** Complete — awaiting approval before Milestone 1

---

## 1. Resolved Architectural Decisions

| Decision | Choice | Rationale |
| -------- | ------ | --------- |
| Backend framework | **FastAPI** | Per `tech-stack.md` and all backend specs |
| Python version | **3.12+** | Per tech stack |
| ORM | **SQLAlchemy 2.0 (async)** | Scalable, type-safe, matches specs |
| Migrations | **Alembic** | Required by project rules |
| Authentication (MVP) | **Full JWT + bcrypt** | `project-rules.md` takes precedence over API contract's "demo login" note |
| Token lifetime (MVP) | **24 hours** | Per backend auth spec |
| Refresh tokens | **Not in MVP** | Explicit non-goal |
| AI evaluation (MVP) | **Synchronous** | No Celery/Redis per architecture non-goals |
| Dashboard IDs in URL | **Support both patterns** | `/dashboard/student/{id}` (api-contracts) + infer from JWT when path omits ID (frontend-spec convenience) |
| Assessment status enum | **`PENDING_EVALUATION → PROCESSING → COMPLETED → REPORT_AVAILABLE \| FAILED`** | Aligns with `api-contracts.md` state machine |
| Primary keys | **UUID** | Per project rules |
| API prefix | **`/api/v1`** | Per api-contracts |
| Response envelope | **`{ success, message?, data?, error?, timestamp }`** | Per api-contracts Part 1 |
| Package manager | **pip + requirements.txt** | Per tech-stack (over backend-spec uv/Poetry mention) |
| Frontend integration | **CORS enabled** for `localhost:3000` | Next.js default dev port |

---

## 2. Missing Spec Stubs

The following referenced documents were **not present** in the repository. Stubs were created for Milestone 1+ implementation:

| Document | Stub Location |
| -------- | ------------- |
| `05_DATABASE_DESIGN.md` | `backend/docs/DATABASE_DESIGN.md` |
| `07_AI_ENGINE_SPEC.md` | `backend/docs/AI_ENGINE_SPEC.md` |
| Frontend API gaps | `backend/docs/API_ALIGNMENT.md` |

---

## 3. Folder Structure (Implemented)

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies/
│   │   └── routers/
│   ├── core/
│   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── migrations/          # Alembic in Milestone 1
│   ├── services/
│   ├── ai/
│   ├── schemas/
│   └── utils/
├── tests/
├── docs/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Milestone 0 Deliverables Checklist

- [x] Backend folder structure scaffolded
- [x] `requirements.txt` with approved dependencies only
- [x] `.env.example` with all required environment variables
- [x] Pydantic settings (`app/core/config.py`)
- [x] Standard API response schemas (`app/schemas/common.py`)
- [x] Centralized exception handling (`app/core/exceptions.py`)
- [x] Structured logging setup (`app/core/logging.py`)
- [x] CORS middleware configured
- [x] Health check endpoint (`GET /api/v1/health`)
- [x] FastAPI OpenAPI docs at `/docs` and `/redoc`
- [x] Database design stub for Milestone 1
- [x] AI engine spec stub for Milestone 5
- [x] API alignment document (frontend contracts → backend endpoints)
- [x] Basic test for health endpoint

---

## 5. Out of Scope (Milestone 0)

- Database models and migrations (Milestone 1)
- Authentication endpoints (Milestone 3)
- Business domain APIs (Milestones 4–6)
- Any frontend code, folders, or configuration

---

## 6. Approval Gate

Proceed to **Milestone 2 — Core Infrastructure** only after user approval.

---

## 7. Milestone 1 Deliverables Checklist

- [x] Database session and async engine setup
- [x] All domain models with enums
- [x] Repository layer with CRUD and query methods
- [x] Alembic async migration setup with initial revision
- [x] Seed data module for demo users
- [x] Unit tests for models and repositories
- [x] All tests passing
