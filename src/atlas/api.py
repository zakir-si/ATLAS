"""Local FastAPI service. Do not expose publicly without authentication."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from atlas import __version__
from atlas.controller import select_best_run
from atlas.schemas import SelectedRunOutput, SelectionRequest, SelectionResponse

logging.basicConfig(level=os.getenv("ATLAS_LOG_LEVEL", "INFO"))
logger = logging.getLogger("atlas.api")

_STATIC_DIR = Path(__file__).parent / "static"
app = FastAPI(
    title="ATLAS API",
    version=__version__,
    description="Local quality-constrained selection over measured training runs.",
    docs_url="/docs",
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve the local demo UI."""
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "alive", "version": __version__}


@app.get("/health/ready", tags=["health"])
def ready() -> dict[str, str]:
    """Readiness probe; this service has no external dependencies."""
    return {"status": "ready"}


@app.post("/api/v1/select", response_model=SelectionResponse, tags=["optimization"])
def select(request: SelectionRequest) -> SelectionResponse:
    """Choose among caller-supplied measurements; does not launch training."""
    try:
        selection = select_best_run(
            [item.to_run_result() for item in request.results],
            min_quality=request.min_quality,
            max_accelerator_hours=request.max_accelerator_hours,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    run = selection.run
    logger.info(
        "selection_complete selected=%s eligible=%d considered=%d",
        run.name,
        selection.eligible_run_count,
        selection.considered_run_count,
    )
    return SelectionResponse(
        selected=SelectedRunOutput(
            name=run.name,
            quality=run.quality,
            accelerator_hours=run.accelerator_hours,
            peak_memory_gb=run.peak_memory_gb,
            tokens_per_second=run.tokens_per_second,
        ),
        quality_margin=selection.quality_margin,
        quality_per_accelerator_hour=selection.quality_per_accelerator_hour,
        eligible_run_count=selection.eligible_run_count,
        considered_run_count=selection.considered_run_count,
    )
