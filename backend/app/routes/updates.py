from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/updates", tags=["updates"])

UPDATES_DIR = Path(os.environ.get("UPDATES_DIR", "/opt/equiptracker/updates"))
VERSION_FILE = UPDATES_DIR / "latest.json"


def _get_manifest() -> dict | None:
    if VERSION_FILE.exists():
        return json.loads(VERSION_FILE.read_text())
    return None


def _platform_file(platform: str) -> Path | None:
    manifest = _get_manifest()
    if not manifest:
        return None
    filename = manifest.get("platforms", {}).get(platform)
    if not filename:
        return None
    filepath = UPDATES_DIR / filename
    return filepath if filepath.exists() else None


@router.get("/latest.json")
def latest_manifest():
    manifest = _get_manifest()
    if manifest is None:
        raise HTTPException(status_code=404, detail="no updates available")
    return JSONResponse(content=manifest)


@router.get("/{platform:str}")
def download_update(platform: str):
    allowed = {"linux", "windows", "macos"}
    if platform not in allowed:
        raise HTTPException(status_code=400, detail="platform must be linux, windows, or macos")

    filepath = _platform_file(platform)
    if filepath is None:
        raise HTTPException(status_code=404, detail="no update for this platform")

    return FileResponse(
        path=str(filepath),
        filename=filepath.name,
        media_type="application/octet-stream",
    )
