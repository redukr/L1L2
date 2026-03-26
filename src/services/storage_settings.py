"""Simple storage settings persisted under /settings."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from .app_paths import get_settings_dir, get_files_dir, make_relative_to_app, resolve_app_path


SETTINGS_FILE = "storage.json"
logger = logging.getLogger(__name__)


def _settings_path() -> Path:
    return get_settings_dir() / SETTINGS_FILE


def get_materials_root() -> Path:
    """Return the materials root directory."""
    path = _settings_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return get_files_dir()
        root = data.get("materials_root")
        if root:
            try:
                resolved = resolve_app_path(root)
            except (OSError, RuntimeError, ValueError, TypeError):
                return get_files_dir()
            # Migrate stored absolute paths to relative when possible.
            try:
                rel = make_relative_to_app(resolved)
                if rel != root:
                    data["materials_root"] = rel
                    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (OSError, RuntimeError, ValueError, TypeError):
                logger.warning("Failed to normalize materials_root in storage settings.", exc_info=True)
            return resolved
    return get_files_dir()


def set_materials_root(path: Path) -> None:
    """Persist the materials root directory."""
    data = {"materials_root": make_relative_to_app(path)}
    _settings_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
