"""Lesson repository for database operations."""
from typing import List, Optional
from datetime import datetime
from ..models.entities import Lesson, Question
from ..models.database import Database


class LessonRepository:
    """Repository for managing lesson data."""

    def __init__(self, database: Database):
        """
        Initialize lesson repository.

        Args:
            database: Database instance
        """
        self.db = database

    def add(self, lesson: Lesson) -> Lesson:
        """
        Add a new lesson to the database.

        Args:
            lesson: Lesson entity to add

        Returns:
            Lesson: Added lesson with assigned ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lessons (title, description, duration_hours, order_index)
                VALUES (?, ?, ?, ?)
            """, (
                lesson.title,
                lesson.description,
                lesson.duration_hours,
                lesson.order_index
            ))
            lesson.id = cursor.lastrowid
            return lesson

    def update(self, lesson: Lesson) -> Lesson:
        """
        Update an existing lesson.

        Args:
            lesson: Lesson entity with updated data

        Returns:
            Lesson: Updated lesson entity
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lessons
                SET title = ?, description = ?, duration_hours = ?, 
                    order_index = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                lesson.title,
                lesson.description,
                lesson.duration_hours,
                lesson.order_index,
                lesson.id
            ))
            return lesson

    def delete(self, lesson_id: int) -> bool:
        """
        Delete a lesson by ID.

        Args:
            lesson_id: ID of lesson to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
            return cursor.rowcount > 0

    def get_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """
        Get a lesson by ID.

        Args:
            lesson_id: ID of lesson to retrieve

        Returns:
            Lesson or None: Lesson entity if found
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, duration_hours, order_index, 
                       created_at, updated_at
                FROM lessons WHERE id = ?
            """, (lesson_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_lesson(row)
            return None

    def get_all(self) -> List[Lesson]:
        """
        Get all lessons.

        Returns:
            List[Lesson]: List of all lessons
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, duration_hours, order_index, 
                       created_at, updated_at
                FROM lessons ORDER BY title
            """)
            return [self._row_to_lesson(row) for row in cursor.fetchall()]

    def search(self, keyword: str) -> List[Lesson]:
        """
        Search lessons by keyword.

        Args:
            keyword: Search keyword

        Returns:
            List[Lesson]: List of matching lessons
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, duration_hours, order_index, 
                       created_at, updated_at
                FROM lessons
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY title
            """, (f"%{keyword}%", f"%{keyword}%"))
            return [self._row_to_lesson(row) for row in cursor.fetchall()]

    def add_question_to_lesson(self, lesson_id: int, question_id: int, order_index: int = 0) -> bool:
        """
        Add a question to a lesson.

        Args:
            lesson_id: ID of the lesson
            question_id: ID of the question
            order_index: Order index for the question in the lesson

        Returns:
            bool: True if added successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO lesson_questions (lesson_id, question_id, order_index)
                    VALUES (?, ?, ?)
                """, (lesson_id, question_id, order_index))
                return True
            except Exception:
                return False

    def remove_question_from_lesson(self, lesson_id: int, question_id: int) -> bool:
        """
        Remove a question from a lesson.

        Args:
            lesson_id: ID of the lesson
            question_id: ID of the question

        Returns:
            bool: True if removed successfully
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM lesson_questions 
                WHERE lesson_id = ? AND question_id = ?
            """, (lesson_id, question_id))
            return cursor.rowcount > 0

    def get_lesson_questions(self, lesson_id: int) -> List[Question]:
        """
        Get all questions for a specific lesson.

        Args:
            lesson_id: ID of the lesson

        Returns:
            List[Question]: List of questions in the lesson
        """
        from .question_repository import QuestionRepository

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.id, q.content, q.answer, q.difficulty_level, 
                       q.order_index, q.created_at, q.updated_at
                FROM questions q
                JOIN lesson_questions lq ON q.id = lq.question_id
                WHERE lq.lesson_id = ?
                ORDER BY lq.order_index
            """, (lesson_id,))

            question_repo = QuestionRepository(self.db)
            return [question_repo._row_to_question(row) for row in cursor.fetchall()]

    def _row_to_lesson(self, row) -> Lesson:
        """
        Convert database row to Lesson entity.

        Args:
            row: Database row

        Returns:
            Lesson: Lesson entity
        """
        return Lesson(
            id=row['id'],
            title=row['title'],
            description=row['description'],
            duration_hours=row['duration_hours'],
            order_index=row['order_index'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
