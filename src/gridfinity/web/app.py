"""FastAPI web app for the Gridfinity assistant."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..models import GridSpec
from ..service import plan

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Gridfinity Assistant",
    description="Upload a photo, set your grid, get printable bin recommendations.",
    version="1.0.0",
)


@app.get("/api/health")
def health() -> dict:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    return {
        "status": "ok",
        "vision_enabled": bool(key) and not key.startswith("your_"),
    }


@app.post("/api/plan")
async def create_plan(
    width_units: int = Form(...),
    depth_units: int = Form(...),
    research: bool = Form(True),
    image: Optional[UploadFile] = File(None),
) -> JSONResponse:
    """Analyze an uploaded photo and return bin recommendations + layout."""
    if width_units < 1 or depth_units < 1:
        return JSONResponse(
            status_code=400,
            content={"error": "Grid dimensions must be at least 1 x 1."},
        )

    image_bytes = None
    media_type = "image/jpeg"
    if image is not None:
        image_bytes = await image.read()
        media_type = image.content_type or "image/jpeg"
        if not image_bytes:
            image_bytes = None

    grid = GridSpec(width_units=width_units, depth_units=depth_units)
    result = plan(
        grid=grid,
        image_bytes=image_bytes,
        media_type=media_type,
        do_research=research,
    )
    return JSONResponse(content=result.model_dump())


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def main() -> None:
    """Entry point: ``python -m src.gridfinity.web.app`` or ``gridfinity-web``."""
    import uvicorn

    host = os.getenv("GRIDFINITY_HOST", "127.0.0.1")
    port = int(os.getenv("GRIDFINITY_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
