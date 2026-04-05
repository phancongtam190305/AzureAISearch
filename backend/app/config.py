from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    search_endpoint: str
    index_name: str
    api_key: str | None
    use_rbac: bool
    tenant_id: str | None
    project_root: Path
    frontend_dir: Path


def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").strip()
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "demo-docs").strip()
    api_key = os.getenv("AZURE_SEARCH_API_KEY", "").strip() or None
    use_rbac = os.getenv("AZURE_USE_RBAC", "true").strip().lower() in {"1", "true", "yes"}
    tenant_id = os.getenv("AZURE_TENANT_ID", "").strip() or None

    return Settings(
        search_endpoint=endpoint,
        index_name=index_name,
        api_key=api_key,
        use_rbac=use_rbac,
        tenant_id=tenant_id,
        project_root=project_root,
        frontend_dir=project_root / "frontend",
    )

