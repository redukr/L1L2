"""Lesson type repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import LessonType
from ..models.database import Database


class LessonTypeRepository:
    """Repository for managing lesson types."""

    def __init__(self, database: Database):
        self.db = database

    def add(self, lesson_type: LessonType) -> LessonType:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lesson_types (name)
                VALUES (?)
            """, (lesson_type.name,))
            lesson_type.id = cursor.lastrowid
            return lesson_type

    def update(self, lesson_type: LessonType) -> LessonType:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lesson_types
                SET name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (lesson_type.name, lesson_type.id))
            return lesson_type

    def delete(self, lesson_type_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lesson_types WHERE id = ?", (lesson_type_id,))
            return cursor.rowcount > 0

    def get_by_id(self, lesson_type_id: int) -> Optional[LessonType]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, created_at, updated_at
                FROM lesson_types
                WHERE id = ?
            """, (lesson_type_id,))
            row = cursor.fetchone()
            return self._row_to_lesson_type(row) if row else None

    def get_all(self) -> List[LessonType]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, created_at, updated_at
                FROM lesson_types
                ORDER BY name
            """)
            return [self._row_to_lesson_type(row) for row in cursor.fetchall()]

    def _row_to_lesson_type(self, row) -> LessonType:
        return LessonType(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
