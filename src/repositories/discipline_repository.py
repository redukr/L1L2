"""Discipline repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Discipline, Topic
from ..models.database import Database


class DisciplineRepository:
    """Repository for managing discipline data."""

    def __init__(self, database: Database):
        self.db = database

    def add(self, discipline: Discipline) -> Discipline:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO disciplines (name, description, order_index)
                VALUES (?, ?, ?)
            """, (discipline.name, discipline.description, discipline.order_index))
            discipline.id = cursor.lastrowid
            return discipline

    def update(self, discipline: Discipline) -> Discipline:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE disciplines
                SET name = ?, description = ?, order_index = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (discipline.name, discipline.description, discipline.order_index, discipline.id))
            return discipline

    def delete(self, discipline_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM disciplines WHERE id = ?", (discipline_id,))
            return cursor.rowcount > 0

    def get_by_id(self, discipline_id: int) -> Optional[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, order_index, created_at, updated_at
                FROM disciplines WHERE id = ?
            """, (discipline_id,))
            row = cursor.fetchone()
            return self._row_to_discipline(row) if row else None

    def get_all(self) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, order_index, created_at, updated_at
                FROM disciplines ORDER BY name
            """)
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, order_index, created_at, updated_at
                FROM disciplines
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            """, (f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def get_discipline_topics(self, discipline_id: int) -> List[Topic]:
        from .topic_repository import TopicRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.description, dt.order_index as order_index,
                       t.created_at, t.updated_at
                FROM topics t
                JOIN discipline_topics dt ON t.id = dt.topic_id
                WHERE dt.discipline_id = ?
                ORDER BY dt.order_index
            """, (discipline_id,))
            topic_repo = TopicRepository(self.db)
            return [topic_repo._row_to_topic(row) for row in cursor.fetchall()]

    def add_topic_to_discipline(self, discipline_id: int, topic_id: int, order_index: int = 0) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO discipline_topics (discipline_id, topic_id, order_index)
                    VALUES (?, ?, ?)
                """, (discipline_id, topic_id, order_index))
                return True
            except Exception:
                return False

    def remove_topic_from_discipline(self, discipline_id: int, topic_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM discipline_topics
                WHERE discipline_id = ? AND topic_id = ?
            """, (discipline_id, topic_id))
            return cursor.rowcount > 0

    def get_disciplines_for_topic(self, topic_id: int) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.name, d.description, d.order_index,
                       d.created_at, d.updated_at
                FROM disciplines d
                JOIN discipline_topics dt ON d.id = dt.discipline_id
                WHERE dt.topic_id = ?
                ORDER BY d.name
            """, (topic_id,))
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def get_disciplines_for_lesson(self, lesson_id: int) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT d.id, d.name, d.description, d.order_index,
                                d.created_at, d.updated_at
                FROM disciplines d
                JOIN discipline_topics dt ON d.id = dt.discipline_id
                JOIN topic_lessons tl ON dt.topic_id = tl.topic_id
                WHERE tl.lesson_id = ?
                ORDER BY d.name
            """, (lesson_id,))
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def get_disciplines_for_question(self, question_id: int) -> List[Discipline]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT d.id, d.name, d.description, d.order_index,
                                d.created_at, d.updated_at
                FROM disciplines d
                JOIN discipline_topics dt ON d.id = dt.discipline_id
                JOIN topic_lessons tl ON dt.topic_id = tl.topic_id
                JOIN lesson_questions lq ON tl.lesson_id = lq.lesson_id
                WHERE lq.question_id = ?
                ORDER BY d.name
            """, (question_id,))
            return [self._row_to_discipline(row) for row in cursor.fetchall()]

    def _row_to_discipline(self, row) -> Discipline:
        return Discipline(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            order_index=row["order_index"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
