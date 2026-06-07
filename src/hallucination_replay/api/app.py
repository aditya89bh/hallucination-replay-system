"""FastAPI application factory for the debugging platform."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Final

from fastapi import FastAPI

PACKAGE_NAME: Final = "hallucination-replay-system"


def create_app() -> FastAPI:
    """Create the Hallucination Replay API application."""
    app = FastAPI(
        title="Hallucination Replay System",
        version=_package_version(),
        description="Interactive debugging APIs for replaying and analyzing traces.",
    )

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
        return "0.1.0"


app = create_app()
