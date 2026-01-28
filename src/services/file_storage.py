"""File storage manager for methodical materials."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Optional, Tuple

from .app_paths import get_app_base_dir, get_files_dir


MAX_PATH_WINDOWS = 260


class FileStorageManager:
    """Controls file storage lifecycle under data/files."""

    def __init__(self, files_root: Optional[Path] = None):
        self._files_root = files_root or get_files_dir()
        self._files_root.mkdir(parents=True, exist_ok=True)

    @property
    def files_root(self) -> Path:
        return self._files_root

    def build_material_path(
        self, program_id: int, discipline_id: int, material_id: int, ext: str
    ) -> Tuple[Path, str]:
        """Return (absolute_path, relative_path) for a material file."""
        program_folder = f"p{program_id:02d}"
        discipline_folder = f"d{discipline_id:02d}"
        stored_filename = f"m_{material_id:06d}{ext}"
        relative_path = Path("files") / program_folder / discipline_folder / stored_filename
        absolute_path = get_app_base_dir() / relative_path
        self._ensure_under_max_path(absolute_path)
        return absolute_path, str(relative_path).replace("\\", "/")

    def store_material_file(
        self,
        source_path: str,
        program_id: int,
        discipline_id: int,
        material_id: int,
    ) -> Tuple[str, str, str, str]:
        """
        Copy file into storage and return:
        (original_filename, stored_filename, relative_path, file_type)
        """
        source = Path(source_path)
        if not source.exists():
            raise ValueError("Source file does not exist.")
        ext = source.suffix.lower()
        absolute_path, relative_path = self.build_material_path(program_id, discipline_id, material_id, ext)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, absolute_path)
        return source.name, absolute_path.name, relative_path, ext.lstrip(".")

    def open_file(self, relative_path: str) -> bool:
        """Open file with default OS application."""
        absolute = get_app_base_dir() / relative_path
        if not absolute.exists():
            return False
        os.startfile(str(absolute))
        return True

    def show_in_folder(self, relative_path: str) -> bool:
        """Show file folder in Explorer."""
        absolute = get_app_base_dir() / relative_path
        if not absolute.exists():
            return False
        os.startfile(str(absolute.parent))
        return True

    def copy_file_as(self, relative_path: str, dest_path: str) -> bool:
        """Copy file to a user-selected destination."""
        absolute = get_app_base_dir() / relative_path
        if not absolute.exists():
            return False
        shutil.copyfile(absolute, dest_path)
        return True

    def delete_file(self, relative_path: Optional[str]) -> None:
        """Delete a stored file if it exists."""
        if not relative_path:
            return
        absolute = get_app_base_dir() / relative_path
        if absolute.exists():
            absolute.unlink()

    def migrate_legacy_material(
        self,
        cursor,
        material_id: int,
        file_path: Optional[str],
        file_name: Optional[str],
        program_id: int,
        discipline_id: int,
    ) -> None:
        """Move legacy files into the new storage layout."""
        if not file_path:
            return
        source = Path(file_path)
        if not source.exists():
            return
        ext = source.suffix.lower()
        absolute_path, relative_path = self.build_material_path(program_id, discipline_id, material_id, ext)
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, absolute_path)
        cursor.execute("""
            UPDATE methodical_materials
            SET original_filename = ?, stored_filename = ?, relative_path = ?, file_type = ?,
                file_path = ?, file_name = ?
            WHERE id = ?
        """, (
            file_name or source.name,
            absolute_path.name,
            relative_path,
            ext.lstrip("."),
            relative_path,
            file_name or source.name,
            material_id,
        ))

    def migrate_legacy_materials(self, database) -> None:
        """Migrate existing stored files into the new layout."""
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, file_path, file_name, relative_path
                FROM methodical_materials
                WHERE relative_path IS NULL AND file_path IS NOT NULL
            """)
            rows = cursor.fetchall()
            for row in rows:
                program_id, discipline_id = self._resolve_program_discipline(cursor, row["id"])
                if program_id is None or discipline_id is None:
                    continue
                self.migrate_legacy_material(
                    cursor,
                    row["id"],
                    row["file_path"],
                    row["file_name"],
                    program_id,
                    discipline_id,
                )

    def _resolve_program_discipline(self, cursor, material_id: int) -> Tuple[Optional[int], Optional[int]]:
        cursor.execute("""
            SELECT entity_type, entity_id
            FROM material_associations
            WHERE material_id = ?
        """, (material_id,))
        associations = cursor.fetchall()
        if not associations:
            return None, None
        for association in associations:
            if association["entity_type"] == "discipline":
                cursor.execute("""
                    SELECT program_id FROM program_disciplines
                    WHERE discipline_id = ?
                    ORDER BY program_id
                    LIMIT 1
                """, (association["entity_id"],))
                row = cursor.fetchone()
                if row:
                    return row["program_id"], association["entity_id"]
        for association in associations:
            if association["entity_type"] == "lesson":
                cursor.execute("""
                    SELECT dt.discipline_id, pd.program_id
                    FROM topic_lessons tl
                    JOIN discipline_topics dt ON tl.topic_id = dt.topic_id
                    JOIN program_disciplines pd ON dt.discipline_id = pd.discipline_id
                    WHERE tl.lesson_id = ?
                    LIMIT 1
                """, (association["entity_id"],))
                row = cursor.fetchone()
                if row:
                    return row["program_id"], row["discipline_id"]
            if association["entity_type"] == "topic":
                cursor.execute("""
                    SELECT dt.discipline_id, pd.program_id
                    FROM discipline_topics dt
                    JOIN program_disciplines pd ON dt.discipline_id = pd.discipline_id
                    WHERE dt.topic_id = ?
                    LIMIT 1
                """, (association["entity_id"],))
                row = cursor.fetchone()
                if row:
                    return row["program_id"], row["discipline_id"]
            if association["entity_type"] == "program":
                cursor.execute("""
                    SELECT discipline_id
                    FROM program_disciplines
                    WHERE program_id = ?
                    ORDER BY order_index
                    LIMIT 1
                """, (association["entity_id"],))
                row = cursor.fetchone()
                if row:
                    return association["entity_id"], row["discipline_id"]
        return None, None

    def _ensure_under_max_path(self, path: Path) -> None:
        if len(str(path)) >= MAX_PATH_WINDOWS:
            raise ValueError("File path exceeds Windows MAX_PATH limit.")
