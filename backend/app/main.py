from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .search_service import SearchService


settings = get_settings()
search_service = SearchService(settings)

app = FastAPI(title="Azure AI Search Starter")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = settings.frontend_dir
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "endpoint_configured": "yes" if settings.search_endpoint else "no",
        "index_name": settings.index_name,
    }


@app.get("/api/search")
def search(
    q: str = Query("", description="Search text"),
    top: int = Query(5, ge=1, le=20),
    mode: str = Query("semantic", pattern="^(semantic|simple)$"),
) -> dict:
    if not settings.search_endpoint:
        raise HTTPException(status_code=400, detail="AZURE_SEARCH_ENDPOINT chua duoc cau hinh.")

    try:
        return search_service.search(q, top=top, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def index() -> FileResponse:
    index_file = Path(frontend_dir) / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend chua duoc tao.")
    return FileResponse(index_file)

