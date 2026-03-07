"""User activity logging for admin/editor actions."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .app_paths import get_settings_dir


class ActivityLogService:
    """Append-only JSONL activity log."""

    def __init__(self) -> None:
        self._path = get_settings_dir() / "activity_log.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("", encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    def log(self, user_name: str, mode: str, action: str, details: str = "") -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user_name or "unknown",
            "mode": mode or "unknown",
            "action": action or "",
            "details": details or "",
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict]:
        rows: list[dict] = []
        if not self._path.exists():
            return rows
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
        return rows

    def clear(self) -> None:
        self._path.write_text("", encoding="utf-8")

