from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import health
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware, register_exception_handlers
from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ConceptMRI API",
        description="AI-Powered Conceptual Learning Assessment Platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(health.router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(users_router, prefix=settings.api_v1_prefix)
    from app.api.routers.topics import router as topics_router
    from app.api.routers.rubrics import router as rubrics_router
    from app.api.routers.assessments import router as assessments_router
    from app.api.routers.evaluations import router as evaluations_router
    from app.api.routers.reports import router as reports_router
    from app.api.routers.dashboard import router as dashboard_router
    from app.api.routers.teacher import router as teacher_router
    app.include_router(topics_router, prefix=settings.api_v1_prefix)
    app.include_router(rubrics_router, prefix=settings.api_v1_prefix)
    app.include_router(assessments_router, prefix=settings.api_v1_prefix)
    app.include_router(evaluations_router, prefix=settings.api_v1_prefix)
    app.include_router(reports_router, prefix=settings.api_v1_prefix)
    app.include_router(dashboard_router, prefix=settings.api_v1_prefix)
    app.include_router(teacher_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
