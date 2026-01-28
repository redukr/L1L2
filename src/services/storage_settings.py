"""Simple storage settings persisted under /settings."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .app_paths import get_settings_dir, get_files_dir


SETTINGS_FILE = "storage.json"


def _settings_path() -> Path:
    return get_settings_dir() / SETTINGS_FILE


def get_materials_root() -> Path:
    """Return the materials root directory."""
    path = _settings_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        root = data.get("materials_root")
        if root:
            return Path(root)
    return get_files_dir()


def set_materials_root(path: Path) -> None:
    """Persist the materials root directory."""
    data = {"materials_root": str(path)}
    _settings_path().write_text(json.dumps(data, indent=2), encoding="utf-8")

