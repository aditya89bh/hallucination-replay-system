"""FastAPI application factory for the debugging platform."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Final

from fastapi import FastAPI

from hallucination_replay import __version__
from hallucination_replay.api.analysis import router as analysis_router
from hallucination_replay.api.comparison import router as comparison_router
from hallucination_replay.api.docs import API_DESCRIPTION, OPENAPI_TAGS
from hallucination_replay.api.hallucination import router as hallucination_router
from hallucination_replay.api.reconstruction import router as reconstruction_router
from hallucination_replay.api.replay import router as replay_router
from hallucination_replay.api.traces import (
    default_trace_repository,
)
from hallucination_replay.api.traces import (
    router as traces_router,
)
from hallucination_replay.storage import TraceRepository

PACKAGE_NAME: Final = "hallucination-replay-system"


def create_app(repository: TraceRepository | None = None) -> FastAPI:
    """Create the Hallucination Replay API application."""
    app = FastAPI(
        title="Hallucination Replay System",
        version=_package_version(),
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
    )
    app.state.trace_repository = repository or default_trace_repository()
    app.include_router(traces_router)
    app.include_router(replay_router)
    app.include_router(reconstruction_router)
    app.include_router(analysis_router)
    app.include_router(hallucination_router)
    app.include_router(comparison_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        """Return API health status."""
        return {"status": "ok"}

    @app.get("/version", tags=["system"])
    def api_version() -> dict[str, str]:
        """Return package and API version information."""
        return {"name": PACKAGE_NAME, "version": _package_version()}

    return app


def _package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return __version__


app = create_app()
