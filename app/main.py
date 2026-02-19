from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.middleware.error_handler import register_error_handlers
from app.api.routes import connections, schema, query, mappings, glossary


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(connections.router, prefix="/connections", tags=["connections"])
    app.include_router(schema.router, prefix="/schema", tags=["schema"])
    app.include_router(query.router, prefix="/query", tags=["query"])
    app.include_router(mappings.router, prefix="/mappings", tags=["mappings"])
    app.include_router(glossary.router, prefix="/glossary", tags=["glossary"])

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok", "version": settings.app_version}

    return app


app = create_app()
